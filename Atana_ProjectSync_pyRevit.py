# -*- coding: utf-8 -*-
"""
Atana Tools — Project Sync (PyRevit)
====================================
Schema: atana-revit-sync/2.0

WHAT IT DOES
  1. Loads the project DB JSON (local file OR download from ACC)
  2. Sets Project Information (built-in + ATA_ZZ_* shared parameters)
  3. Sets / creates Global Parameters (GLOBAL_ZZ_*)
  4. Derives task team from the model file name (ISO role segment)
  5. Bulk-updates title block Designed By (TTM) / Checked By (Peer)
  6. Builds a Publish Set for the current work stage (matched DR/SH sheets)
  7. Writes a sheet-inventory JSON for the Atana IM app

INSTALL (once)
--------------
1. Install pyRevit
2. Create folder:
   %APPDATA%\\pyRevit\\Extensions\\AtanaTools.extension\\AtanaTools.tab\\ProjectSync.panel\\ProjectSync.pushbutton\\
3. Copy this file as script.py into that folder
4. Copy ATA_ZZ_SharedParameters.txt next to script.py
5. pyRevit → Reload
6. Revit: AtanaTools → Project Sync

APS / ACC LOGIN (optional — for downloading JSON from ACC)
----------------------------------------------------------
Register callback URL on your APS app (exact):

    http://127.0.0.1:8765/callback

Scopes (same as the web app where possible):
    data:read data:write data:create account:read code:all

First run: script asks for Client ID + Client Secret (stored in
%APPDATA%\\AtanaTools\\aps_config.json — not committed to git).

You can also skip ACC and pick a local DB JSON exported from the web app.

Pylance warnings about __revit__ / BuiltinParameterGroup are normal —
those symbols only exist inside Revit + pyRevit.
"""

from __future__ import print_function

import os
import re
import json
import time
import traceback
import threading

# ---------------------------------------------------------------------------
# .NET / Revit imports (guarded — prevents blank window on import failure)
# ---------------------------------------------------------------------------
IMPORT_ERROR = None
try:
    import clr
    clr.AddReference("RevitAPI")
    clr.AddReference("RevitAPIUI")
    clr.AddReference("System")
    clr.AddReference("System.Windows.Forms")

    from Autodesk.Revit.DB import (
        FilteredElementCollector, BuiltInCategory, BuiltInParameter,
        Transaction, StorageType, GlobalParameter,
        IntegerParameterValue, StringParameterValue,
        ViewSheet, ViewSet
    )
    from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult
    from System.Windows.Forms import (
        OpenFileDialog, DialogResult, FolderBrowserDialog, Form,
        Label, TextBox, Button, DockStyle, FormStartPosition, DialogResult as DR, FormBorderStyle
    )
    from System.IO import File, Directory
    from System import Uri
    from System.Diagnostics import Process, ProcessStartInfo
except Exception as _ex:
    IMPORT_ERROR = traceback.format_exc()


# ---------------------------------------------------------------------------
# Config paths
# ---------------------------------------------------------------------------
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AtanaTools")
CONFIG_PATH = os.path.join(CONFIG_DIR, "sync_path.txt")
APS_CFG_PATH = os.path.join(CONFIG_DIR, "aps_config.json")
APS_TOKEN_PATH = os.path.join(CONFIG_DIR, "aps_token.json")

# ---------------------------------------------------------------------------
# COMPANY APS APP (embedded so end users do not type these)
# Replace the two strings below with your APS Client ID + Secret once.
# Callback URL that MUST be registered on the same APS app:
#   http://127.0.0.1:8765/callback
# ---------------------------------------------------------------------------
APS_CLIENT_ID = ""      # e.g. "AbCdEf..."
APS_CLIENT_SECRET = ""  # e.g. "xxx..."

# Localhost callback — ADD THIS EXACT URL in APS → your app → Callback URL
# Port 8765 is often freer than 54777; change APS_CALLBACK_PORT if needed.
# If HttpListener still fails, run (Admin CMD):
#   netsh http add urlacl url=http://127.0.0.1:8765/ user=%USERNAME%
APS_CALLBACK_PORT = 8765
APS_CALLBACK_URL = "http://127.0.0.1:%d/callback" % APS_CALLBACK_PORT
APS_AUTH = "https://developer.api.autodesk.com/authentication/v2"
APS_DM = "https://developer.api.autodesk.com/data/v1"
APS_SCOPES = "data:read data:write data:create account:read code:all"
APS_LOGIN_TIMEOUT_SEC = 180  # stop hanging forever if browser never returns

SHARED_PARAM_FILE = os.path.join(os.path.dirname(__file__), "ATA_ZZ_SharedParameters.txt")

SHARED_GUIDS = {
    "ATA_ZZ_ClientContractNumber": "28b55e4c-650c-4af5-aae2-5ae0a0cda589",
    "ATA_ZZ_ProjectDiscipline": "60119a77-63b3-451e-969d-768d3b01fce0",
    "ATA_ZZ_ProjectStage": "b00f059e-1c43-446a-ad66-b7826e488c8f",
}

TITLEBLOCK_DESIGNED = ["Designed By", "Designed by", "DESIGNED BY", "Drawn By", "Author"]
TITLEBLOCK_CHECKED = ["Checked By", "Checked by", "CHECKED BY", "Approved By", "Approved by"]


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------
def info(msg, title="Atana Project Sync"):
    try:
        TaskDialog.Show(title, str(msg)[:3500])
    except Exception:
        print(title, msg)

def confirm(msg, title="Atana Project Sync"):
    try:
        r = TaskDialog.Show(title, str(msg)[:3500],
                            TaskDialogCommonButtons.Yes | TaskDialogCommonButtons.No)
        return r == TaskDialogResult.Yes
    except Exception:
        return False

def ensure_config_dir():
    if not Directory.Exists(CONFIG_DIR):
        Directory.CreateDirectory(CONFIG_DIR)


