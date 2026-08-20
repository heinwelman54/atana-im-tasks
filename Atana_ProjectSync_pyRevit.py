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
        ViewSheet, ViewSet, FamilySymbol, ElementId
    )
    from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons, TaskDialogResult
    from System.Windows.Forms import (
        OpenFileDialog, DialogResult, FolderBrowserDialog, Form,
        Label, TextBox, Button, DockStyle, FormStartPosition, DialogResult as DR, FormBorderStyle,
        CheckedListBox, ComboBox, CheckState, Panel, Padding
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

def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()

def find_shared_param_file():
    names = ["ATA_ZZ_SharedParameters_MERGED.txt", "ATA_ZZ_SharedParameters.txt"]
    bases = []
    try:
        d = _script_dir()
        for _ in range(6):
            if d and d not in bases:
                bases.append(d)
            d = os.path.dirname(d) if d else None
    except Exception:
        pass
    bases.extend([
        os.path.expandvars(r"%APPDATA%\\Atana"),
        os.path.expandvars(r"%APPDATA%\\pyRevit"),
        os.path.expandvars(r"%APPDATA%\\pyRevit\\Extensions"),
        r"C:\\Atana",
    ])
    for base in bases:
        if not base:
            continue
        for name in names:
            path = os.path.join(base, name)
            if os.path.isfile(path):
                return path
    return os.path.join(_script_dir(), names[0])

SHARED_PARAM_FILE = find_shared_param_file()

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



def confirm_lines(lines, title="Atana Project Sync"):
    """Join lines with real newlines for TaskDialog."""
    msg = chr(10).join([str(x) for x in lines])
    return confirm(msg, title)

def info_lines(lines, title="Atana Project Sync"):
    msg = chr(10).join([str(x) for x in lines])
    info(msg, title)

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
        "Local File - JSON from Atana IM (export / push) - recommended.\n"
        "Sign In - Autodesk (APS). Prefer Edge so company SSO is used."
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
        (("Browser opened for Autodesk login." if opened else "Could not auto-open browser - copy the URL from the next step.")
         + "\n\nYou have %d seconds.\n"
         "Callback must be:\n%s")
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


DISCIPLINE_FULL = {
    "AR": "ARCHITECTURE", "ST": "STRUCTURAL", "CV": "CIVIL", "CW": "CIVIL WATER",
    "EE": "ELECTRICAL", "ME": "MECHANICAL", "MH": "MECHANICAL - HVAC", "PD": "PUBLIC HEALTH",
    "FP": "FIRE PROTECTION", "QS": "QUANTITY SURVEYOR", "PE": "PROCESS ENGINEER",
    "HG": "ROADS & HIGHWAYS - GEOMETRICS", "YC": "CONTROLS ENGINEER", "YS": "SECURITY SPECIALIST",
    "IM": "INFORMATION MANAGER", "DM": "DOCUMENT MANAGER", "DTL": "DELIVERY TEAM LEAD",
    "PDM": "PROJECT DELIVERY MANAGER",
}

def discipline_full_name(code):
    c = (code or "").strip().upper()
    if not c:
        return ""
    if c in DISCIPLINE_FULL:
        return DISCIPLINE_FULL[c]
    if len(c) > 3:
        return c
    return DISCIPLINE_FULL.get(c, c)


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
    global SHARED_PARAM_FILE
    try:
        SHARED_PARAM_FILE = find_shared_param_file()
    except Exception:
        pass
    if not File.Exists(SHARED_PARAM_FILE):
        print("Shared param file missing:", SHARED_PARAM_FILE)
        try:
            info("Shared parameter file not found." + chr(10) + chr(10)
                 + "Copy ATA_ZZ_SharedParameters_MERGED.txt to:" + chr(10)
                 + " - same folder as script.py" + chr(10)
                 + " - or %APPDATA%\\Atana\\" + chr(10) + chr(10)
                 + "Looked at:" + chr(10) + str(SHARED_PARAM_FILE))
        except Exception:
            pass
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
    """Match ViewSheets whose SheetNumber equals the FULL plan document id.

    Example plan id:  MD6264-ATA-01-ZZ-DR-AR-1003
    Sheet number must be that full string (not only 'AR' or '1003').
    Role only filters which plan rows are considered.
    """
    sheets = list(FilteredElementCollector(doc).OfClass(ViewSheet))
    if not plan_rows:
        return []

    role_u = (role or "").strip().upper()
    plan_ids = []
    for r in plan_rows:
        if not isinstance(r, dict):
            continue
        did = (r.get("documentId") or r.get("number") or r.get("name") or "").strip()
        if not did:
            continue
        did_u = re.sub(r"\.(PDF|DWG|RVT|IFC)$", "", did.upper(), flags=re.I)
        if role_u:
            segs = [p for p in did_u.replace("_", "-").split("-") if p]
            if role_u not in segs:
                continue
        plan_ids.append(did_u)

    plan_set = set(plan_ids)
    matched = []
    seen = set()
    for s in sheets:
        try:
            num = re.sub(r"\.(PDF|DWG)$", "", (s.SheetNumber or "").strip().upper(), flags=re.I)
        except Exception:
            continue
        if not num or num in seen:
            continue
        # STRICT: full sheet number must equal full document id
        if num in plan_set:
            matched.append(s)
            seen.add(num)
    return matched


def create_or_update_print_set(doc, set_name, sheets):
    """Update (or create) a named sheet set and make it the current/selected set.

    Existing sets are NOT deleted. Views from `sheets` are assigned and SaveAs
    updates the named set. CurrentViewSheetSet is left selected (ticked).
    """
    if not sheets:
        return 0
    t = Transaction(doc, "Atana — publish set " + str(set_name))
    t.Start()
    try:
        from Autodesk.Revit.DB import PrintRange, ViewSet
        pm = doc.PrintManager
        try:
            pm.PrintRange = PrintRange.Select
        except Exception:
            pass
        vss = pm.ViewSheetSetting

        # Build view set of target sheets
        vs = ViewSet()
        count = 0
        for s in sheets:
            try:
                vs.Insert(s)
                count += 1
            except Exception:
                pass

        # Try load existing named set first (reuse), then assign views and save
        loaded = False
        try:
            # Some API versions: Open existing
            names = []
            try:
                for ss in FilteredElementCollector(doc).OfClass(__import__("Autodesk.Revit.DB", fromlist=["ViewSheetSet"]).ViewSheetSet):
                    names.append(ss.Name)
            except Exception:
                pass
            if set_name in names:
                try:
                    vss.Open(set_name)
                    loaded = True
                except Exception:
                    pass
        except Exception:
            pass

        try:
            vss.CurrentViewSheetSet.Views = vs
        except Exception as ex:
            print("assign views", ex)

        try:
            if loaded:
                try:
                    vss.Save()
                except Exception:
                    vss.SaveAs(set_name)
            else:
                vss.SaveAs(set_name)
        except Exception as ex:
            try:
                vss.SaveAs(set_name)
            except Exception as ex2:
                print("SaveAs set", ex2)

        # Attempt to leave this set as the in-session / selected set
        try:
            vss.Open(set_name)
        except Exception:
            pass

        t.Commit()
        return count
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
    """All planned deliverables from Revit sync JSON (every stage / team)."""
    rows = []
    for key in ("deliverables", "planRows", "allPlanRows", "sheetPlan"):
        block = pack.get(key)
        if isinstance(block, list) and block:
            rows.extend(block)
    sheets = pack.get("sheets") or {}
    if isinstance(sheets, dict):
        for key in ("plan", "allPlanned", "rows"):
            block = sheets.get(key)
            if isinstance(block, list) and block:
                rows.extend(block)
    sd = pack.get("stageDeliverables") or {}
    if isinstance(sd, dict):
        for stage, block in sd.items():
            if isinstance(block, dict):
                rows.extend(block.get("rows") or [])
            elif isinstance(block, list):
                rows.extend(block)
    # de-dupe by documentId / number
    seen = set()
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        k = str(r.get("documentId") or r.get("number") or r.get("name") or id(r))
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out

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

# ---------------------------------------------------------------------------
# Sheets (DR / SH) + Publish Set from plan JSON
# ---------------------------------------------------------------------------

def _sheet_number_from_row(row):
    for k in ("documentId", "Document ID", "number", "Number", "sheetNumber", "code", "name"):
        v = row.get(k) if isinstance(row, dict) else None
        if v:
            return str(v).strip()
    return ""


def _sheet_title_from_row(row):
    for k in ("description", "Description", "Document Title", "title", "Title", "name"):
        v = row.get(k) if isinstance(row, dict) else None
        if v:
            return str(v).strip()
    return ""


def _row_form(row):
    for k in ("form", "Form", "type", "Type", "documentType"):
        v = row.get(k) if isinstance(row, dict) else None
        if v:
            return str(v).strip().upper()
    # parse from document id e.g. ...-DR-... or ...-SH-...
    did = _sheet_number_from_row(row)
    parts = did.replace("_", "-").split("-")
    for p in parts:
        if p.upper() in ("DR", "SH"):
            return p.upper()
    return ""


def _row_role(row):
    for k in ("role", "Role", "discipline", "taskTeam", "Task Team"):
        v = row.get(k) if isinstance(row, dict) else None
        if v:
            return str(v).strip().upper()
    did = _sheet_number_from_row(row)
    parts = did.replace("_", "-").split("-")
    # typical: PROJ-ORIG-FUNC-...-ROLE-...
    if len(parts) >= 2:
        return parts[-2].upper() if len(parts) >= 6 else parts[1].upper()
    return ""


def _row_stage(row):
    for k in ("workStage", "Work Stage", "stage", "Stage"):
        v = row.get(k) if isinstance(row, dict) else None
        if v:
            return str(v).strip().upper()
    return ""


def parse_model_codes(path):
    """From model file name: project-orig-func-spatial-form-role-number → codes."""
    base = os.path.basename(path or "")
    base = re.sub(r"\.rvt$", "", base, flags=re.I)
    parts = [p for p in base.replace("_", "-").split("-") if p]
    out = {"project": "", "originator": "", "functional": "", "spatial": "", "form": "", "role": "", "number": ""}
    if len(parts) >= 6:
        out["project"] = parts[0].upper()
        out["originator"] = parts[1].upper()
        out["functional"] = parts[2].upper()
        out["spatial"] = parts[3].upper()
        out["form"] = parts[4].upper()
        out["role"] = parts[5].upper()
        if len(parts) >= 7:
            out["number"] = parts[6].upper()
    elif len(parts) >= 2:
        out["role"] = parts[-2].upper()
    return out


def _row_functional(row):
    for k in ("functional", "Functional", "functionalBreakdown", "Functional Breakdown", "volume", "Volume", "func"):
        v = row.get(k) if isinstance(row, dict) else None
        if v:
            return str(v).strip().upper()
    did = _sheet_number_from_row(row)
    parts = [p for p in did.replace("_", "-").split("-") if p]
    # PROJ-ORIG-FUNC-...
    if len(parts) >= 3:
        return parts[2].upper()
    return ""


def collect_plan_sheets(pack, role_code, functional_code=None, stage_code=None):
    """Match planned items by Task team (role) + functional breakdown from model name.
    No form filter — all planned deliverables for that team/func are candidates.
    """
    rows = extract_plan_rows(pack) or []
    # also merge pack.sheetPlan / pack.planSheets if present
    extra = pack.get("sheetPlan") or pack.get("planSheets") or pack.get("allPlanRows") or []
    if isinstance(extra, list):
        rows = list(rows) + [r for r in extra if r not in rows]

    role_code = (role_code or "").upper()
    role_full = discipline_full_name(role_code).upper()
    functional_code = (functional_code or "").upper()
    out = []
    seen = set()
    for r in rows:
        if not isinstance(r, dict):
            continue
        rrole = _row_role(r)
        rfunc = _row_functional(r)

        # Task team / role match
        role_ok = True
        if role_code:
            if rrole:
                role_ok = (
                    rrole == role_code
                    or rrole == role_full
                    or role_code in rrole
                    or rrole.startswith(role_code)
                    or role_full in rrole
                )
            # if row has no role, keep (will rely on functional)
        if not role_ok:
            continue

        # Functional breakdown match when both sides known
        if functional_code and rfunc:
            if rfunc != functional_code and functional_code not in rfunc and rfunc not in functional_code:
                continue

        num = _sheet_number_from_row(r)
        if not num:
            continue
        key = num.upper()
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "number": num,
            "title": _sheet_title_from_row(r) or num,
            "form": _row_form(r),
            "stage": _row_stage(r),
            "role": rrole,
            "functional": rfunc,
            "row": r,
        })
    return out



