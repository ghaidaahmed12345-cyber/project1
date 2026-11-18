"""Functional smoke tests for Cookie Nook, driven through Chrome DevTools.

Run: python tools/qa_check.py
"""

import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture import CDP, wait_for_port  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9223
BASE = "http://127.0.0.1:8000/"
PROFILE = os.path.join(os.environ.get("TEMP", "."), "opencode", "chrome-qa-profile")
OUT = os.path.join(os.environ.get("TEMP", "."), "cookie-qa")
os.makedirs(OUT, exist_ok=True)

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print("PASS", label)
    else:
        failed += 1
        print("FAIL", label, detail)


def main():
    process = subprocess.Popen([
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

    def js(expression):
        return cdp.evaluate(expression)

    cdp.call("Page.navigate", {"url": BASE})
    time.sleep(2.0)
    js("localStorage.clear(); location.reload()")
    time.sleep(2.0)

    # --- initial state -----------------------------------------------------
    check("Arabic is the default language", js("document.documentElement.lang") == "ar")
    check("RTL is the default direction", js("document.documentElement.dir") == "rtl")
    check("Morning is the default theme", js("document.documentElement.dataset.theme") == "morning")
    check("Arabic morning greeting", "صباح الخير" in (js("document.querySelector('#greetingText').textContent") or ""))
    check("Six products rendered", js("document.querySelectorAll('#productGrid .product-card').length") == 6)
    check("Three best sellers rendered", js("document.querySelectorAll('#bestGrid .best-card').length") == 3)
    check("Six add-ons rendered", js("document.querySelectorAll('#addonGrid .addon-card').length") == 6)
    check("Cart starts empty", js("document.querySelector('#cartList').children.length") == 0)
    check("Cart badge starts hidden", js("getComputedStyle(document.querySelector('#cartCount')).display") == "none")

    # --- theme -------------------------------------------------------------
    js("document.querySelector('#modeSwitch').click()")
    time.sleep(0.7)
    check("Theme switches to evening", js("document.documentElement.dataset.theme") == "evening")
    check("Evening greeting shown", "أحلامًا حلوة" in (js("document.querySelector('#greetingText').textContent") or ""))
    check("Evening persisted", js("localStorage.getItem('cookienook.theme')") == "evening")
    check("Switch is checked", js("document.querySelector('#modeSwitch').getAttribute('aria-checked')") == "true")

    # --- language ----------------------------------------------------------
    js("document.querySelector('#langBtn').click()")
    time.sleep(0.5)
    check("Language switches to English", js("document.documentElement.lang") == "en")
    check("Direction switches to LTR", js("document.documentElement.dir") == "ltr")
    check("English nav label", js("document.querySelector('[data-i18n=\"nav.home\"]').textContent") == "Home")
    check("English evening greeting", "Sweet Dreams" in (js("document.querySelector('#greetingText').textContent") or ""))
    check("Products re-rendered in English", "Classic Chocolate Chip" in js("document.querySelector('#productGrid').textContent"))
    check("Language persisted", js("localStorage.getItem('cookienook.lang')") == "en")
    check("Title translated", "Cookie Nook" in (js("document.title") or ""))

    # --- filters -----------------------------------------------------------
    js("document.querySelector('[data-filter=\"chocolate\"]').click()")
    time.sleep(0.4)
    check("Chocolate filter shows 2 products", js("document.querySelectorAll('#productGrid .product-card').length") == 2)
    check("Filter marked active", js("document.querySelector('[data-filter=\"chocolate\"]').getAttribute('aria-pressed')") == "true")
    js("document.querySelector('[data-filter=\"fruity\"]').click()")
    time.sleep(0.3)
    check("Fruity filter shows 1 product", js("document.querySelectorAll('#productGrid .product-card').length") == 1)
    js("document.querySelector('[data-filter=\"all\"]').click()")
    time.sleep(0.3)
    check("All filter restores 6 products", js("document.querySelectorAll('#productGrid .product-card').length") == 6)

    # --- cart --------------------------------------------------------------
    js("document.querySelector('#productGrid [data-add]').click()")
    time.sleep(0.4)
    check("Cart badge shows 1", js("document.querySelector('#cartCount').textContent") == "1")
    check("Cart line added", js("document.querySelectorAll('#cartList .cart-item').length") == 1)
    check("Subtotal is SAR 12", "12" in (js("document.querySelector('#cartSubtotal').textContent") or ""))
    check("Free delivery progress starts", "88" in (js("document.querySelector('#deliveryText').textContent") or ""))
    check("Cart persisted", len(json.loads(js("localStorage.getItem('cookienook.cart')") or "[]")) == 1)

    js("document.querySelector('#productGrid [data-add]').click()")
    time.sleep(0.4)
    check("Adding again merges line", js("document.querySelectorAll('#cartList .cart-item').length") == 1)
    check("Quantity becomes 2", js("document.querySelector('.qty span').textContent") == "2")
    check("Subtotal becomes 24", "24" in (js("document.querySelector('#cartSubtotal').textContent") or ""))

    js("document.querySelector('#cartBtn').click()")
    time.sleep(0.6)
    check("Cart drawer opens", js("document.querySelector('#cartDrawer').classList.contains('is-open')"))
    check("Drawer aria-hidden is false", js("document.querySelector('#cartDrawer').getAttribute('aria-hidden')") == "false")
    check("Body is locked", js("document.body.classList.contains('no-scroll')"))

    js("document.querySelector('[data-inc]').click()")
    time.sleep(0.4)
    check("Quantity increments to 3", js("document.querySelector('.qty span').textContent") == "3")
    js("document.querySelector('[data-dec]').click()")
    time.sleep(0.4)
    check("Quantity decrements to 2", js("document.querySelector('.qty span').textContent") == "2")

    # about / offers screenshots after scrolling (reveal + lazy images)
    js("document.querySelector('#cartClose').click()")
    time.sleep(0.4)
    js("(() => { const el = document.querySelector('#about'); window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 82); })()")
    time.sleep(1.2)
    cdp.shot("09-about-en.png")
    js("(() => { const el = document.querySelector('#cookies'); window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 82); })()")
    time.sleep(1.2)
    cdp.shot("10-cookies-en.png")
    js("(() => { const el = document.querySelector('#offers'); window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 82); })()")
    time.sleep(1.2)
    cdp.shot("11-offers-en.png")

    # copy code
    js("document.querySelector('#offers [data-copy]').click()")
    time.sleep(0.5)
    check("Copy toast appears", "copied" in (js("document.querySelector('#toasts').textContent") or "").lower())

    # favourites
    js("window.scrollTo(0,0)")
    js("document.querySelector('#productGrid [data-like]').click()")
    time.sleep(0.4)
    check("Like toggles on", js("document.querySelector('#productGrid [data-like]').classList.contains('is-liked')"))
    check("Like persisted", len(json.loads(js("localStorage.getItem('cookienook.likes')") or "[]")) == 1)
    js("document.querySelector('#productGrid [data-like]').click()")
    time.sleep(0.3)
    check("Like can be removed", len(json.loads(js("localStorage.getItem('cookienook.likes')") or "[]")) == 0)

    # contact form validation + success
    js("document.querySelector('#contactForm').requestSubmit()")
    time.sleep(0.3)
    check("Empty contact form is invalid", js("document.querySelector('#contactName').classList.contains('is-invalid')"))
    check("Invalid toast appears", "check" in (js("document.querySelector('#toasts').textContent") or "").lower())

    js("""
      document.querySelector('#contactName').value = 'QA Cookie';
      document.querySelector('#contactEmail').value = 'qa@example.com';
      document.querySelector('#contactMessage').value = 'A little note about cookies.';
      document.querySelector('#contactForm').requestSubmit();
    """)
    time.sleep(0.4)
    check("Valid contact form sends", "arrived" in (js("document.querySelector('#toasts').textContent") or "").lower())
    check("Contact form resets", js("document.querySelector('#contactName').value") == "")

    # newsletter
    js("document.querySelector('#newsletterEmail').value = 'bad'; document.querySelector('#newsletterForm').requestSubmit()")
    time.sleep(0.3)
    check("Bad newsletter email is invalid", js("document.querySelector('#newsletterEmail').classList.contains('is-invalid')"))
    js("document.querySelector('#newsletterEmail').value = 'qa@example.com'; document.querySelector('#newsletterForm').requestSubmit()")
    time.sleep(0.4)
    check("Newsletter subscribes", "family" in (js("document.querySelector('#toasts').textContent") or "").lower())

    # checkout + success modal
    js("document.querySelector('#cartBtn').click()")
    time.sleep(0.5)
    js("document.querySelector('#checkoutBtn').click()")
    time.sleep(0.8)
    check("Success modal opens", js("document.querySelector('#successModal').classList.contains('is-open')"))
    check("Order number generated", "#CN-" in (js("document.querySelector('#orderNumber').textContent") or ""))
    check("Cart clears after checkout", js("document.querySelectorAll('#cartList .cart-item').length") == 0)
    check("Cart storage clears", json.loads(js("localStorage.getItem('cookienook.cart')") or "[]") == [])
    cdp.shot("12-success-en.png")
    js("document.querySelector('#successDone').click()")
    time.sleep(0.5)
    check("Success modal closes", not js("document.querySelector('#successModal').classList.contains('is-open')"))

    # persistence across reload
    js("localStorage.setItem('cookienook.lang','en'); localStorage.setItem('cookienook.theme','evening'); location.reload()")
    time.sleep(2.0)
    check("Language persists on reload", js("document.documentElement.lang") == "en")
    check("Theme persists on reload", js("document.documentElement.dataset.theme") == "evening")

    # mobile navigation
    cdp.call("Emulation.setDeviceMetricsOverride", {
        "width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True,
    })
    js("location.reload()")
    time.sleep(2.0)
    check("Mobile nav starts closed", not js("document.querySelector('#mainNav').classList.contains('is-open')"))
    js("document.querySelector('#navToggle').click()")
    time.sleep(0.4)
    check("Mobile nav opens", js("document.querySelector('#mainNav').classList.contains('is-open')"))
    check("Nav toggle reports expanded", js("document.querySelector('#navToggle').getAttribute('aria-expanded')") == "true")
    cdp.shot("13-mobile-nav-en.png")
    js("document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', bubbles:true}))")
    time.sleep(0.3)
    check("Escape closes mobile nav", not js("document.querySelector('#mainNav').classList.contains('is-open')"))

    # countdown running
    first = js("document.querySelector('#cdSeconds').textContent")
    time.sleep(1.2)
    second = js("document.querySelector('#cdSeconds').textContent")
    check("Countdown ticks", first != second, f"{first} -> {second}")

    exceptions = [event for event in cdp.events if event.get("method") == "Runtime.exceptionThrown"]
    check("No uncaught exceptions", len(exceptions) == 0, str(exceptions[:1]))

    print(f"\n{passed} passed, {failed} failed")
    print("screenshots:", OUT)

    try:
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, timeout=10)
    except Exception:
        pass


if __name__ == "__main__":
    main()