# ---------------------------------------------------------------------------
# APS config (Client ID / Secret)
# ---------------------------------------------------------------------------
def load_aps_cfg():
    """Prefer embedded company credentials; optional local override file."""
    cfg = {
        "clientId": (APS_CLIENT_ID or "").strip(),
        "clientSecret": (APS_CLIENT_SECRET or "").strip(),
        "callbackUrl": APS_CALLBACK_URL,
    }
    ensure_config_dir()
    if File.Exists(APS_CFG_PATH):
        try:
            disk = json.loads(File.ReadAllText(APS_CFG_PATH))
            # Disk only fills blanks (embedded wins when set)
            if not cfg["clientId"]:
                cfg["clientId"] = (disk.get("clientId") or "").strip()
            if not cfg["clientSecret"]:
                cfg["clientSecret"] = (disk.get("clientSecret") or "").strip()
        except Exception:
            pass
    return cfg

def save_aps_cfg(cfg):
    ensure_config_dir()
    File.WriteAllText(APS_CFG_PATH, json.dumps(cfg, indent=2))

def prompt_aps_credentials():
    """Simple WinForms dialog for Client ID + Secret."""
    form = Form()
    form.Text = "Atana — Autodesk APS credentials"
    form.Width = 520
    form.Height = 260
    form.StartPosition = FormStartPosition.CenterScreen

    lbl = Label()
    lbl.Text = ("Enter APS app Client ID and Client Secret.\n"
                "Callback URL (add in APS portal):\n" + APS_CALLBACK_URL)
    lbl.Top = 10
    lbl.Left = 12
    lbl.Width = 480
    lbl.Height = 55

    l1 = Label(); l1.Text = "Client ID"; l1.Top = 70; l1.Left = 12; l1.Width = 100
    t1 = TextBox(); t1.Top = 68; t1.Left = 120; t1.Width = 360
    l2 = Label(); l2.Text = "Client Secret"; l2.Top = 105; l2.Left = 12; l2.Width = 100
    t2 = TextBox(); t2.Top = 103; t2.Left = 120; t2.Width = 360
    t2.UseSystemPasswordChar = True

    cfg = load_aps_cfg()
    t1.Text = cfg.get("clientId") or ""
    t2.Text = cfg.get("clientSecret") or ""

    ok = Button(); ok.Text = "Save"; ok.Top = 160; ok.Left = 280; ok.Width = 90
    ok.DialogResult = DR.OK
    cancel = Button(); cancel.Text = "Cancel"; cancel.Top = 160; cancel.Left = 380; cancel.Width = 90
    cancel.DialogResult = DR.Cancel

    form.Controls.Add(lbl)
    form.Controls.Add(l1); form.Controls.Add(t1)
    form.Controls.Add(l2); form.Controls.Add(t2)
    form.Controls.Add(ok); form.Controls.Add(cancel)
    form.AcceptButton = ok
    form.CancelButton = cancel

    if form.ShowDialog() != DR.OK:
        return None
    out = {
        "clientId": (t1.Text or "").strip(),
        "clientSecret": (t2.Text or "").strip(),
        "callbackUrl": APS_CALLBACK_URL
    }
    if not out["clientId"] or not out["clientSecret"]:
        info("Client ID and Client Secret are both required.")
        return None
    save_aps_cfg(out)
    return out


# ---------------------------------------------------------------------------
# APS OAuth (authorization code + localhost callback)
# ---------------------------------------------------------------------------
def _http_post_form(url, data, headers=None):
    """Minimal POST using System.Net (works in IronPython)."""
    from System.Net import WebClient, WebRequest
    from System.Text import Encoding
    req = WebRequest.Create(url)
    req.Method = "POST"
    req.ContentType = "application/x-www-form-urlencoded"
    if headers:
        for k, v in headers.items():
            if k.lower() == "authorization":
                req.Headers.Add("Authorization", v)
            elif k.lower() != "content-type":
                try:
                    req.Headers.Add(k, v)
                except Exception:
                    pass
    body = Encoding.UTF8.GetBytes(data)
    req.ContentLength = body.Length
    stream = req.GetRequestStream()
    stream.Write(body, 0, body.Length)
    stream.Close()
    resp = req.GetResponse()
    from System.IO import StreamReader as _SR
    reader = _SR(resp.GetResponseStream())
    text = reader.ReadToEnd()
    reader.Close()
    resp.Close()
    return text

def _http_get_json(url, token):
    from System.Net import WebRequest
    from System.IO import StreamReader
    req = WebRequest.Create(url)
    req.Method = "GET"
    req.Headers.Add("Authorization", "Bearer " + token)
    resp = req.GetResponse()
    reader = StreamReader(resp.GetResponseStream())
    text = reader.ReadToEnd()
    reader.Close()
    resp.Close()
    return json.loads(text)

def load_tokens():
    if not File.Exists(APS_TOKEN_PATH):
        return None
    try:
        return json.loads(File.ReadAllText(APS_TOKEN_PATH))
    except Exception:
        return None

def save_tokens(tok):
    ensure_config_dir()
    File.WriteAllText(APS_TOKEN_PATH, json.dumps(tok, indent=2))

def tokens_valid(tok):
    if not tok or not tok.get("access_token"):
        return False
    exp = tok.get("expires_at") or 0
    return time.time() < float(exp) - 60

def refresh_tokens(cfg, tok):
    if not tok or not tok.get("refresh_token"):
        return None
    import base64
    basic = base64.b64encode(
        ("%s:%s" % (cfg["clientId"], cfg["clientSecret"])).encode("ascii")
    ).decode("ascii")
    try:
        import System
        data = "grant_type=refresh_token&refresh_token=" + tok["refresh_token"]
        text = _http_post_form(
            APS_AUTH + "/token",
            data,
            {"Authorization": "Basic " + basic}
        )
        js = json.loads(text)
        out = {
            "access_token": js["access_token"],
            "refresh_token": js.get("refresh_token") or tok["refresh_token"],
            "expires_at": time.time() + int(js.get("expires_in") or 3600),
            "token_type": js.get("token_type") or "Bearer"
        }
        save_tokens(out)
        return out
    except Exception as ex:
        print("refresh failed", ex)
        return None

