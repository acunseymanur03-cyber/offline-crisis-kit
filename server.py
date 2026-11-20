#!/usr/bin/env python3
"""Offline Crisis Kit

A zero-dependency local web server that provides:
  * a chat room for everyone connected to the same Wi-Fi / phone hotspot
  * offline reference pages (first aid, water, communication, power)

Works with no internet. Python 3.7+ standard library only.

Run:  python server.py        (then open http://<phone-ip>:8080 from any device)
"""
import html
import json
import os
import re
import socket
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

import pages

BASE = os.path.dirname(os.path.abspath(__file__))
EXTRA_DIR = os.path.join(BASE, "content")          # optional extra .md pages
LOG_FILE = os.path.join(BASE, "chat_log.jsonl")
PORT = int(os.environ.get("PORT", "8080"))
MAX_TEXT = 500
MAX_NAME = 24
MAX_MESSAGES = 1000
MIN_SECONDS_BETWEEN_POSTS = 1.0

_lock = threading.Lock()
_messages = []          # list of dicts: id, ts, name, text, help
_next_id = 1
_last_post = {}         # ip -> timestamp


# ----------------------------------------------------------------- chat store
def _load_log():
    global _next_id
    if not os.path.exists(LOG_FILE):
        return
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    m = json.loads(line)
                except ValueError:
                    continue
                _messages.append(m)
        del _messages[:-MAX_MESSAGES]
        if _messages:
            _next_id = _messages[-1]["id"] + 1
    except OSError:
        pass


def add_message(name, text, is_help):
    global _next_id
    with _lock:
        msg = {
            "id": _next_id,
            "ts": int(time.time()),
            "name": name,
            "text": text,
            "help": bool(is_help),
        }
        _next_id += 1
        _messages.append(msg)
        del _messages[:-MAX_MESSAGES]
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        except OSError:
            pass  # storage trouble must never break chat
        return msg


def messages_after(after_id):
    with _lock:
        return [m for m in _messages if m["id"] > after_id]


# ----------------------------------------------------------------- rendering
def render_markdown(text):
    """Tiny, safe renderer: escapes everything first, then applies syntax."""
    out, in_list = [], False

    def inline(s):
        s = html.escape(s)
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    for raw in text.strip().splitlines():
        line = raw.rstrip()
        is_item = line.startswith("- ") or re.match(r"^\d+\.\s", line)
        if in_list and not is_item:
            out.append("</ul>")
            in_list = False
        if not line:
            continue
        if line.startswith("## "):
            out.append("<h2>%s</h2>" % inline(line[3:]))
        elif line.startswith("# "):
            out.append("<h1>%s</h1>" % inline(line[2:]))
        elif is_item:
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = line[2:] if line.startswith("- ") else re.sub(r"^\d+\.\s", "", line)
            out.append("<li>%s</li>" % inline(item))
        else:
            out.append("<p>%s</p>" % inline(line))
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


STYLE = """
body{font-family:system-ui,sans-serif;margin:0;background:#f5f5f2;color:#1b1b1b;line-height:1.5}
header{background:#1d3b2f;color:#fff;padding:12px 16px}
header a{color:#fff;text-decoration:none;font-weight:600}
main{padding:16px;max-width:720px;margin:0 auto}
a.card{display:block;background:#fff;border-radius:10px;padding:14px 16px;margin:10px 0;
 text-decoration:none;color:inherit;border:1px solid #ddd}
h1{font-size:1.4rem} h2{font-size:1.1rem;margin-top:1.4em}
.note{font-size:.85rem;color:#555}
"""


def page_shell(title, body):
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>%s</title><style>%s</style></head><body>"
        "<header><a href='/'>Offline Crisis Kit</a></header><main>%s</main></body></html>"
        % (html.escape(title), STYLE, body)
    )


def all_pages():
    """Built-in pages plus optional .md files from ./content/."""
    result = dict(pages.PAGES)
    if os.path.isdir(EXTRA_DIR):
        for fn in sorted(os.listdir(EXTRA_DIR)):
            if fn.endswith(".md"):
                slug = re.sub(r"[^a-z0-9-]", "-", fn[:-3].lower())
                try:
                    with open(os.path.join(EXTRA_DIR, fn), encoding="utf-8") as f:
                        text = f.read()
                except OSError:
                    continue
                first = text.strip().splitlines()[0] if text.strip() else slug
                result[slug] = (first.lstrip("# ").strip(), text)
    return result


def home_page():
    cards = ["<a class='card' href='/chat'><strong>Local chat</strong><br>"
             "<span class='note'>Talk to everyone on this network. Flag urgent messages as HELP.</span></a>"]
    for slug, (title, _) in all_pages().items():
        cards.append("<a class='card' href='/info/%s'><strong>%s</strong></a>"
                     % (html.escape(slug), html.escape(title)))
    body = ("<h1>Works without internet</h1>" + "".join(cards) +
            "<p class='note'>Reference pages are a basic guide only. "
            "Contact official emergency services whenever you can.</p>")
    return page_shell("Offline Crisis Kit", body)


