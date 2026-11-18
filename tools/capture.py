"""Headless visual QA with the Chrome DevTools Protocol.

Usage: python tools/capture.py [outdir]
Requires a local Chrome install. Starts its own headless instance.
"""

import base64
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.parse
import urllib.request

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9223
BASE = "http://127.0.0.1:8000/"
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("TEMP", "."), "cookie-qa")
os.makedirs(OUT, exist_ok=True)
PROFILE = os.path.join(os.environ.get("TEMP", "."), "opencode", "chrome-cdp-profile")


class CDP:
    def __init__(self, ws_url):
        parsed = urllib.parse.urlparse(ws_url)
        self.sock = socket.create_connection((parsed.hostname, parsed.port), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET {parsed.path}{('?' + parsed.query) if parsed.query else ''} HTTP/1.1\r\n"
            f"Host: {parsed.hostname}:{parsed.port}\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(request.encode())
        response = b""
        while b"\r\n\r\n" not in response:
            response += self.sock.recv(4096)
        if b"101" not in response.split(b"\r\n", 1)[0]:
            raise RuntimeError("websocket handshake failed: " + response.split(b"\r\n")[0].decode(errors="replace"))
        self.msg_id = 0
        self.events = []

    def _send_frame(self, payload):
        data = payload.encode()
        header = bytearray([0x81])
        length = len(data)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", length)
        mask = os.urandom(4)
        header += mask
        masked = bytes(byte ^ mask[i % 4] for i, byte in enumerate(data))
        self.sock.sendall(bytes(header) + masked)

    def _read_exact(self, count):
        data = b""
        while len(data) < count:
            chunk = self.sock.recv(count - len(data))
            if not chunk:
                raise RuntimeError("socket closed")
            data += chunk
        return data

    def _read_frame(self):
        first, second = self._read_exact(2)
        opcode = first & 0x0F
        length = second & 0x7F
        if length == 126:
            length = struct.unpack(">H", self._read_exact(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._read_exact(8))[0]
        masked = second & 0x80
        mask = self._read_exact(4) if masked else b""
        payload = self._read_exact(length)
        if masked:
            payload = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
        if opcode == 0x9:  # ping
            self.sock.sendall(bytes([0x8A, 0x80]) + os.urandom(4))
            return ""
        if opcode == 0x8:
            raise RuntimeError("websocket closed by browser")
        return payload.decode(errors="replace")

    def call(self, method, params=None):
        self.msg_id += 1
        message_id = self.msg_id
        self._send_frame(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self._read_frame())
            if message.get("id") == message_id:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message.get("result", {})
            if "method" in message:
                self.events.append(message)

    def evaluate(self, expression):
        result = self.call("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        })
        return result.get("result", {}).get("value")

    def shot(self, filename, full=False):
        params = {"format": "png", "captureBeyondViewport": bool(full)}
        if full:
            metrics = self.call("Page.getLayoutMetrics")
            size = metrics.get("cssContentSize") or metrics.get("contentSize")
            params["clip"] = {
                "x": 0, "y": 0,
                "width": size["width"],
                "height": size["height"],
                "scale": 1,
            }
        data = self.call("Page.captureScreenshot", params)["data"]
        path = os.path.join(OUT, filename)
        with open(path, "wb") as handle:
            handle.write(base64.b64decode(data))
        print("shot", path)


def wait_for_port():
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1) as response:
                return json.load(response)
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Chrome remote debugging did not start")


def main():
    subprocess.Popen([
        CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFILE}",
        "--window-size=1440,1000", "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wait_for_port()
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list") as response:
        tabs = json.load(response)
    page = next(tab for tab in tabs if tab.get("type") == "page")
    cdp = CDP(page["webSocketDebuggerUrl"])
    cdp.call("Page.enable")
    cdp.call("Runtime.enable")

    def reset():
        cdp.evaluate("localStorage.clear(); location.reload()")
        time.sleep(2.0)

    cdp.call("Page.navigate", {"url": BASE})
    time.sleep(2.2)
    cdp.evaluate("localStorage.clear(); location.reload()")
    time.sleep(2.2)

    # full page, morning Arabic
    cdp.shot("01-morning-ar-full.png", full=True)

    # key sections, morning Arabic
    for name, selector in (("about", "#about"), ("cookies", "#cookies"), ("best", "#best"),
                           ("addons", "#addons"), ("reviews", "#reviews"),
                           ("offers", "#offers"), ("contact", "#contact"), ("footer", "#footer")):
        cdp.evaluate(
            "(() => { const el = document.querySelector(%r);"
            " window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 82); })()" % selector
        )
        time.sleep(1.15)
        cdp.shot(f"02-{name}-ar.png")

    # cart flow
    cdp.evaluate("document.querySelector('#productGrid [data-add]').click()")
    time.sleep(0.4)
    cdp.evaluate("document.querySelector('#cartBtn').click()")
    time.sleep(0.7)
    cdp.shot("03-cart-ar.png")

    # evening Arabic
    cdp.evaluate("document.querySelector('#cartClose').click()")
    cdp.evaluate("document.querySelector('#modeSwitch').click()")
    time.sleep(0.9)
    cdp.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.4)
    cdp.shot("04-evening-ar.png")

    # English morning
    cdp.evaluate("document.querySelector('#modeSwitch').click()")
    time.sleep(0.7)
    cdp.evaluate("document.querySelector('#langBtn').click()")
    time.sleep(0.7)
    cdp.shot("05-morning-en.png")

    # English evening
    cdp.evaluate("document.querySelector('#modeSwitch').click()")
    time.sleep(0.9)
    cdp.shot("06-evening-en.png")

    # mobile morning Arabic
    cdp.evaluate("document.querySelector('#langBtn').click()")
    cdp.evaluate("document.querySelector('#modeSwitch').click()")
    cdp.call("Emulation.setDeviceMetricsOverride", {
        "width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True,
    })
    cdp.evaluate("window.scrollTo(0, 0); localStorage.clear();")
    time.sleep(0.5)
    cdp.call("Page.navigate", {"url": BASE})
    time.sleep(2.0)
    cdp.shot("07-mobile-ar.png")

    # checkout confirmation
    cdp.evaluate("document.querySelector('#productGrid [data-add]').click()")
    time.sleep(0.3)
    cdp.evaluate("document.querySelector('#cartBtn').click()")
    time.sleep(0.5)
    cdp.evaluate("document.querySelector('#checkoutBtn').click()")
    time.sleep(0.8)
    cdp.shot("08-success-ar-mobile.png")

    errors = [e for e in cdp.events if e.get("method") == "Runtime.exceptionThrown"]
    print("exceptions:", len(errors))
    for error in errors:
        details = error.get("params", {}).get("exceptionDetails", {})
        print(" -", details.get("text"), details.get("exception", {}).get("description", ""))

    # restore desktop for any manual checks
    print("output:", OUT)


if __name__ == "__main__":
    main()