def _exchange_code_for_token(cfg, code):
    """Exchange authorization code for tokens."""
    import base64
    import System
    client_id = cfg["clientId"]
    client_secret = cfg["clientSecret"]
    redirect = APS_CALLBACK_URL
    basic = base64.b64encode(
        ("%s:%s" % (client_id, client_secret)).encode("ascii")
    ).decode("ascii")
    data = (
        "grant_type=authorization_code"
        + "&code=" + code
        + "&redirect_uri=" + System.Uri.EscapeDataString(redirect)
    )
    text_body = _http_post_form(
        APS_AUTH + "/token",
        data,
        {"Authorization": "Basic " + basic}
    )
    js = json.loads(text_body)
    if not js.get("access_token"):
        raise Exception("No access_token in response: " + text_body[:500])
    tok = {
        "access_token": js["access_token"],
        "refresh_token": js.get("refresh_token"),
        "expires_at": time.time() + int(js.get("expires_in") or 3600),
        "token_type": js.get("token_type") or "Bearer"
    }
    save_tokens(tok)
    return tok


def _extract_code_from_text(s):
    """Accept full redirect URL or raw code."""
    s = (s or "").strip()
    if not s:
        return None
    # full URL? code=...
    m = re.search(r"[?&#]code=([^&\\s#]+)", s)
    if m:
        return m.group(1)
    # bare code (no spaces, reasonably long)
    if " " not in s and len(s) > 20 and "http" not in s.lower():
        return s
    return None




def choose_json_source():
    """Neat dialog: Local File | Sign In | Cancel. Returns 'local' | 'signin' | None."""
    form = Form()
    form.Text = "Atana Project Sync"
    form.Width = 460
    form.Height = 250
    form.StartPosition = FormStartPosition.CenterScreen
    try:
        form.FormBorderStyle = FormBorderStyle.FixedDialog
    except Exception:
        pass
    form.MaximizeBox = False
    form.MinimizeBox = False
    try:
        form.TopMost = True
    except Exception:
        pass

    result = {"v": None}

    title = Label()
    title.Text = "Load project DB JSON"
    title.Left = 20
    title.Top = 16
    title.Width = 410
    title.Height = 28
    try:
        import System.Drawing
        title.Font = System.Drawing.Font("Segoe UI", 11, System.Drawing.FontStyle.Bold)
    except Exception:
        pass

    body = Label()
    body.Text = (
        "Choose how to get the project information file for Revit sync.\n\n"
        "Local File — JSON from Atana IM (export / push) — recommended.\n"
        "Sign In — Autodesk (APS). Prefer Edge so company SSO is used."
    )
    body.Left = 20
    body.Top = 48
    body.Width = 410
    body.Height = 100

    def on_local(s, e):
        result["v"] = "local"
        form.DialogResult = DR.OK
        form.Close()

    def on_signin(s, e):
        result["v"] = "signin"
        form.DialogResult = DR.OK
        form.Close()

    def on_cancel(s, e):
        result["v"] = None
        form.DialogResult = DR.Cancel
        form.Close()

    btn_local = Button()
    btn_local.Text = "Local File"
    btn_local.Width = 120
    btn_local.Height = 32
    btn_local.Left = 20
    btn_local.Top = 160
    btn_local.Click += on_local

    btn_signin = Button()
    btn_signin.Text = "Sign In"
    btn_signin.Width = 120
    btn_signin.Height = 32
    btn_signin.Left = 150
    btn_signin.Top = 160
    btn_signin.Click += on_signin

    btn_cancel = Button()
    btn_cancel.Text = "Cancel"
    btn_cancel.Width = 120
    btn_cancel.Height = 32
    btn_cancel.Left = 280
    btn_cancel.Top = 160
    btn_cancel.Click += on_cancel

    form.Controls.Add(title)
    form.Controls.Add(body)
    form.Controls.Add(btn_local)
    form.Controls.Add(btn_signin)
    form.Controls.Add(btn_cancel)
    form.AcceptButton = btn_local
    form.CancelButton = btn_cancel
    form.ShowDialog()
    return result["v"]


def open_browser(url):
    """Open browser from Revit. Prefer Edge (company SSO / Autodesk cookies)."""
    if not url:
        return False
    errors = []

    def _popen(args):
        try:
            import subprocess
            subprocess.Popen(args, shell=False)
            return True
        except Exception as ex:
            errors.append(str(ex))
            return False

    # 1) Edge with Default profile (SSO)
    for edge in (
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ):
        if os.path.isfile(edge):
            if _popen([edge, "--profile-directory=Default", url]):
                return True
            if _popen([edge, url]):
                return True

    # 2) Edge URL protocol
    try:
        Process.Start("microsoft-edge:" + url)
        return True
    except Exception as ex:
        errors.append("edge-protocol: " + str(ex))

    # 3) os.startfile
    try:
        os.startfile(url)
        return True
    except Exception as ex:
        errors.append("startfile: " + str(ex))

    # 4) cmd start
    if _popen(["cmd", "/c", "start", "", url]):
        return True

    # 5) Process.Start
    try:
        Process.Start(url)
        return True
    except Exception as ex:
        errors.append("Process: " + str(ex))

    try:
        print("[Atana] open_browser failed: " + " | ".join(errors))
    except Exception:
        pass
    return False