CHAT_PAGE = """<!doctype html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Local chat</title><style>
body{font-family:system-ui,sans-serif;margin:0;display:flex;flex-direction:column;height:100vh;background:#f5f5f2}
header{background:#1d3b2f;color:#fff;padding:12px 16px}header a{color:#fff;text-decoration:none;font-weight:600}
#log{flex:1;overflow-y:auto;padding:12px}
.m{background:#fff;border:1px solid #ddd;border-radius:10px;padding:8px 12px;margin:6px 0;word-wrap:break-word}
.m.help{background:#ffe9e7;border-color:#d33}
.meta{font-size:.75rem;color:#666}
form{display:flex;flex-wrap:wrap;gap:6px;padding:10px;background:#e9e9e4}
input[type=text]{flex:1 1 100px;padding:10px;font-size:1rem;border:1px solid #aaa;border-radius:8px}
#text{flex:3 1 200px}
button{padding:10px 16px;font-size:1rem;border:0;border-radius:8px;background:#1d3b2f;color:#fff}
label{display:flex;align-items:center;gap:4px;font-size:.9rem}
#status{font-size:.75rem;color:#a00;padding:0 12px}
</style></head><body>
<header><a href='/'>&larr; Offline Crisis Kit</a> &nbsp;|&nbsp; Local chat</header>
<div id='log'></div><div id='status'></div>
<form id='f'>
<input type='text' id='name' placeholder='Your name' maxlength='%(maxname)d'>
<input type='text' id='text' placeholder='Message' maxlength='%(maxtext)d' autocomplete='off'>
<label><input type='checkbox' id='help'> HELP</label>
<button type='submit'>Send</button></form>
<script>
var last = 0, log = document.getElementById('log'), status = document.getElementById('status');
var nameEl = document.getElementById('name');
try { nameEl.value = localStorage.getItem('ock_name') || ''; } catch (e) {}
function add(m) {
  var d = document.createElement('div'); d.className = 'm' + (m.help ? ' help' : '');
  var meta = document.createElement('div'); meta.className = 'meta';
  var t = new Date(m.ts * 1000);
  meta.textContent = (m.help ? 'HELP - ' : '') + m.name + '  ' + t.toLocaleTimeString();
  var body = document.createElement('div'); body.textContent = m.text;
  d.appendChild(meta); d.appendChild(body); log.appendChild(d);
}
function poll() {
  fetch('/api/messages?after=' + last).then(function (r) { return r.json(); }).then(function (data) {
    status.textContent = '';
    if (data.length) {
      var atBottom = log.scrollTop + log.clientHeight >= log.scrollHeight - 40;
      data.forEach(function (m) { add(m); last = Math.max(last, m.id); });
      if (atBottom) log.scrollTop = log.scrollHeight;
    }
  }).catch(function () { status.textContent = 'Connection lost, retrying...'; })
    .then(function () { setTimeout(poll, 2000); });
}
document.getElementById('f').addEventListener('submit', function (e) {
  e.preventDefault();
  var text = document.getElementById('text'), help = document.getElementById('help');
  if (!text.value.trim()) return;
  try { localStorage.setItem('ock_name', nameEl.value); } catch (e2) {}
  fetch('/api/send', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: nameEl.value, text: text.value, help: help.checked }) })
    .then(function (r) { if (!r.ok) throw new Error(); text.value = ''; help.checked = false; })
    .catch(function () { status.textContent = 'Message not sent. Try again.'; });
});
poll();
</script></body></html>""" % {"maxname": MAX_NAME, "maxtext": MAX_TEXT}


# ------------------------------------------------------------------- handler
class Handler(BaseHTTPRequestHandler):
    server_version = "OfflineCrisisKit/0.1"

    def log_message(self, fmt, *args):  # keep the console quiet and cheap
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        path = unquote(url.path)
        if path == "/":
            self._send(200, home_page())
        elif path == "/chat":
            self._send(200, CHAT_PAGE)
        elif path.startswith("/info/"):
            slug = path[len("/info/"):]
            entry = all_pages().get(slug)
            if entry:
                self._send(200, page_shell(entry[0], render_markdown(entry[1])))
            else:
                self._send(404, page_shell("Not found", "<h1>Page not found</h1>"))
        elif path == "/api/messages":
            try:
                after = int(parse_qs(url.query).get("after", ["0"])[0])
            except ValueError:
                after = 0
            self._send(200, json.dumps(messages_after(after)), "application/json")
        elif path == "/health":
            self._send(200, "ok", "text/plain")
        else:
            self._send(404, page_shell("Not found", "<h1>Page not found</h1>"))

    def do_POST(self):
        if urlparse(self.path).path != "/api/send":
            self._send(404, "not found", "text/plain")
            return
        ip = self.client_address[0]
        now = time.time()
        with _lock:
            if now - _last_post.get(ip, 0) < MIN_SECONDS_BETWEEN_POSTS:
                too_fast = True
            else:
                _last_post[ip] = now
                too_fast = False
        if too_fast:
            self._send(429, "slow down", "text/plain")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 4096:
                raise ValueError
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            text = str(data.get("text", "")).strip()[:MAX_TEXT]
            name = (str(data.get("name", "")).strip() or "Anonymous")[:MAX_NAME]
            if not text:
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            self._send(400, "bad request", "text/plain")
            return
        msg = add_message(name, text, data.get("help") is True)
        self._send(200, json.dumps(msg), "application/json")


# ---------------------------------------------------------------------- main
def local_addresses():
    """Best-effort list of this device's LAN addresses (works offline)."""
    addrs = set()
    try:  # no packets are sent; this only selects a local interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        addrs.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    for cmd in (["ip", "-4", "addr"], ["ifconfig"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=3).stdout
            addrs.update(re.findall(r"inet (?:addr:)?(\d+\.\d+\.\d+\.\d+)", out))
        except (OSError, subprocess.SubprocessError):
            continue
    return sorted(a for a in addrs if not a.startswith("127."))


def main():
    _load_log()
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("Offline Crisis Kit running. Open from any device on this network:")
    found = local_addresses()
    if found:
        for a in found:
            print("  http://%s:%d" % (a, PORT))
    else:
        print("  http://<this-device-ip>:%d   (find the IP with: ip addr  or  ifconfig)" % PORT)
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