def existing_sheets_map(doc):
    """sheetNumber -> ViewSheet"""
    out = {}
    col = FilteredElementCollector(doc).OfClass(ViewSheet)
    for vs in col:
        try:
            out[str(vs.SheetNumber)] = vs
        except Exception:
            pass
    return out


def list_titleblocks(doc):
    """List loaded titleblock family symbols: [(name, symbol)]"""
    result = []
    col = FilteredElementCollector(doc).OfClass(FamilySymbol)
    for fs in col:
        try:
            cat = fs.Category
            if cat and cat.Id.IntegerValue == int(BuiltInCategory.OST_TitleBlocks):
                if not fs.IsActive:
                    try:
                        fs.Activate()
                    except Exception:
                        pass
                fam = fs.Family.Name if fs.Family else ""
                tname = ""
                try:
                    p = fs.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
                    tname = p.AsString() if p else ""
                except Exception:
                    try:
                        tname = fs.Name
                    except Exception:
                        tname = ""
                result.append(("%s : %s" % (fam, tname or "?"), fs))
        except Exception:
            continue
    return result


def pick_titleblock_symbol(doc):
    tbs = list_titleblocks(doc)
    if not tbs:
        info("No title block families loaded in this project.")
        return None
    names = [n for n, _ in tbs]
    if forms:
        try:
            choice = forms.SelectFromList.show(names, title="Title block for new sheets", multiselect=False)
            if not choice:
                return None
            for n, sym in tbs:
                if n == choice:
                    return sym
        except Exception:
            pass
    # fallback first
    return tbs[0][1]