def prompt_paste_auth_code(auth_url):
    """Fallback when Windows blocks HttpListener — user pastes redirect URL or code."""
    form = Form()
    form.Text = "Atana — paste Autodesk login code"
    form.Width = 560
    form.Height = 320
    form.StartPosition = FormStartPosition.CenterScreen

    lbl = Label()
    lbl.Text = (
        "Complete Autodesk login in Edge (company SSO).\n\n"
        "1) Browser should open Autodesk login (or open the URL shown after OK).\n"
        "2) Sign in and Allow.\n"
        "3) Browser may show an error page — that is OK.\n"
        "4) Copy the FULL address from the browser bar\n"
        "   (starts with http://127.0.0.1:%d/callback?code=...)\n"
        "   and paste it below."
    ) % APS_CALLBACK_PORT
    lbl.Top = 10
    lbl.Left = 12
    lbl.Width = 520
    lbl.Height = 120

    t = TextBox()
    t.Top = 140
    t.Left = 12
    t.Width = 520
    t.Height = 60
    t.Multiline = True

    ok = Button(); ok.Text = "Continue"; ok.Top = 220; ok.Left = 320; ok.Width = 100
    ok.DialogResult = DR.OK
    cancel = Button(); cancel.Text = "Cancel"; cancel.Top = 220; cancel.Left = 430; cancel.Width = 100
    cancel.DialogResult = DR.Cancel
    openbtn = Button(); openbtn.Text = "Open login URL"; openbtn.Top = 220; openbtn.Left = 12; openbtn.Width = 120

    def _open(sender, args):
        try:
            open_browser(auth_url)
        except Exception:
            pass
    openbtn.Click += _open

    form.Controls.Add(lbl)
    form.Controls.Add(t)
    form.Controls.Add(ok)
    form.Controls.Add(cancel)
    form.Controls.Add(openbtn)
    form.AcceptButton = ok
    form.CancelButton = cancel

    try:
        open_browser(auth_url)
    except Exception:
        pass

    if form.ShowDialog() != DR.OK:
        return None
    return _extract_code_from_text(t.Text)


def aps_login_interactive(cfg):
    """Prefer localhost callback; on Windows block / timeout, fall back to paste-code."""
    import base64
    import System
    from System.Net import HttpListener
    from System.Threading import Thread, ThreadStart, ManualResetEvent

    client_id = cfg["clientId"]
    redirect = APS_CALLBACK_URL

    auth_url = (
        APS_AUTH + "/authorize"
        + "?response_type=code"
        + "&client_id=" + client_id
        + "&redirect_uri=" + System.Uri.EscapeDataString(redirect)
        + "&scope=" + System.Uri.EscapeDataString(APS_SCOPES)
    )

    listener_ok = False
    listener = None
    try:
        listener = HttpListener()
        prefix = "http://127.0.0.1:%d/" % APS_CALLBACK_PORT
        listener.Prefixes.Add(prefix)
        listener.Start()
        listener_ok = True
    except Exception as ex:
        print("HttpListener start failed:", ex)
        listener_ok = False

    if not listener_ok:
        # --- Windows block path ---
        info(
            "Windows blocked HttpListener on port %d.\n\n"
            "Fix (run once in Command Prompt as Administrator):\n\n"
            "  netsh http add urlacl url=http://127.0.0.1:%d/ user=%%USERNAME%%\n\n"
            "Or use the next dialog to paste the browser redirect URL / code."
            % (APS_CALLBACK_PORT, APS_CALLBACK_PORT)
        )
        code = prompt_paste_auth_code(auth_url)
        if not code:
            return None
        try:
            return _exchange_code_for_token(cfg, code)
        except Exception as ex:
            info("Token exchange failed:\n" + str(ex))
            return None

    # --- Listener path with timeout ---
    holder = {"ctx": None, "err": None}
    done = ManualResetEvent(False)

    def _accept():
        try:
            holder["ctx"] = listener.GetContext()
        except Exception as ex:
            holder["err"] = str(ex)
        try:
            done.Set()
        except Exception:
            pass

    th = Thread(ThreadStart(_accept))
    th.IsBackground = True
    th.Start()

    opened = False
    try:
        opened = open_browser(auth_url)
    except Exception:
        opened = False

    info(
        ("Browser opened for Autodesk login." if opened else "Could not auto-open browser — copy the URL from the next step.")
        + "\n\nYou have %d seconds.\n"
        "Callback must be:\n%s"
        % (APS_LOGIN_TIMEOUT_SEC, redirect)
    )

    ok = done.WaitOne(int(APS_LOGIN_TIMEOUT_SEC * 1000))
    if not ok:
        try:
            listener.Stop()
        except Exception:
            pass
        info(
            "Local callback timed out (Windows often blocks this).\n\n"
            "Next dialog: paste the browser address bar URL\n"
            "(http://127.0.0.1:%d/callback?code=...).\n\n"
            "Optional permanent fix (Admin CMD):\n"
            "  netsh http add urlacl url=http://127.0.0.1:%d/ user=%%USERNAME%%"
            % (APS_CALLBACK_PORT, APS_CALLBACK_PORT)
        )
        code = prompt_paste_auth_code(auth_url)
        if not code:
            return None
        try:
            return _exchange_code_for_token(cfg, code)
        except Exception as ex:
            info("Token exchange failed:\n" + str(ex))
            return None

    ctx = holder["ctx"]
    if ctx is None:
        try:
            listener.Stop()
        except Exception:
            pass
        code = prompt_paste_auth_code(auth_url)
        if not code:
            return None
        try:
            return _exchange_code_for_token(cfg, code)
        except Exception as ex:
            info("Token exchange failed:\n" + str(ex))
            return None

    code = None
    try:
        req = ctx.Request
        code = req.QueryString["code"]
        err = req.QueryString["error"]
        html = """<html><body style="font-family:sans-serif;padding:24px">
        <h2>Atana Project Sync</h2>
        <p>Login complete. Close this tab and return to Revit.</p>
        </body></html>"""
        if err or not code:
            html = """<html><body style="font-family:sans-serif;padding:24px">
            <h2>Login failed</h2><p>%s</p></body></html>""" % (err or "No code")
        buf = System.Text.Encoding.UTF8.GetBytes(html)
        ctx.Response.ContentLength64 = buf.Length
        ctx.Response.OutputStream.Write(buf, 0, buf.Length)
        ctx.Response.OutputStream.Close()
    except Exception as ex:
        print("callback read error", ex)
    finally:
        try:
            listener.Stop()
        except Exception:
            pass

    if not code:
        code = prompt_paste_auth_code(auth_url)
        if not code:
            return None
    try:
        return _exchange_code_for_token(cfg, code)
    except Exception as ex:
        info("Token exchange failed:\n" + str(ex))
        return None


