/* ============================================================
   Cookie Nook — interactions, language, theme, basket
   ============================================================ */
(function () {
  "use strict";

  const DATA = window.COOKIE_NOOK;
  if (!DATA) return;

  const { I18N, PRODUCTS, ADDONS, BEST } = DATA;

  const FREE_DELIVERY = 100;
  const MAX_QTY = 99;

  const STORE = {
    lang: "cookienook.lang",
    theme: "cookienook.theme",
    cart: "cookienook.cart",
    likes: "cookienook.likes",
    offerEnd: "cookienook.offerEnd"
  };

  const state = {
    lang: "ar",
    theme: "morning",
    filter: "all",
    cart: [],
    likes: new Set(),
    offerEnd: 0
  };

  /* ---------- Helpers ---------- */
  const $ = (selector, root) => (root || document).querySelector(selector);
  const $$ = (selector, root) => Array.prototype.slice.call((root || document).querySelectorAll(selector));

  const html = document.documentElement;
  const metaDescription = $('meta[name="description"]');
  const metaTheme = $('meta[name="theme-color"]');

  const header = $("#siteHeader");
  const nav = $("#mainNav");
  const navToggle = $("#navToggle");
  const modeSwitch = $("#modeSwitch");
  const modeLabel = $("#modeLabel");
  const langBtn = $("#langBtn");
  const langLabel = $("#langLabel");
  const cartBtn = $("#cartBtn");
  const cartCount = $("#cartCount");
  const greeting = $(".greeting");
  const greetingIcon = $("#greetingIcon");
  const greetingText = $("#greetingText");
  const productGrid = $("#productGrid");
  const bestGrid = $("#bestGrid");
  const addonGrid = $("#addonGrid");
  const cartDrawer = $("#cartDrawer");
  const cartClose = $("#cartClose");
  const cartEmpty = $("#cartEmpty");
  const cartList = $("#cartList");
  const cartFoot = $("#cartFoot");
  const deliveryText = $("#deliveryText");
  const deliveryFill = $("#deliveryFill");
  const cartSubtotal = $("#cartSubtotal");
  const checkoutBtn = $("#checkoutBtn");
  const cartBrowse = $("#cartBrowse");
  const drawerOverlay = $("#drawerOverlay");
  const successModal = $("#successModal");
  const successOverlay = $("#successOverlay");
  const successClose = $("#successClose");
  const successDone = $("#successDone");
  const orderNumber = $("#orderNumber");
  const toasts = $("#toasts");
  const confettiLayer = $("#confetti");
  const bgStars = $("#bgStars");
  const contactForm = $("#contactForm");
  const newsletterForm = $("#newsletterForm");
  const filtersBar = $(".filters");
  const cdDays = $("#cdDays");
  const cdHours = $("#cdHours");
  const cdMinutes = $("#cdMinutes");
  const cdSeconds = $("#cdSeconds");
  const navLinks = $$(".nav__link");
  const sections = ["home", "about", "cookies", "best", "addons", "offers", "contact"]
    .map((id) => document.getElementById(id))
    .filter(Boolean);

  let lastFocused = null;
  let ticking = false;

  function esc(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function icon(name) {
    return '<svg aria-hidden="true"><use href="#' + name + '"/></svg>';
  }

  function t(key, vars) {
    const dict = I18N[state.lang] || I18N.ar;
    let text = dict[key];
    if (text == null) text = I18N.en[key];
    if (text == null) return key;
    if (vars) {
      Object.keys(vars).forEach(function (name) {
        text = text.split("{" + name + "}").join(vars[name]);
      });
    }
    return text;
  }

  function formatNumber(value) {
    return Number(value).toLocaleString("en-US");
  }

  function money(value) {
    const amount = formatNumber(value);
    return state.lang === "ar" ? amount + " " + t("currency") : t("currency") + " " + amount;
  }

  function storageGet(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value == null ? fallback : value;
    } catch (error) {
      return fallback;
    }
  }

  function storageSet(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      /* storage may be unavailable — the page still works */
    }
  }

  function prefersReduced() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function findItem(id) {
    return PRODUCTS.find((product) => product.id === id) || ADDONS.find((addon) => addon.id === id);
  }

  function nameOf(item) {
    return item.name[state.lang] || item.name.en || item.name.ar;
  }

  function descriptionOf(item) {
    return item.desc[state.lang] || item.desc.en || item.desc.ar;
  }

  /* ---------- Toast ---------- */
  function toast(message) {
    if (!toasts) return;
    const element = document.createElement("div");
    element.className = "toast";
    element.innerHTML = icon("i-check") + "<span></span>";
    element.lastElementChild.textContent = message;
    toasts.appendChild(element);

    while (toasts.children.length > 3) {
      toasts.removeChild(toasts.firstElementChild);
    }

    window.setTimeout(function () {
      element.classList.add("is-out");
      window.setTimeout(function () {
        if (element.parentNode) element.parentNode.removeChild(element);
      }, 320);
    }, 2700);
  }

  /* ---------- Language ---------- */
  function applyLanguage(lang, options) {
    if (lang !== "en" && lang !== "ar") lang = "ar";
    state.lang = lang;

    html.lang = lang;
    html.dir = lang === "ar" ? "rtl" : "ltr";
    storageSet(STORE.lang, lang);

    document.title = t("meta.title");
    if (metaDescription) metaDescription.setAttribute("content", t("meta.description"));

    $$("[data-i18n]").forEach(function (element) {
      element.textContent = t(element.getAttribute("data-i18n"));
    });

    $$("[data-i18n-aria]").forEach(function (element) {
      element.setAttribute("aria-label", t(element.getAttribute("data-i18n-aria")));
    });

    $$("[data-i18n-alt]").forEach(function (element) {
      element.setAttribute("alt", t(element.getAttribute("data-i18n-alt")));
    });

    $$("[data-i18n-placeholder]").forEach(function (element) {
      element.setAttribute("placeholder", t(element.getAttribute("data-i18n-placeholder")));
    });

    if (langLabel) langLabel.textContent = lang === "ar" ? "EN" : "AR";
    if (langBtn) langBtn.setAttribute("aria-label", t("aria.lang"));

    $$("[data-copy]").forEach(function (element) {
      const code = element.getAttribute("data-copy");
      element.setAttribute("aria-label", t("aria.copy", { code: code }));
    });

    updateModeUI();
    updateNavState();
    renderProducts();
    renderBest();
    renderAddons();
    renderCart();

    if (!options || !options.silent) {
      document.body.classList.remove("lang-switching");
      void document.body.offsetWidth;
      document.body.classList.add("lang-switching");
    }
  }

  function toggleLanguage() {
    applyLanguage(state.lang === "ar" ? "en" : "ar");
  }

  /* ---------- Theme ---------- */
  function applyTheme(theme, animate) {
    state.theme = theme === "evening" ? "evening" : "morning";
    html.dataset.theme = state.theme;
    storageSet(STORE.theme, state.theme);

    if (metaTheme) {
      metaTheme.setAttribute("content", state.theme === "evening" ? "#251711" : "#FFF9F0");
    }

    updateModeUI();

    if (animate && greeting && !prefersReduced()) {
      greeting.classList.remove("is-pop");
      void greeting.offsetWidth;
      greeting.classList.add("is-pop");
    }
  }

  function toggleTheme() {
    applyTheme(state.theme === "morning" ? "evening" : "morning", true);
  }

  function updateModeUI() {
    const evening = state.theme === "evening";

    if (modeSwitch) {
      modeSwitch.setAttribute("aria-checked", String(evening));
      modeSwitch.setAttribute(
        "aria-label",
        t(evening ? "aria.switchMorning" : "aria.switchEvening")
      );
    }
    if (modeLabel) modeLabel.textContent = t(evening ? "mode.evening" : "mode.morning");
    if (greetingText) {
      greetingText.textContent = t(evening ? "hero.greetingEvening" : "hero.greetingMorning");
    }
    if (greetingIcon) {
      greetingIcon.innerHTML = icon(evening ? "i-moon" : "i-sun");
    }
  }

  /* ---------- Products ---------- */
  function badgeMarkup(badge) {
    if (!badge) return "";
    const map = {
      best: { className: "badge badge--best", icon: "i-star", key: "badge.best" },
      new: { className: "badge badge--new", icon: "i-sparkle", key: "badge.new" },
      limited: { className: "badge badge--limited", icon: "i-clock", key: "badge.limited" }
    };
    const entry = map[badge];
    if (!entry) return "";
    return (
      '<span class="' + entry.className + '">' +
      icon(entry.icon) +
      "<span>" + esc(t(entry.key)) + "</span></span>"
    );
  }

  function priceMarkup(price) {
    return (
      '<span class="price"><strong>' + esc(formatNumber(price)) + "</strong>" +
      "<small>" + esc(t("currency")) + "</small></span>"
    );
  }

  function likeButton(product) {
    const liked = state.likes.has(product.id);
    const name = nameOf(product);
    return (
      '<button class="like-btn' + (liked ? " is-liked" : "") + '" type="button" ' +
      'data-like="' + esc(product.id) + '" aria-pressed="' + String(liked) + '" ' +
      'aria-label="' + esc(t(liked ? "aria.unlike" : "aria.like", { name: name })) + '">' +
      icon("i-heart") + "</button>"
    );
  }

  function addButton(product, extraClass) {
    const name = nameOf(product);
    return (
      '<button class="add-btn ' + (extraClass || "") + '" type="button" ' +
      'data-add="' + esc(product.id) + '" aria-label="' +
      esc(t("aria.addToCart", { name: name })) + '">' +
      "<span>" + esc(t("common.add")) + "</span>" +
      '<span class="add-btn__icon">' + icon("i-plus") + "</span></button>"
    );
  }

  function renderProducts() {
    if (!productGrid) return;

    const list = state.filter === "all"
      ? PRODUCTS
      : PRODUCTS.filter((product) => product.category === state.filter);

    if (!list.length) {
      productGrid.innerHTML = '<p class="filter-empty">' + esc(t("filters.empty")) + "</p>";
      return;
    }

    productGrid.innerHTML = list.map(function (product, index) {
      const name = nameOf(product);
      const tags = (product.tags || []).map(function (tag) {
        return "<span>" + esc(tag[state.lang] || tag.en) + "</span>";
      }).join("");

      return (
        '<article class="product-card" data-category="' + esc(product.category) + '" ' +
        'style="animation-delay:' + index * 55 + 'ms">' +
          '<div class="product-card__media">' +
            badgeMarkup(product.badge) +
            likeButton(product) +
            '<img src="' + esc(product.img) + '" alt="' + esc(name) + '" ' +
              'width="600" height="600" loading="lazy" />' +
          "</div>" +
          '<div class="product-card__body">' +
            '<div class="product-card__title-row">' +
              "<h3>" + esc(name) + "</h3>" +
              priceMarkup(product.price) +
            "</div>" +
            '<p class="product-card__desc">' + esc(descriptionOf(product)) + "</p>" +
            '<div class="product-card__tags">' + tags + "</div>" +
            addButton(product, "") +
          "</div>" +
        "</article>"
      );
    }).join("");
  }

  function renderBest() {
    if (!bestGrid) return;

    bestGrid.innerHTML = BEST.map(function (entry, index) {
      const product = PRODUCTS.find((item) => item.id === entry.id);
      if (!product) return "";
      const name = nameOf(product);

      return (
        '<article class="best-card">' +
          '<div class="best-card__media">' +
            '<span class="best-card__rank"><small>' + esc(t("best.rank")) + "</small>" +
              (index + 1) + "</span>" +
            '<span class="best-card__trend">' + icon("i-sparkle") +
              "<span>" + esc(t("best.trending")) + "</span></span>" +
            '<img src="' + esc(product.img) + '" alt="' + esc(name) + '" ' +
              'width="600" height="480" loading="lazy" />' +
          "</div>" +
          '<div class="best-card__body">' +
            "<h3>" + esc(name) + "</h3>" +
            "<p>" + esc(descriptionOf(product)) + "</p>" +
            '<div class="sold">' +
              '<div class="sold__bar"><span style="width:' + Math.max(0, Math.min(100, entry.progress)) + '%"></span></div>' +
              "<span>" + esc(t("best.sold", { n: formatNumber(entry.sold) })) + "</span>" +
            "</div>" +
            '<div class="best-card__foot">' +
              priceMarkup(product.price) +
              addButton(product, "") +
            "</div>" +
          "</div>" +
        "</article>"
      );
    }).join("");
  }

  function renderAddons() {
    if (!addonGrid) return;

    addonGrid.innerHTML = ADDONS.map(function (addon) {
      const name = nameOf(addon);
      return (
        '<article class="addon-card">' +
          '<span class="addon-card__icon">' + icon(addon.icon) + "</span>" +
          '<div class="addon-card__body">' +
            "<h3>" + esc(name) + "</h3>" +
            "<p>" + esc(descriptionOf(addon)) + "</p>" +
          "</div>" +
          '<div class="addon-card__side">' +
            '<span class="addon-card__price">' + esc(formatNumber(addon.price)) +
              "<small>" + esc(t("currency")) + "</small></span>" +
            '<button class="addon-add" type="button" data-addon="' + esc(addon.id) + '" ' +
              'aria-label="' + esc(t("aria.addToCart", { name: name })) + '">' +
              icon("i-plus") + "</button>" +
          "</div>" +
        "</article>"
      );
    }).join("");
  }

  /* ---------- Basket ---------- */
  function loadCart() {
    let stored;
    try {
      stored = JSON.parse(storageGet(STORE.cart, "[]"));
    } catch (error) {
      stored = [];
    }
    if (!Array.isArray(stored)) stored = [];

    state.cart = stored.map(function (entry) {
      if (!entry || typeof entry.id !== "string") return null;
      if (!findItem(entry.id)) return null;
      const qty = Math.max(1, Math.min(MAX_QTY, parseInt(entry.qty, 10) || 1));
      return { id: entry.id, qty: qty };
    }).filter(Boolean);
  }

  function saveCart() {
    storageSet(STORE.cart, JSON.stringify(state.cart));
  }

  function cartTotal() {
    return state.cart.reduce(function (total, entry) {
      const item = findItem(entry.id);
      return item ? total + item.price * entry.qty : total;
    }, 0);
  }

  function cartQuantity() {
    return state.cart.reduce(function (total, entry) {
      return total + entry.qty;
    }, 0);
  }

  function addToCart(id, source) {
    const item = findItem(id);
    if (!item) return;

    const entry = state.cart.find((line) => line.id === id);
    if (entry) {
      entry.qty = Math.min(MAX_QTY, entry.qty + 1);
    } else {
      state.cart.push({ id: id, qty: 1 });
    }

    saveCart();
    renderCart();
    bumpCart();
    toast(t("toast.added", { name: nameOf(item) }));
    flyToCart(source);
  }

  function changeQuantity(id, delta) {
    const entry = state.cart.find((line) => line.id === id);
    if (!entry) return;

    entry.qty = Math.max(1, Math.min(MAX_QTY, entry.qty + delta));
    saveCart();
    renderCart();
    bumpCart();
  }

  function removeFromCart(id) {
    const entry = state.cart.find((line) => line.id === id);
    const item = entry ? findItem(id) : null;
    state.cart = state.cart.filter((line) => line.id !== id);
    saveCart();
    renderCart();
    if (item) toast(t("toast.removed", { name: nameOf(item) }));
  }

  function renderCart() {
    if (!cartList || !cartEmpty || !cartFoot) return;

    const count = cartQuantity();
    if (cartCount) {
      cartCount.textContent = String(count);
      cartCount.style.display = count ? "" : "none";
    }

    const lines = state.cart.map(function (entry) {
      return { entry: entry, item: findItem(entry.id) };
    }).filter((line) => line.item);

    if (!lines.length) {
      cartEmpty.hidden = false;
      cartList.hidden = true;
      cartList.innerHTML = "";
      cartFoot.hidden = true;
      return;
    }

    cartEmpty.hidden = true;
    cartList.hidden = false;
    cartFoot.hidden = false;

    cartList.innerHTML = lines.map(function (line) {
      const item = line.item;
      const name = nameOf(item);
      const isProduct = PRODUCTS.indexOf(item) !== -1;
      const thumb = isProduct
        ? '<span class="cart-item__thumb"><img src="' + esc(item.img) + '" alt="" width="66" height="66" loading="lazy" /></span>'
        : '<span class="cart-item__thumb">' + icon(item.icon) + "</span>";

      const unit = isProduct
        ? t("cart.unit", { price: money(item.price) })
        : money(item.price);

      return (
        '<li class="cart-item" data-id="' + esc(item.id) + '">' +
          thumb +
          '<div class="cart-item__info">' +
            "<h4>" + esc(name) + "</h4>" +
            '<span class="cart-item__unit">' + esc(unit) + "</span>" +
            '<div class="qty">' +
              '<button type="button" data-dec="' + esc(item.id) + '" ' +
                'aria-label="' + esc(t("aria.decrease")) + '"' +
                (line.entry.qty <= 1 ? " disabled" : "") + ">" +
                icon("i-minus") + "</button>" +
              "<span>" + formatNumber(line.entry.qty) + "</span>" +
              '<button type="button" data-inc="' + esc(item.id) + '" ' +
                'aria-label="' + esc(t("aria.increase")) + '"' +
                (line.entry.qty >= MAX_QTY ? " disabled" : "") + ">" +
                icon("i-plus") + "</button>" +
            "</div>" +
          "</div>" +
          '<div class="cart-item__end">' +
            '<span class="cart-item__total">' + esc(money(item.price * line.entry.qty)) + "</span>" +
            '<button class="remove-btn" type="button" data-remove="' + esc(item.id) + '" ' +
              'aria-label="' + esc(t("aria.remove", { name: name })) + '">' +
              icon("i-trash") + "</button>" +
          "</div>" +
        "</li>"
      );
    }).join("");

    const total = cartTotal();
    if (cartSubtotal) cartSubtotal.textContent = money(total);

    if (deliveryText && deliveryFill) {
      const left = Math.max(0, FREE_DELIVERY - total);
      deliveryText.textContent = left > 0
        ? t("cart.freeLeft", { amount: money(left) })
        : t("cart.freeDone");
      deliveryFill.style.width = Math.min(100, (total / FREE_DELIVERY) * 100) + "%";
    }
  }

  function bumpCart() {
    if (!cartBtn || prefersReduced()) return;
    cartBtn.classList.remove("is-bump");
    void cartBtn.offsetWidth;
    cartBtn.classList.add("is-bump");
    window.setTimeout(function () {
      cartBtn.classList.remove("is-bump");
    }, 600);
  }

  function flyToCart(source) {
    if (!source || !cartBtn || prefersReduced()) return;
    if (typeof Element.prototype.animate !== "function") return;

    const card = source.closest(".product-card, .best-card");
    const fromElement = (card && card.querySelector("img")) || source;
    const from = fromElement.getBoundingClientRect();
    const to = cartBtn.getBoundingClientRect();
    if (!from.width || !to.width) return;

    const flyer = document.createElement("div");
    flyer.className = "cookie-fly";
    flyer.innerHTML = icon("i-cookie");
    flyer.style.left = from.left + from.width / 2 - 13 + "px";
    flyer.style.top = from.top + from.height / 2 - 13 + "px";
    document.body.appendChild(flyer);

    const startX = from.left + from.width / 2;
    const startY = from.top + from.height / 2;
    const endX = to.left + to.width / 2;
    const endY = to.top + to.height / 2;
    const dx = endX - startX;
    const dy = endY - startY;

    const animation = flyer.animate([
      { transform: "translate(0, 0) scale(1)", opacity: 1, offset: 0 },
      { transform: "translate(" + dx * 0.45 + "px, " + (dy * 0.45 - 70) + "px) scale(1.15)", opacity: 1, offset: 0.55 },
      { transform: "translate(" + dx + "px, " + dy + "px) scale(0.35)", opacity: 0.35, offset: 1 }
    ], {
      duration: 720,
      easing: "cubic-bezier(0.35, 0.6, 0.35, 1)"
    });

    animation.onfinish = function () {
      if (flyer.parentNode) flyer.parentNode.removeChild(flyer);
    };
    window.setTimeout(function () {
      if (flyer.parentNode) flyer.parentNode.removeChild(flyer);
    }, 1000);
  }

  /* ---------- Drawer, modal, focus ---------- */
  function syncBodyLock() {
    const locked = cartDrawer.classList.contains("is-open") ||
      successModal.classList.contains("is-open");
    document.body.classList.toggle("no-scroll", locked);
  }

  function openCart() {
    if (!cartDrawer) return;
    lastFocused = document.activeElement;
    cartDrawer.classList.add("is-open");
    drawerOverlay.classList.add("is-open");
    cartDrawer.setAttribute("aria-hidden", "false");
    cartBtn.setAttribute("aria-expanded", "true");
    syncBodyLock();
    window.setTimeout(function () {
      if (cartClose) cartClose.focus({ preventScroll: true });
    }, 120);
  }

  function closeCart(restoreFocus) {
    if (!cartDrawer) return;
    const wasOpen = cartDrawer.classList.contains("is-open");
    cartDrawer.classList.remove("is-open");
    drawerOverlay.classList.remove("is-open");
    cartDrawer.setAttribute("aria-hidden", "true");
    cartBtn.setAttribute("aria-expanded", "false");
    syncBodyLock();

    if (wasOpen && restoreFocus !== false && lastFocused && document.contains(lastFocused)) {
      lastFocused.focus({ preventScroll: true });
    }
  }

  function showSuccess() {
    const order = "#CN-" + String(Math.floor(1000 + Math.random() * 9000));
    if (orderNumber) orderNumber.textContent = order;

    successModal.classList.add("is-open");
    successOverlay.classList.add("is-open");
    successModal.setAttribute("aria-hidden", "false");
    syncBodyLock();
    confetti();

    window.setTimeout(function () {
      if (successDone) successDone.focus({ preventScroll: true });
    }, 150);
  }

  function closeSuccess() {
    successModal.classList.remove("is-open");
    successOverlay.classList.remove("is-open");
    successModal.setAttribute("aria-hidden", "true");
    syncBodyLock();
    if (cartBtn) cartBtn.focus({ preventScroll: true });
  }

  function checkout() {
    if (!state.cart.length) {
      toast(t("toast.emptyCart"));
      return;
    }

    state.cart = [];
    saveCart();
    renderCart();
    closeCart(false);
    showSuccess();
  }

  function trapFocus(event) {
    if (event.key !== "Tab") return;
    const modalOpen = successModal.classList.contains("is-open");
    const drawerOpen = cartDrawer.classList.contains("is-open");
    const container = modalOpen ? successModal : drawerOpen ? cartDrawer : null;
    if (!container) return;

    const focusable = $$(
      'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
      container
    ).filter(function (element) {
      return element.offsetWidth > 0 || element.offsetHeight > 0 || element === document.activeElement;
    });

    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  /* ---------- Navigation ---------- */
  function updateNavState() {
    if (!nav || !navToggle) return;
    const open = nav.classList.contains("is-open");
    navToggle.setAttribute("aria-expanded", String(open));
    navToggle.setAttribute("aria-label", t(open ? "aria.closeMenu" : "aria.menu"));
  }

  function openNav() {
    nav.classList.add("is-open");
    navToggle.classList.add("is-open");
    header.classList.add("is-open");
    updateNavState();
  }

  function closeNav() {
    if (!nav) return;
    nav.classList.remove("is-open");
    navToggle.classList.remove("is-open");
    header.classList.remove("is-open");
    updateNavState();
  }

  function scrollToSection(hash) {
    if (!hash || hash === "#") return;
    const target = document.getElementById(hash.slice(1));
    if (!target) return;
    target.scrollIntoView({ behavior: prefersReduced() ? "auto" : "smooth", block: "start" });
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", hash);
    }
  }

  function setActiveNav(id) {
    navLinks.forEach(function (link) {
      link.classList.toggle("is-active", link.getAttribute("href") === "#" + id);
    });
  }

  function onScroll() {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 12);

    const offset = header.offsetHeight + 28;
    let active = "home";

    sections.forEach(function (section) {
      if (section.getBoundingClientRect().top <= offset) active = section.id;
    });

    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 12) {
      active = "contact";
    }

    setActiveNav(active);
  }

  /* ---------- Filters ---------- */
  function setFilter(filter) {
    state.filter = filter;
    if (!filtersBar) return;

    $$(".filter", filtersBar).forEach(function (button) {
      const active = button.getAttribute("data-filter") === filter;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });

    renderProducts();
  }

  /* ---------- Favourites ---------- */
  function loadLikes() {
    let stored;
    try {
      stored = JSON.parse(storageGet(STORE.likes, "[]"));
    } catch (error) {
      stored = [];
    }
    state.likes = new Set(Array.isArray(stored) ? stored.filter(function (id) {
      return typeof id === "string" && findItem(id);
    }) : []);
  }

  function saveLikes() {
    storageSet(STORE.likes, JSON.stringify(Array.from(state.likes)));
  }

  function toggleLike(button) {
    const id = button.getAttribute("data-like");
    const item = findItem(id);
    if (!item) return;

    const liked = !state.likes.has(id);
    if (liked) state.likes.add(id);
    else state.likes.delete(id);

    saveLikes();
    button.classList.toggle("is-liked", liked);
    button.setAttribute("aria-pressed", String(liked));
    button.setAttribute("aria-label", t(liked ? "aria.unlike" : "aria.like", { name: nameOf(item) }));
    toast(t(liked ? "toast.liked" : "toast.unliked"));
  }

  /* ---------- Countdown ---------- */
  function pad2(value) {
    return String(value).padStart(2, "0");
  }

  function initCountdown() {
    if (!cdDays || !cdHours || !cdMinutes || !cdSeconds) return;

    let deadline = Number(storageGet(STORE.offerEnd, "0"));
    if (!isFinite(deadline) || deadline <= Date.now()) {
      deadline = Date.now() + 3 * 24 * 60 * 60 * 1000;
      storageSet(STORE.offerEnd, String(deadline));
    }
    state.offerEnd = deadline;

    function tick() {
      let diff = state.offerEnd - Date.now();
      if (diff <= 0) {
        state.offerEnd = Date.now() + 3 * 24 * 60 * 60 * 1000;
        storageSet(STORE.offerEnd, String(state.offerEnd));
        diff = state.offerEnd - Date.now();
      }

      const days = Math.floor(diff / 86400000);
      const hours = Math.floor((diff % 86400000) / 3600000);
      const minutes = Math.floor((diff % 3600000) / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);

      cdDays.textContent = pad2(days);
      cdHours.textContent = pad2(hours);
      cdMinutes.textContent = pad2(minutes);
      cdSeconds.textContent = pad2(seconds);
    }

    tick();
    window.setInterval(tick, 1000);
  }

  /* ---------- Stars ---------- */
  function initStars() {
    if (!bgStars) return;
    const fragment = document.createDocumentFragment();
    for (let index = 0; index < 46; index += 1) {
      const star = document.createElement("span");
      star.className = "star-dot";
      star.style.left = (Math.random() * 100).toFixed(2) + "%";
      star.style.top = (Math.random() * 100).toFixed(2) + "%";
      star.style.animationDelay = (-Math.random() * 4).toFixed(2) + "s";
      star.style.animationDuration = (3 + Math.random() * 3).toFixed(2) + "s";
      if (Math.random() > 0.78) {
        star.style.width = "5px";
        star.style.height = "5px";
      }
      fragment.appendChild(star);
    }
    bgStars.appendChild(fragment);
  }

  /* ---------- Reveal ---------- */
  function initReveal() {
    const elements = $$("[data-reveal]");
    if (!elements.length) return;

    elements.forEach(function (element) {
      const delay = parseInt(element.getAttribute("data-delay"), 10);
      if (delay > 0 && !prefersReduced()) {
        element.style.transitionDelay = delay * 90 + "ms";
      }
    });

    if (!("IntersectionObserver" in window) || prefersReduced()) {
      elements.forEach(function (element) {
        element.classList.add("is-visible");
      });
      return;
    }

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    elements.forEach(function (element) {
      observer.observe(element);
    });
  }

  /* ---------- Confetti ---------- */
  function confetti() {
    if (!confettiLayer || prefersReduced()) return;
    confettiLayer.innerHTML = "";

    const colors = ["#E88CA2", "#C98B58", "#F0C97A", "#CFEAF5", "#F9D7DE", "#D9A05E", "#FFF6E5"];
    const fragment = document.createDocumentFragment();

    for (let index = 0; index < 74; index += 1) {
      const piece = document.createElement("i");
      piece.className = "confetti-piece";
      piece.style.left = (Math.random() * 100).toFixed(2) + "%";
      piece.style.background = colors[Math.floor(Math.random() * colors.length)];
      piece.style.animationDuration = (2.3 + Math.random() * 2.1).toFixed(2) + "s";
      piece.style.animationDelay = (Math.random() * 0.55).toFixed(2) + "s";
      piece.style.width = (6 + Math.random() * 6).toFixed(1) + "px";
      piece.style.height = (9 + Math.random() * 9).toFixed(1) + "px";
      piece.style.setProperty("--drift", (Math.random() * 200 - 100).toFixed(1) + "px");
      piece.style.setProperty("--rot", Math.floor(360 + Math.random() * 780) + "deg");
      if (Math.random() > 0.7) piece.style.borderRadius = "50%";
      fragment.appendChild(piece);
    }

    confettiLayer.appendChild(fragment);
    window.setTimeout(function () {
      confettiLayer.innerHTML = "";
    }, 5200);
  }

  /* ---------- Copy code ---------- */
  function fallbackCopy(text) {
    const field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.top = "-1000px";
    field.style.opacity = "0";
    document.body.appendChild(field);
    field.select();
    try {
      document.execCommand("copy");
    } catch (error) {
      /* nothing else to do */
    }
    document.body.removeChild(field);
  }

  function copyCode(text) {
    if (!text) return;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        toast(t("toast.copied"));
      }).catch(function () {
        fallbackCopy(text);
        toast(t("toast.copied"));
      });
    } else {
      fallbackCopy(text);
      toast(t("toast.copied"));
    }
  }

  /* ---------- Forms ---------- */
  function validEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
  }

  function markInvalid(field, invalid) {
    if (!field) return;
    field.classList.toggle("is-invalid", Boolean(invalid));
    field.setAttribute("aria-invalid", String(Boolean(invalid)));
  }

  function initForms() {
    if (contactForm) {
      contactForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const name = $("#contactName");
        const email = $("#contactEmail");
        const message = $("#contactMessage");

        const nameBad = !name.value.trim() || name.value.trim().length < 2;
        const emailBad = !validEmail(email.value.trim());
        const messageBad = !message.value.trim() || message.value.trim().length < 5;

        markInvalid(name, nameBad);
        markInvalid(email, emailBad);
        markInvalid(message, messageBad);

        if (nameBad || emailBad || messageBad) {
          toast(t("toast.invalid"));
          const firstBad = [name, email, message].find(function (field) {
            return field.classList.contains("is-invalid");
          });
          if (firstBad) firstBad.focus();
          return;
        }

        contactForm.reset();
        [name, email, message].forEach(function (field) {
          markInvalid(field, false);
        });
        toast(t("toast.message"));
      });

      contactForm.addEventListener("input", function (event) {
        if (event.target && event.target.classList) {
          event.target.classList.remove("is-invalid");
          event.target.setAttribute("aria-invalid", "false");
        }
      });
    }

    if (newsletterForm) {
      newsletterForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const email = $("#newsletterEmail");
        if (!email || !validEmail(email.value.trim())) {
          markInvalid(email, true);
          toast(t("toast.invalid"));
          if (email) email.focus();
          return;
        }

        markInvalid(email, false);
        newsletterForm.reset();
        toast(t("toast.subscribed"));
      });

      const email = $("#newsletterEmail");
      if (email) {
        email.addEventListener("input", function () {
          markInvalid(email, false);
        });
      }
    }
  }

  /* ---------- Events ---------- */
  function bindEvents() {
    if (modeSwitch) modeSwitch.addEventListener("click", toggleTheme);
    if (langBtn) langBtn.addEventListener("click", toggleLanguage);
    if (cartBtn) cartBtn.addEventListener("click", openCart);
    if (cartClose) cartClose.addEventListener("click", function () { closeCart(); });
    if (drawerOverlay) drawerOverlay.addEventListener("click", function () { closeCart(); });
    if (cartBrowse) {
      cartBrowse.addEventListener("click", function () {
        closeCart(false);
        scrollToSection("#cookies");
      });
    }
    if (checkoutBtn) checkoutBtn.addEventListener("click", checkout);
    if (successClose) successClose.addEventListener("click", closeSuccess);
    if (successDone) successDone.addEventListener("click", closeSuccess);
    if (successOverlay) successOverlay.addEventListener("click", closeSuccess);

    if (navToggle) {
      navToggle.addEventListener("click", function () {
        if (nav.classList.contains("is-open")) closeNav();
        else openNav();
      });
    }

    if (filtersBar) {
      filtersBar.addEventListener("click", function (event) {
        const button = event.target.closest("[data-filter]");
        if (button) setFilter(button.getAttribute("data-filter"));
      });
    }

    document.addEventListener("click", function (event) {
      const copyTarget = event.target.closest("[data-copy]");
      if (copyTarget) {
        copyCode(copyTarget.getAttribute("data-copy"));
        return;
      }

      const likeTarget = event.target.closest("[data-like]");
      if (likeTarget) {
        toggleLike(likeTarget);
        return;
      }

      const addTarget = event.target.closest("[data-add]");
      if (addTarget) {
        addToCart(addTarget.getAttribute("data-add"), addTarget);
        return;
      }

      const addonTarget = event.target.closest("[data-addon]");
      if (addonTarget) {
        addToCart(addonTarget.getAttribute("data-addon"), addonTarget);
        return;
      }

      const incTarget = event.target.closest("[data-inc]");
      if (incTarget) {
        changeQuantity(incTarget.getAttribute("data-inc"), 1);
        return;
      }

      const decTarget = event.target.closest("[data-dec]");
      if (decTarget) {
        changeQuantity(decTarget.getAttribute("data-dec"), -1);
        return;
      }

      const removeTarget = event.target.closest("[data-remove]");
      if (removeTarget) {
        removeFromCart(removeTarget.getAttribute("data-remove"));
        return;
      }

      const anchor = event.target.closest('a[href^="#"]');
      if (anchor) {
        const hash = anchor.getAttribute("href");
        if (hash === "#") {
          event.preventDefault();
          return;
        }
        if (document.getElementById(hash.slice(1))) {
          event.preventDefault();
          closeNav();
          if (cartDrawer.classList.contains("is-open")) closeCart(false);
          scrollToSection(hash);
          return;
        }
      }

      if (nav && nav.classList.contains("is-open") &&
        !nav.contains(event.target) && !navToggle.contains(event.target)) {
        closeNav();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        if (successModal.classList.contains("is-open")) {
          closeSuccess();
        } else if (cartDrawer.classList.contains("is-open")) {
          closeCart();
        } else if (nav.classList.contains("is-open")) {
          closeNav();
        }
      }
      trapFocus(event);
    });

    if (greeting) {
      greeting.addEventListener("animationend", function () {
        greeting.classList.remove("is-pop");
      });
    }

    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        onScroll();
        ticking = false;
      });
    }, { passive: true });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1040) closeNav();
    });

    document.addEventListener("input", function (event) {
      if (event.target.classList && event.target.classList.contains("is-invalid")) {
        event.target.classList.remove("is-invalid");
        event.target.setAttribute("aria-invalid", "false");
      }
    });
  }

  /* ---------- Boot ---------- */
  function init() {
    state.lang = html.lang === "en" ? "en" : "ar";
    state.theme = html.dataset.theme === "evening" ? "evening" : "morning";

    loadCart();
    loadLikes();
    applyLanguage(state.lang, { silent: true });
    applyTheme(state.theme, false);
    initStars();
    initCountdown();
    initReveal();
    initForms();
    bindEvents();
    onScroll();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