def set_sheet_param(sheet, names, value):
    if not value:
        return False
    for name in names:
        try:
            p = sheet.LookupParameter(name)
            if p and not p.IsReadOnly and p.StorageType == StorageType.String:
                p.Set(str(value))
                return True
        except Exception:
            continue
    return False


def ensure_publish_set(doc, set_name, sheet_ids):
    """Create/update a ViewSheetSet named set_name and add sheets. Returns message."""
    # ViewSheetSet via PrintManager
    try:
        pm = doc.PrintManager
        pm.PrintRange = PrintRange.Select
        vsns = pm.ViewSheetSetting
        # find existing
        existing = None
        it = vsns.GetSheetSetNames() if False else None
    except Exception:
        pass
    # Use ViewSheetSet collector
    try:
        from Autodesk.Revit.DB import ViewSheetSet, PrintManager, PrintRange
    except Exception:
        return "Publish set API limited in this Revit version."

    try:
        pm = doc.PrintManager
        pm.PrintRange = PrintRange.Select
        vss = pm.ViewSheetSetting
        # Try open existing set
        created = False
        try:
            # InAvailableSheetSets
            names = []
            for s in FilteredElementCollector(doc).OfClass(ViewSheetSet):
                names.append(s.Name)
                if s.Name == set_name:
                    # cannot easily edit via collector set; use ViewSheetSetting
                    pass
        except Exception:
            pass

        # Save current as named set after selecting views
        # Select sheets in ViewSheetSetting is complex in API
        # Alternative: create ViewSheetSet element - restricted
        return "Publish set '%s' — add sheets manually if not applied (API limits)." % set_name
    except Exception as ex:
        return "Publish set: " + str(ex)