def ensure_aps_token():
    cfg = load_aps_cfg()
    if not cfg.get("clientId") or not cfg.get("clientSecret"):
        info("APS Client ID / Secret are not set in script.py.\n\n"
             "A site admin must set APS_CLIENT_ID and APS_CLIENT_SECRET "
             "at the top of script.py (company APS app).")
        # last resort prompt for admin machines only
        cfg = prompt_aps_credentials()
        if not cfg:
            return None, None
    tok = load_tokens()
    if tokens_valid(tok):
        return cfg, tok
    if tok:
        tok = refresh_tokens(cfg, tok)
        if tokens_valid(tok):
            return cfg, tok
    tok = aps_login_interactive(cfg)
    if tokens_valid(tok):
        return cfg, tok
    return cfg, None


# ---------------------------------------------------------------------------
# Local JSON helpers
# ---------------------------------------------------------------------------
def load_sync_folder():
    if File.Exists(CONFIG_PATH):
        try:
            p = File.ReadAllText(CONFIG_PATH).strip()
            if p and Directory.Exists(p):
                return p
        except Exception:
            pass
    return None

def save_sync_folder(path):
    ensure_config_dir()
    File.WriteAllText(CONFIG_PATH, path)

def pick_folder(prompt="Select folder that contains the Atana DB JSON"):
    dlg = FolderBrowserDialog()
    dlg.Description = prompt
    if dlg.ShowDialog() == DialogResult.OK:
        return dlg.SelectedPath
    return None

def pick_json_file():
    dlg = OpenFileDialog()
    dlg.Filter = "JSON (*.json)|*.json|All files (*.*)|*.*"
    dlg.Title = "Select Atana project DB JSON"
    if dlg.ShowDialog() == DialogResult.OK:
        return dlg.FileName
    return None

def find_db_json_in_folder(folder):
    if not folder or not Directory.Exists(folder):
        return None
    # Prefer *DB*.json or *revit*sync*.json
    try:
        names = list(Directory.GetFiles(folder, "*.json"))
    except Exception:
        return None
    prefer = []
    other = []
    for n in names:
        base = os.path.basename(n).lower()
        if "db" in base or "revit" in base or "atana" in base or "sync" in base:
            prefer.append(n)
        else:
            other.append(n)
    pool = prefer or other
    if not pool:
        return None
    pool.sort(key=lambda p: File.GetLastWriteTime(p).Ticks, reverse=True)
    return pool[0]

def load_pack_from_path(path):
    text = File.ReadAllText(path)
    return json.loads(text)


# ---------------------------------------------------------------------------
# Model / role helpers
# ---------------------------------------------------------------------------
def model_path(doc):
    try:
        p = doc.PathName
        return p or ""
    except Exception:
        return ""

def parse_role_from_model_name(path):
    base = os.path.basename(path or "")
    base = re.sub(r"\.rvt$", "", base, flags=re.I)
    parts = base.split("-")
    if len(parts) >= 6:
        # Project-Orig-Func-Spatial-Form-Role-Number
        return parts[-2].upper()
    if len(parts) >= 2:
        return parts[-2].upper()
    return ""


# ---------------------------------------------------------------------------
# Shared parameters / Project Info / Globals
# ---------------------------------------------------------------------------
def ensure_shared_params(doc, app):
    if not File.Exists(SHARED_PARAM_FILE):
        print("Shared param file missing:", SHARED_PARAM_FILE)
        return False
    prev = app.SharedParametersFilename
    try:
        app.SharedParametersFilename = SHARED_PARAM_FILE
        def_file = app.OpenSharedParameterFile()
        if def_file is None:
            return False
        # Group
        group = None
        for g in def_file.Groups:
            group = g
            break
        if group is None:
            return False
        cats = app.Create.NewCategorySet()
        cats.Insert(doc.Settings.Categories.get_Item(BuiltInCategory.OST_ProjectInformation))
        binding_map = doc.ParameterBindings
        t = Transaction(doc, "Atana — ensure shared params")
        t.Start()
        try:
            for defn in group.Definitions:
                name = defn.Name
                if name not in SHARED_GUIDS:
                    continue
                # already bound?
                it = binding_map.ForwardIterator()
                it.Reset()
                found = False
                while it.MoveNext():
                    try:
                        if it.Key and it.Key.Name == name:
                            found = True
                            break
                    except Exception:
                        pass
                if found:
                    continue
                binding = app.Create.NewInstanceBinding(cats)
                # BuiltInParameterGroup may differ by Revit version
                try:
                    from Autodesk.Revit.DB import BuiltInParameterGroup
                    binding_map.Insert(defn, binding, BuiltInParameterGroup.PG_DATA)
                except Exception:
                    try:
                        binding_map.Insert(defn, binding)
                    except Exception as ex:
                        print("bind", name, ex)
        finally:
            t.Commit()
        return True
    except Exception as ex:
        print("ensure_shared_params:", ex)
        return False
    finally:
        try:
            app.SharedParametersFilename = prev
        except Exception:
            pass

def get_project_info_element(doc):
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectInformation)
    for e in col:
        return e
    return None

def set_pi_builtin(pi, bip, value):
    if value is None:
        return False
    p = pi.get_Parameter(bip)
    if p is None or p.IsReadOnly:
        return False
    try:
        if p.StorageType == StorageType.String:
            cur = p.AsString() or ""
            if cur == str(value):
                return False
            p.Set(str(value))
            return True
    except Exception as ex:
        print("set_pi_builtin", bip, ex)
    return False

def set_pi_shared_by_name(pi, name, value):
    if value is None:
        return False
    for p in pi.Parameters:
        if p.Definition and p.Definition.Name == name:
            if p.IsReadOnly:
                return False
            try:
                if p.StorageType == StorageType.String:
                    cur = p.AsString() or ""
                    if cur == str(value):
                        return False
                    p.Set(str(value))
                    return True
            except Exception as ex:
                print("set_pi_shared", name, ex)
    return False

def read_pi_value(pi, name_or_bip):
    if isinstance(name_or_bip, BuiltInParameter):
        p = pi.get_Parameter(name_or_bip)
        return (p.AsString() if p else "") or ""
    for p in pi.Parameters:
        if p.Definition and p.Definition.Name == name_or_bip:
            return (p.AsString() if p else "") or ""
    return ""

def set_global(doc, name, value, is_integer=False):
    if value is None or value == "":
        return False
    gp = None
    for g in FilteredElementCollector(doc).OfClass(GlobalParameter):
        if g.GetDefinition().Name == name:
            gp = g
            break
    t = Transaction(doc, "Atana — global " + name)
    t.Start()
    try:
        if gp is None:
            try:
                from Autodesk.Revit.DB import SpecTypeId
                if is_integer:
                    gp = GlobalParameter.Create(doc, name, SpecTypeId.Int.Integer)
                else:
                    gp = GlobalParameter.Create(doc, name, SpecTypeId.String.Text)
            except Exception:
                try:
                    from Autodesk.Revit.DB import ParameterType as PT
                    if is_integer:
                        gp = GlobalParameter.Create(doc, name, PT.Integer)
                    else:
                        gp = GlobalParameter.Create(doc, name, PT.Text)
                except Exception as ex:
                    print("create global", name, ex)
                    t.RollBack()
                    return False
        if is_integer:
            try:
                gp.SetValue(IntegerParameterValue(int(str(value).lstrip("SsWw"))))
            except Exception:
                gp.SetValue(IntegerParameterValue(0))
        else:
            gp.SetValue(StringParameterValue(str(value)))
        t.Commit()
        return True
    except Exception as ex:
        print("set_global", name, ex)
        try:
            t.RollBack()
        except Exception:
            pass
        return False


# ---------------------------------------------------------------------------
# Title blocks + publish set + sheet inventory
# ---------------------------------------------------------------------------
def apply_titleblocks(doc, designed_by, checked_by):
    count = 0
    t = Transaction(doc, "Atana — title blocks")
    t.Start()
    try:
        for tb in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType():
            changed = False
            for p in tb.Parameters:
                if not p.Definition or p.IsReadOnly:
                    continue
                n = p.Definition.Name
                if designed_by and n in TITLEBLOCK_DESIGNED and p.StorageType == StorageType.String:
                    if (p.AsString() or "") != designed_by:
                        p.Set(designed_by)
                        changed = True
                if checked_by and n in TITLEBLOCK_CHECKED and p.StorageType == StorageType.String:
                    if (p.AsString() or "") != checked_by:
                        p.Set(checked_by)
                        changed = True
            if changed:
                count += 1
        t.Commit()
    except Exception as ex:
        print("titleblocks", ex)
        try:
            t.RollBack()
        except Exception:
            pass
    return count

def match_sheets_to_plan(doc, plan_rows, role):
    sheets = list(FilteredElementCollector(doc).OfClass(ViewSheet))
    if not plan_rows:
        return sheets  # no plan → leave empty; caller decides
    ids = set()
    for r in plan_rows:
        did = (r.get("documentId") or r.get("name") or "").upper()
        if role and ("-" + role + "-") not in did and not did.endswith("-" + role):
            # soft filter by role segment
            pass
        ids.add(re.sub(r"\.[A-Z0-9]+$", "", did))
    matched = []
    for s in sheets:
        try:
            num = (s.SheetNumber or "").upper()
            name = (s.Name or "").upper()
            key = num
            for pid in ids:
                if num and num in pid:
                    matched.append(s)
                    break
                if name and name in pid:
                    matched.append(s)
                    break
        except Exception:
            pass
    return matched

def create_or_update_print_set(doc, set_name, sheets):
    """Best-effort in-session ViewSheetSet via PrintManager."""
    if not sheets:
        return 0
    t = Transaction(doc, "Atana — publish set " + set_name)
    t.Start()
    try:
        pm = doc.PrintManager
        pm.PrintRange = pm.PrintRange.Select
        vss = pm.ViewSheetSetting
        vs = ViewSet()
        for s in sheets:
            vs.Insert(s)
        # Remove existing with same name if possible
        try:
            existing = vss.InSession
        except Exception:
            existing = None
        try:
            vss.CurrentViewSheetSet.Views = vs
            vss.SaveAs(set_name)
        except Exception:
            try:
                vss.SaveAs(set_name)
            except Exception as ex:
                print("SaveAs set", ex)
        t.Commit()
        return len(list(sheets))
    except Exception as ex:
        print("publish set", ex)
        try:
            t.RollBack()
        except Exception:
            pass
        return 0