def sheet_picker_form(plan_items, existing_map, titleblock_names):
    """WinForms: checkboxes for create/update sheets + title block combo.
    Returns dict {create: [items], update: [(item,vs)], titleblock_name: str} or None.
    """
    form = Form()
    form.Text = "Atana — Sheet sync"
    form.Width = 720
    form.Height = 560
    form.StartPosition = FormStartPosition.CenterScreen
    try:
        form.FormBorderStyle = FormBorderStyle.FixedDialog
    except Exception:
        pass
    form.MaximizeBox = False
    form.MinimizeBox = False

    result = {"ok": False, "create": [], "update": [], "tb": None}

    hdr = Label()
    hdr.Text = "Select sheets to create or update. Tick items to include."
    hdr.Left = 12
    hdr.Top = 10
    hdr.Width = 680
    hdr.Height = 22

    lbl_new = Label()
    lbl_new.Text = "Missing in model (create):"
    lbl_new.Left = 12
    lbl_new.Top = 36
    lbl_new.Width = 340

    cl_new = CheckedListBox()
    cl_new.Left = 12
    cl_new.Top = 58
    cl_new.Width = 340
    cl_new.Height = 280
    cl_new.CheckOnClick = True

    lbl_ex = Label()
    lbl_ex.Text = "Already in model (update title):"
    lbl_ex.Left = 368
    lbl_ex.Top = 36
    lbl_ex.Width = 330

    cl_ex = CheckedListBox()
    cl_ex.Left = 368
    cl_ex.Top = 58
    cl_ex.Width = 330
    cl_ex.Height = 280
    cl_ex.CheckOnClick = True

    # Build lists
    create_items = []
    update_items = []
    for item in plan_items:
        num = item.get("number") or ""
        title = item.get("title") or ""
        # Exact full sheet number only (document id == sheet number)
        match = existing_map.get(num) or existing_map.get(num.upper()) or existing_map.get(num.lower())
        if not match:
            for k, vs in existing_map.items():
                if k and num and k.upper() == num.upper():
                    match = vs
                    break
        label = "%s  |  %s" % (num, title)
        if match:
            update_items.append((item, match, label))
            idx = cl_ex.Items.Add(label)
            # default checked if title differs
            try:
                cur = match.Name or ""
            except Exception:
                cur = ""
            if title and cur != title:
                cl_ex.SetItemChecked(idx, True)
            else:
                cl_ex.SetItemChecked(idx, False)
        else:
            create_items.append((item, label))
            idx = cl_new.Items.Add(label)
            cl_new.SetItemChecked(idx, True)  # default all new selected

    lbl_tb = Label()
    lbl_tb.Text = "Title block for NEW sheets (bulk apply):"
    lbl_tb.Left = 12
    lbl_tb.Top = 350
    lbl_tb.Width = 400

    cmb = ComboBox()
    cmb.Left = 12
    cmb.Top = 372
    cmb.Width = 500
    # DropDownStyle: IronPython/Revit host only accepts 0; leave default
    for n in (titleblock_names or []):
        cmb.Items.Add(n)
    if cmb.Items.Count > 0:
        cmb.SelectedIndex = 0

    btn_all = Button()
    btn_all.Text = "Select all"
    btn_all.Left = 12
    btn_all.Top = 410
    btn_all.Width = 100
    def sel_all(s, e):
        for i in range(cl_new.Items.Count):
            cl_new.SetItemChecked(i, True)
        for i in range(cl_ex.Items.Count):
            cl_ex.SetItemChecked(i, True)
    btn_all.Click += sel_all

    btn_none = Button()
    btn_none.Text = "Select none"
    btn_none.Left = 120
    btn_none.Top = 410
    btn_none.Width = 100
    def sel_none(s, e):
        for i in range(cl_new.Items.Count):
            cl_new.SetItemChecked(i, False)
        for i in range(cl_ex.Items.Count):
            cl_ex.SetItemChecked(i, False)
    btn_none.Click += sel_none

    summary = Label()
    summary.Text = "New: %d   Existing: %d" % (len(create_items), len(update_items))
    summary.Left = 240
    summary.Top = 416
    summary.Width = 300

    def on_ok(s, e):
        result["ok"] = True
        result["create"] = []
        for i in range(cl_new.Items.Count):
            if cl_new.GetItemChecked(i):
                result["create"].append(create_items[i][0])
        result["update"] = []
        for i in range(cl_ex.Items.Count):
            if cl_ex.GetItemChecked(i):
                result["update"].append((update_items[i][0], update_items[i][1]))
        if cmb.SelectedIndex >= 0:
            result["tb"] = str(cmb.Items[cmb.SelectedIndex])
        form.DialogResult = DR.OK
        form.Close()

    def on_cancel(s, e):
        result["ok"] = False
        form.DialogResult = DR.Cancel
        form.Close()

    btn_ok = Button()
    btn_ok.Text = "Create / Update selected"
    btn_ok.Left = 420
    btn_ok.Top = 470
    btn_ok.Width = 170
    btn_ok.Height = 32
    btn_ok.Click += on_ok

    btn_cancel = Button()
    btn_cancel.Text = "Skip sheets"
    btn_cancel.Left = 600
    btn_cancel.Top = 470
    btn_cancel.Width = 100
    btn_cancel.Height = 32
    btn_cancel.Click += on_cancel

    form.Controls.Add(hdr)
    form.Controls.Add(lbl_new)
    form.Controls.Add(cl_new)
    form.Controls.Add(lbl_ex)
    form.Controls.Add(cl_ex)
    form.Controls.Add(lbl_tb)
    form.Controls.Add(cmb)
    form.Controls.Add(btn_all)
    form.Controls.Add(btn_none)
    form.Controls.Add(summary)
    form.Controls.Add(btn_ok)
    form.Controls.Add(btn_cancel)
    form.AcceptButton = btn_ok
    form.CancelButton = btn_cancel
    form.ShowDialog()
    if not result["ok"]:
        return None
    return result