def export_sheet_inventory(folder, role, pack, doc):
    try:
        sheets = []
        for s in FilteredElementCollector(doc).OfClass(ViewSheet):
            sheets.append({
                "sheetNumber": s.SheetNumber,
                "sheetName": s.Name,
                "uniqueId": s.UniqueId
            })
        out = {
            "schema": "atana-sheet-inventory/1.0",
            "role": role,
            "projectCode": (pack.get("project") or {}).get("code") if isinstance(pack.get("project"), dict) else pack.get("code"),
            "sheets": sheets,
            "exportedAt": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        path = os.path.join(folder, "sheet-inventory-%s.json" % (role or "ZZ"))
        File.WriteAllText(path, json.dumps(out, indent=2))
        return path
    except Exception as ex:
        print("inventory", ex)
        return None


# ---------------------------------------------------------------------------
# Pack field extraction (flexible schema)
# ---------------------------------------------------------------------------
def extract_pi(pack):
    """Support both nested pack.projectInformation and flat project keys."""
    if not isinstance(pack, dict):
        return {}
    pi = pack.get("projectInformation") or pack.get("projectInfo") or {}
    if not pi and pack.get("project"):
        p = pack["project"]
        pi = {
            "Project Number": p.get("code") or p.get("projectNumber") or p.get("number"),
            "Project Name": p.get("name") or p.get("projectName"),
            "Client Name": p.get("client") or p.get("clientName"),
            "Project Address": p.get("address") or p.get("projectAddress"),
            "Organization Name": p.get("originator") or p.get("organizationName") or "ATANA",
            "ATA_ZZ_ClientContractNumber": p.get("clientContractNo") or p.get("clientContractNumber"),
            "ATA_ZZ_ProjectDiscipline": p.get("discipline") or "",
            "ATA_ZZ_ProjectStage": p.get("currentStageId") or p.get("projectStage") or "",
        }
    # globals
    return pi

def extract_stage(pack):
    p = pack.get("project") if isinstance(pack.get("project"), dict) else pack
    return (p.get("currentStageId") or p.get("projectStage") or
            pack.get("currentStageId") or "S1")

def extract_plan_rows(pack):
    # deliverables / stageDeliverables / midp
    rows = pack.get("deliverables") or pack.get("planRows") or []
    if rows:
        return rows
    sd = pack.get("stageDeliverables") or {}
    stage = extract_stage(pack)
    block = sd.get(stage) or {}
    if isinstance(block, dict):
        return block.get("rows") or []
    return []

def extract_titleblock_map(pack):
    """role → {designedBy, checkedBy} from organogram / projectTeam."""
    out = {}
    team = pack.get("projectTeam") or {}
    members = team.get("members") if isinstance(team, dict) else []
    if not members and isinstance(pack.get("organogram"), list):
        members = pack["organogram"]
    for m in members or []:
        disc = (m.get("discipline") or m.get("roleCode") or "").upper()
        func = (m.get("func") or "").upper()
        name = m.get("name") or ""
        if not disc or not name:
            continue
        if disc not in out:
            out[disc] = {}
        if func == "TTM":
            out[disc]["designedBy"] = name
        if func in ("PEER", "PR"):
            out[disc]["checkedBy"] = name
            out[disc]["approvedBy"] = name
    # also pack.revit.titleblocks
    tb = (pack.get("revit") or {}).get("titleblocks") or pack.get("titleblocks") or {}
    for role, val in tb.items():
        if isinstance(val, dict):
            out.setdefault(role.upper(), {}).update(val)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if IMPORT_ERROR:
        # Can't even show TaskDialog if imports failed hard
        print(IMPORT_ERROR)
        try:
            TaskDialog.Show("Atana Project Sync", "Import error:\n" + IMPORT_ERROR[:1500])
        except Exception:
            pass
        return

    # Resolve Revit context INSIDE main (avoids blank window / Pylance noise)
    try:
        _revit = __revit__  # noqa: F821  — provided by pyRevit at runtime
    except NameError:
        info("This script must be run from pyRevit inside Revit.\n"
             "__revit__ was not found.")
        return

    if _revit.ActiveUIDocument is None:
        info("Open a project model first, then run Project Sync.")
        return

    doc = _revit.ActiveUIDocument.Document
    uidoc = _revit.ActiveUIDocument
    app = _revit.Application

    if doc.IsFamilyDocument:
        info("Open a project (.rvt), not a family.")
        return

    # ---- Choose data source ----
    source = None
    pack = None
    json_path = None

    source_mode = choose_json_source()
    if not source_mode:
        return

    if source_mode == "signin":
        # ACC / APS login — use Edge so company SSO cookies apply
        cfg, tok = ensure_aps_token()
        if not tok:
            info(
                "Sign-in did not complete.\n\n"
                "Tips:\n"
                "• Sign in to Autodesk in Edge first (same PC user).\n"
                "• APS Callback URL must be exactly:\n  " + APS_CALLBACK_URL + "\n"
                "• Client ID / Secret must match that APS app.\n\n"
                "You can still load a Local File next."
            )
            source_mode = "local"
        else:
            info(
                "Signed in to Autodesk.\n\n"
                "ACC folder browse is limited here.\n"
                "Use Atana IM → Push DB JSON, then choose Local File,\n"
                "or keep the JSON in your remembered sync folder.\n\n"
                "Checking the saved sync folder…"
            )
            folder = load_sync_folder()
            if folder:
                json_path = find_db_json_in_folder(folder)
            if json_path:
                try:
                    pack = load_pack_from_path(json_path)
                    source = "local+token"
                except Exception as ex:
                    info("Could not read JSON in sync folder:\n" + str(ex))
                    pack = None
            if pack is None:
                info("No JSON found after sign-in.\nPick a local JSON file.")
                source_mode = "local"

    if source_mode == "local" and pack is None:
        folder = load_sync_folder()
        if folder:
            json_path = find_db_json_in_folder(folder)
        if not json_path:
            # ask file or folder
            if confirm("Pick a JSON file?\n\nYes = file\nNo = folder"):
                json_path = pick_json_file()
                if json_path:
                    save_sync_folder(os.path.dirname(json_path))
            else:
                folder = pick_folder()
                if folder:
                    save_sync_folder(folder)
                    json_path = find_db_json_in_folder(folder)
        if not json_path:
            info("No JSON selected.")
            return
        try:
            pack = load_pack_from_path(json_path)
            source = "local"
        except Exception as ex:
            info("Could not read JSON:\n" + str(ex))
            return

    if not pack:
        info("No project pack loaded.")
        return

    # ---- Extract ----
    pi_src = extract_pi(pack)
    stage_code = extract_stage(pack)
    plan_rows = extract_plan_rows(pack)
    tb_map = extract_titleblock_map(pack)

    role = parse_role_from_model_name(model_path(doc))
    if not role:
        role = (pi_src.get("ATA_ZZ_ProjectDiscipline") or "").upper()

    team_info = tb_map.get(role) or {}
    designed_by = team_info.get("designedBy") or ""
    checked_by = team_info.get("approvedBy") or team_info.get("checkedBy") or ""

    ensure_shared_params(doc, app)
    pi = get_project_info_element(doc)
    if pi is None:
        info("No Project Information element found.")
        return

    PI_BUILTIN = {
        "Project Number": BuiltInParameter.PROJECT_NUMBER,
        "Project Name": BuiltInParameter.PROJECT_NAME,
        "Client Name": BuiltInParameter.CLIENT_NAME,
        "Project Address": BuiltInParameter.PROJECT_ADDRESS,
        "Organization Name": BuiltInParameter.PROJECT_ORGANIZATION_NAME,
    }

    desired_pi = {
        "Project Number": pi_src.get("Project Number") or pi_src.get("projectNumber") or "",
        "Project Name": pi_src.get("Project Name") or pi_src.get("projectName") or "",
        "Client Name": pi_src.get("Client Name") or pi_src.get("clientName") or "",
        "Project Address": pi_src.get("Project Address") or pi_src.get("projectAddress") or "",
        "Organization Name": pi_src.get("Organization Name") or pi_src.get("organizationName") or "",
        "ATA_ZZ_ClientContractNumber": pi_src.get("ATA_ZZ_ClientContractNumber") or "",
        "ATA_ZZ_ProjectDiscipline": role or pi_src.get("ATA_ZZ_ProjectDiscipline") or "",
        "ATA_ZZ_ProjectStage": pi_src.get("ATA_ZZ_ProjectStage") or stage_code,
    }

    mismatches = []
    for k, new_v in desired_pi.items():
        if not new_v:
            continue
        bip = PI_BUILTIN.get(k)
        cur = read_pi_value(pi, bip if bip is not None else k)
        if (cur or "") != str(new_v):
            mismatches.append((k, cur, new_v))

    if mismatches:
        lines = ["Project Information differs from Atana pack:\n"]
        for k, cur, new_v in mismatches:
            lines.append(u"• {}: \"{}\" → \"{}\"".format(k, cur, new_v))
        lines.append("\nUpdate all listed values?")
        if confirm("\n".join(lines)):
            t = Transaction(doc, "Atana — project information")
            t.Start()
            try:
                for k, cur, new_v in mismatches:
                    bip = PI_BUILTIN.get(k)
                    if bip is not None:
                        set_pi_builtin(pi, bip, new_v)
                    else:
                        set_pi_shared_by_name(pi, k, new_v)
                t.Commit()
            except Exception as ex:
                try:
                    t.RollBack()
                except Exception:
                    pass
                info("Project Information update failed:\n" + str(ex))
    else:
        print("Project Information already matches pack")

    # Globals
    globals_map = {
        "GLOBAL_ZZ_ClientContractNumber": desired_pi.get("ATA_ZZ_ClientContractNumber"),
        "GLOBAL_ZZ_ProjectDiscipline": desired_pi.get("ATA_ZZ_ProjectDiscipline"),
        "GLOBAL_ZZ_ProjectStage": desired_pi.get("ATA_ZZ_ProjectStage"),
        "GLOBAL_ZZ_ProjectDeliveryManager": "",
        "GLOBAL_ZZ_InformationManager": "",
    }
    team = pack.get("projectTeam") or {}
    for m in (team.get("members") or []):
        if (m.get("func") or "").upper() == "PDM":
            globals_map["GLOBAL_ZZ_ProjectDeliveryManager"] = m.get("name") or ""
        if (m.get("func") or "").upper() == "IM":
            globals_map["GLOBAL_ZZ_InformationManager"] = m.get("name") or ""

    for n, val in globals_map.items():
        if not val:
            continue
        set_global(doc, n, val, is_integer=(n == "GLOBAL_ZZ_ProjectStage"))

    # Title blocks
    if designed_by or checked_by:
        msg = ("Title blocks for task team {}:\n\n"
               "Designed By (TTM): {}\n"
               "Checked By (Peer): {}\n\n"
               "Apply to all title blocks in this model?").format(
                   role or "—", designed_by or "—", checked_by or "—")
        if confirm(msg):
            n = apply_titleblocks(doc, designed_by, checked_by)
            info("Updated parameters on {} title block instance(s).".format(n))

    # Publish set
    matched = match_sheets_to_plan(doc, plan_rows, role)
    set_name = stage_code if stage_code else "S1"
    if set_name.startswith("S") and not set_name.startswith("WS"):
        set_name = "WS" + set_name[1:]
    if matched and plan_rows:
        msg = ("Publish Set \"{}\"\n\n"
               "Matched {} sheet(s) from the plan for role {}.\n"
               "Create / replace this publish set?").format(set_name, len(matched), role or "all")
        if confirm(msg):
            n = create_or_update_print_set(doc, set_name, matched)
            info("Publish set \"{}\" processed ({} sheet(s)).".format(set_name, n))

    folder = os.path.dirname(json_path) if json_path else load_sync_folder()
    inv = None
    if folder:
        inv = export_sheet_inventory(folder, role or "ZZ", pack, doc)

    info(
        "Project Sync complete.\n\n"
        "Source: {}\n"
        "JSON: {}\n"
        "Role: {}\n"
        "Stage: {}\n"
        "Publish set: {}\n"
        "Sheet inventory: {}".format(
            source or "—",
            os.path.basename(json_path) if json_path else "—",
            role or "—",
            stage_code,
            set_name,
            os.path.basename(inv) if inv else "—"
        )
    )


# pyRevit executes the script body — always call main (don't rely on __name__)
try:
    main()
except Exception:
    err = traceback.format_exc()
    print(err)
    try:
        TaskDialog.Show("Atana Project Sync — error", err[:3000])
    except Exception:
        pass