def sync_sheets_ui(doc, pack, role, stage_code, designed_by, checked_by, functional_code=None):
    """Checkbox UI: select sheets to create/update, pick title block, write TTM/Peer."""
    plan = collect_plan_sheets(pack, role, functional_code=functional_code, stage_code=stage_code)
    if not plan:
        NL = chr(10)
        msg = (
            "No planned sheets found in the JSON for this model." + NL + NL
            + "Role (task team): %s" + NL
            + "Functional: %s" + NL + NL
            + "Continue without sheet sync?"
        ) % (discipline_full_name(role) or role or "(unknown)", functional_code or "(any)")
        if not confirm(msg):
            return
        info("Sheet sync skipped.")
        return

    # Titleblock list
    tb_list = list_titleblocks(doc)  # [(name, symbol), ...]
    tb_names = [n for n, _ in tb_list]
    tb_map = dict(tb_list)
    existing = existing_sheets_map(doc)

    # Intro confirm
    NL = chr(10)
    intro = (
        "Sheet sync" + NL + NL
        + "Role: %s" + NL
        + "Functional: %s" + NL
        + "Planned matches: %d" + NL + NL
        + "Yes = open sheet picker (tick boxes + title block)" + NL
        + "No = skip"
    ) % (
        discipline_full_name(role) or role or "?",
        functional_code or "(any)",
        len(plan),
    )
    if not confirm(intro):
        return

    picked = sheet_picker_form(plan, existing, tb_names)
    if not picked:
        info("Sheet sync cancelled.")
        return

    to_create = picked.get("create") or []
    to_update = picked.get("update") or []
    tb_name = picked.get("tb")
    tb = tb_map.get(tb_name) if tb_name else None
    if to_create and tb is None:
        # try first available
        if tb_list:
            tb = tb_list[0][1]
            tb_name = tb_list[0][0]
        else:
            info("No title block loaded in this project.\\nLoad a title block family first, then re-run sheet sync.")
            to_create = []

    if not to_create and not to_update:
        info("No sheets selected.")
        return

    created = 0
    updated = 0
    failed = []
    t = Transaction(doc, "Atana — sheets from plan")
    t.Start()
    try:
        for item, vs in to_update:
            try:
                title = item.get("title") or ""
                if title and vs.Name != title:
                    vs.Name = title[:256]
                    updated += 1
                set_sheet_param(vs, TITLEBLOCK_DESIGNED, designed_by)
                set_sheet_param(vs, TITLEBLOCK_CHECKED, checked_by)
            except Exception as ex:
                failed.append("update %s: %s" % (item.get("number"), ex))
        for item in to_create:
            try:
                vs = ViewSheet.Create(doc, tb.Id)
                # Full ISO document id as sheet number (e.g. MD6264-ATA-01-ZZ-DR-AR-1003)
                raw = item.get("number") or ""
                if item.get("row"):
                    raw = item["row"].get("documentId") or item["row"].get("number") or raw
                num = re.sub(r"\.(pdf|dwg)$", "", str(raw).strip(), flags=re.I)[:64]
                title = (item.get("title") or num)[:256]
                vs.SheetNumber = num
                vs.Name = title
                set_sheet_param(vs, TITLEBLOCK_DESIGNED, designed_by)
                set_sheet_param(vs, TITLEBLOCK_CHECKED, checked_by)
                created += 1
            except Exception as ex:
                failed.append("create %s: %s" % (item.get("number"), ex))
        t.Commit()
    except Exception as ex:
        try:
            t.RollBack()
        except Exception:
            pass
        info("Sheet transaction failed:\\n%s" % ex)
        return

    # Publish set name from work stage
    sn = stage_code or extract_stage(pack) or "S1"
    sn_u = str(sn).upper().replace(" ", "")
    if sn_u.startswith("S") and not sn_u.startswith("SW"):
        pub_name = "SW" + sn_u.lstrip("S")
    else:
        pub_name = sn_u
    pub_msg = ensure_publish_set(doc, pub_name, [])

    lines = [
        "Sheets complete.",
        "",
        "Created: %d" % created,
        "Titles updated: %d" % updated,
        "Title block: %s" % (tb_name or "(n/a)"),
        "TTM (Designed By): %s" % (designed_by or "(none)"),
        "Peer (Checked By): %s" % (checked_by or "(none)"),
        "Publish set target: %s" % pub_name,
        pub_msg or "",
    ]
    if failed:
        lines.append("")
        lines.append("Issues:")
        lines.extend(failed[:8])
    info_lines(lines)



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
        "ATA_ZZ_ProjectDiscipline": discipline_full_name(role) or discipline_full_name(pi_src.get("ATA_ZZ_ProjectDiscipline")) or discipline_full_name(pi_src.get("discipline")) or "",
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
        lines = ["✓  Review project information differences\n"]
        lines.append("Values in Revit will be updated to match the Atana pack:\n")
        for k, cur, new_v in mismatches:
            lines.append(u"  ✓ {}:".format(k))
            lines.append(u"      now:  {}".format(cur if cur else "(empty)"))
            lines.append(u"      pack: {}".format(new_v))
        lines.append("")
        lines.append("Apply all updates?")
        if confirm_lines(lines):
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

    # Sheet create/update (DR/SH) for this model role
    try:
        mcodes = parse_model_codes(model_path(doc) if "model_path" in dir() else (doc.PathName if doc else ""))
        sync_sheets_ui(doc, pack, role, stage_code, designed_by, checked_by, functional_code=mcodes.get("functional"))
    except Exception as ex:
        info("Sheet sync error:\n" + str(ex))


    # Globals
    globals_map = {
        "GLOBAL_ZZ_ClientContractNumber": desired_pi.get("ATA_ZZ_ClientContractNumber"),
        "GLOBAL_ZZ_ProjectDiscipline": desired_pi.get("ATA_ZZ_ProjectDiscipline") or discipline_full_name(role),
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
        msg = (
            "Publish Set: " + str(set_name) + chr(10) + chr(10)
            + "Sheets in model with FULL number matching plan document id: "
            + str(len(matched)) + chr(10)
            + "Role filter: " + str(role or "all") + chr(10) + chr(10)
            + "Add these sheets to the publish set?" + chr(10)
            + "(Existing set is kept and updated — not replaced.)"
        )
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
