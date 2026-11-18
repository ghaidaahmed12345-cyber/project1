"""Generate the Cookie Nook SVG illustration set.

Everything is drawn as layered vector art so the site stays crisp at any size
and needs no external images. Run: python tools/gen_art.py
"""

import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
os.makedirs(OUT, exist_ok=True)


# --------------------------------------------------------------------------
# palette
# --------------------------------------------------------------------------
BROWN = "#4A2B1D"
BROWN_2 = "#5A3524"
CARAMEL = "#C98B58"
CARAMEL_DARK = "#A9643A"
CREAM = "#FFF9F0"
CREAM_2 = "#FFF6E5"
PINK = "#F3C4CE"
PINK_STRONG = "#E88CA2"
SKY = "#CFEAF5"
GOLD = "#E9B872"

VARIANTS = {
    "classic": {
        "base": "#DCA363",
        "light": "#EFC084",
        "dark": "#B0733F",
        "chip": "#4A2B1D",
        "chip_stroke": "#3A2117",
        "chip_kind": "dark",
    },
    "double": {
        "base": "#8B5A3C",
        "light": "#A97452",
        "dark": "#5B3726",
        "chip": "#341C12",
        "chip_stroke": "#24120C",
        "chip_kind": "dark",
    },
    "strawberry": {
        "base": "#F0A6B7",
        "light": "#F9C6D1",
        "dark": "#D57A91",
        "chip": "#FFF4E2",
        "chip_stroke": "#EBD6B8",
        "chip_kind": "white",
    },
    "pistachio": {
        "base": "#C8D8A3",
        "light": "#DEE9C1",
        "dark": "#9DB77A",
        "chip": "#FFF6E7",
        "chip_stroke": "#EAD9BB",
        "chip_kind": "white",
    },
    "oat": {
        "base": "#D9B47E",
        "light": "#EDCE9E",
        "dark": "#B48A58",
        "chip": "#6B4A2F",
        "chip_stroke": "#553823",
        "chip_kind": "dark",
    },
    "caramel": {
        "base": "#DDA45F",
        "light": "#F2C585",
        "dark": "#B4763A",
        "chip": "#4A2B1D",
        "chip_stroke": "#3A2117",
        "chip_kind": "dark",
    },
}

PRODUCT_BG = {
    "classic": ("#FFF3E2", "#F7DEC1", PINK),
    "double": ("#F4E4DA", "#E7CBB9", SKY),
    "strawberry": ("#FDEBF0", "#F8D2DA", PINK),
    "pistachio": ("#EEF4E2", "#DCE8C6", SKY),
    "oat": ("#FBF0DF", "#F1DCC0", PINK),
    "caramel": ("#FDF0DC", "#F5DAB6", SKY),
}


# --------------------------------------------------------------------------
# small drawing helpers
# --------------------------------------------------------------------------
def star(cx, cy, size, fill, opacity=1.0, points=5):
    coords = []
    for i in range(points * 2):
        radius = size if i % 2 == 0 else size * 0.42
        angle = -math.pi / 2 + i * math.pi / points
        coords.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in coords) + " Z"
    return f'<path d="{path}" fill="{fill}" opacity="{opacity}"/>'


def heart(cx, cy, size, fill, opacity=1.0, rotate=0):
    s = size
    d = (
        f"M {cx} {cy + s * 0.85} "
        f"C {cx - s * 1.25} {cy - s * 0.05} {cx - s * 0.9} {cy - s * 0.95} {cx} {cy - s * 0.35} "
        f"C {cx + s * 0.9} {cy - s * 0.95} {cx + s * 1.25} {cy - s * 0.05} {cx} {cy + s * 0.85} Z"
    )
    return f'<path d="{d}" fill="{fill}" opacity="{opacity}" transform="rotate({rotate} {cx} {cy})"/>'


def chunk(cx, cy, size, rotate, fill, stroke, stroke_opacity=0.35):
    s = size
    d = (
        f"M {-s} {-s * 0.62} L {-s * 0.34} {-s * 1.02} L {s * 0.72} {-s * 0.72} "
        f"L {s * 1.02} {s * 0.26} L {s * 0.34} {s * 0.96} L {-s * 0.7} {s * 0.7} Z"
    )
    return (
        f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-opacity="{stroke_opacity}" '
        f'stroke-width="{max(1.2, s * 0.12):.1f}" transform="translate({cx:.1f} {cy:.1f}) rotate({rotate:.0f})"/>'
    )


def dot(cx, cy, r, fill, opacity=1.0):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" opacity="{opacity}"/>'


def ellipse(cx, cy, rx, ry, fill, opacity=1.0, rotate=0, stroke=None, sw=0):
    stroke_attr = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" '
        f'opacity="{opacity}" transform="rotate({rotate} {cx:.1f} {cy:.1f})"{stroke_attr}/>'
    )


def sparkle(cx, cy, size, fill, opacity=1.0):
    d = (
        f"M {cx} {cy - size} C {cx + size * 0.16} {cy - size * 0.28} {cx + size * 0.3} {cy - size * 0.14} {cx + size} {cy} "
        f"C {cx + size * 0.3} {cy + size * 0.14} {cx + size * 0.16} {cy + size * 0.28} {cx} {cy + size} "
        f"C {cx - size * 0.16} {cy + size * 0.28} {cx - size * 0.3} {cy + size * 0.14} {cx - size} {cy} "
        f"C {cx - size * 0.3} {cy - size * 0.14} {cx - size * 0.16} {cy - size * 0.28} {cx} {cy - size} Z"
    )
    return f'<path d="{d}" fill="{fill}" opacity="{opacity}"/>'


def dots_field(width, height, spacing, radius, fill, opacity):
    parts = []
    for y in range(spacing // 2, height, spacing):
        for x in range(spacing // 2, width, spacing):
            parts.append(dot(x, y, radius, fill, opacity))
    return "".join(parts)


# --------------------------------------------------------------------------
# cookie
# --------------------------------------------------------------------------
def cookie(name, cx, cy, r, rotate=0, seed=1, uid="0"):
    """Return (defs, markup) for one cookie centred on cx/cy."""
    cfg = VARIANTS[name]
    rng = random.Random(seed)
    gid = f"cookie-{uid}"
    clip = f"clip-{uid}"

    defs = (
        f'<radialGradient id="{gid}" cx="36%" cy="28%" r="78%">'
        f'<stop offset="0" stop-color="{cfg["light"]}"/>'
        f'<stop offset="0.62" stop-color="{cfg["base"]}"/>'
        f'<stop offset="1" stop-color="{cfg["dark"]}"/>'
        f"</radialGradient>"
        f'<clipPath id="{clip}"><circle r="{r}"/></clipPath>'
    )

    body = [
        f'<circle r="{r}" fill="url(#{gid})"/>',
        f'<g clip-path="url(#{clip})">',
        f'<ellipse cx="0" cy="{r * 0.62:.1f}" rx="{r * 0.94:.1f}" ry="{r * 0.62:.1f}" '
        f'fill="{cfg["dark"]}" opacity="0.18"/>',
        f'<ellipse cx="{-r * 0.28:.1f}" cy="{-r * 0.42:.1f}" rx="{r * 0.52:.1f}" ry="{r * 0.3:.1f}" '
        f'fill="#FFFFFF" opacity="0.16" transform="rotate(-18 {-r * 0.28:.1f} {-r * 0.42:.1f})"/>',
        "</g>",
        f'<circle r="{r}" fill="none" stroke="{cfg["dark"]}" stroke-opacity="0.24" stroke-width="{max(1.4, r * 0.018):.1f}"/>',
    ]

    # airy crumb texture
    for _ in range(7):
        ang = rng.uniform(0, math.tau)
        rad = rng.uniform(0.18, 0.82) * r
        body.append(dot(math.cos(ang) * rad, math.sin(ang) * rad, rng.uniform(r * 0.014, r * 0.03), cfg["dark"], 0.2))

    # chocolate / white chunks
    count = 11 if name in ("classic", "double", "caramel") else 9
    for i in range(count):
        ang = (i / count) * math.tau + rng.uniform(-0.32, 0.32)
        rad = rng.uniform(0.12, 0.68) * r
        px, py = math.cos(ang) * rad, math.sin(ang) * rad
        size = rng.uniform(0.08, 0.125) * r
        body.append(chunk(px, py, size, rng.uniform(-40, 40), cfg["chip"], cfg["chip_stroke"]))

    # variant-specific toppings
    if name == "double":
        for _ in range(12):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(0.25, 0.88) * r
            body.append(dot(math.cos(ang) * rad, math.sin(ang) * rad, rng.uniform(1.4, 3.4), "#2E190F", 0.36))

    if name == "strawberry":
        drizzle = (
            f"M {-r * 0.78:.1f} {-r * 0.02:.1f} "
            f"C {-r * 0.42:.1f} {-r * 0.52:.1f} {-r * 0.06:.1f} {r * 0.32:.1f} {r * 0.3:.1f} {-r * 0.02:.1f} "
            f"S {r * 0.68:.1f} {-r * 0.38:.1f} {r * 0.82:.1f} {r * 0.12:.1f}"
        )
        body.append(
            f'<path d="{drizzle}" fill="none" stroke="#FFF6E7" stroke-width="{r * 0.075:.1f}" '
            f'stroke-linecap="round" opacity="0.92"/>'
        )
        for _ in range(4):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(0.4, 0.78) * r
            px, py = math.cos(ang) * rad, math.sin(ang) * rad
            body.append(ellipse(px, py, r * 0.085, r * 0.06, "#E4637F", 0.95, rng.uniform(-50, 50)))
            body.append(dot(px - 3, py - 2, 1.4, "#FFF0DC", 0.8))

    if name == "pistachio":
        for _ in range(7):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(0.3, 0.8) * r
            px, py = math.cos(ang) * rad, math.sin(ang) * rad
            body.append(ellipse(px, py, r * 0.075, r * 0.052, "#8FB067", 0.95, rng.uniform(-70, 70), "#6E8F4A", 1))
        body.append(
            f'<path d="M {-r * 0.6:.1f} {r * 0.3:.1f} C {-r * 0.2:.1f} {r * 0.05:.1f} {r * 0.2:.1f} {r * 0.42:.1f} {r * 0.68:.1f} {r * 0.05:.1f}" '
            f'fill="none" stroke="#FFF7E8" stroke-width="{r * 0.055:.1f}" stroke-linecap="round" opacity="0.85"/>'
        )

    if name == "oat":
        for _ in range(13):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(0.22, 0.82) * r
            px, py = math.cos(ang) * rad, math.sin(ang) * rad
            body.append(ellipse(px, py, r * 0.095, r * 0.036, "#F4DDB6", 0.92, rng.uniform(-90, 90), "#B48A58", 1.1))
        for _ in range(3):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(0.3, 0.68) * r
            body.append(chunk(math.cos(ang) * rad, math.sin(ang) * rad, r * 0.115, rng.uniform(-30, 30), "#7A5335", "#5C3C26"))

    if name == "caramel":
        for offset, width in ((0.0, 0.075), (0.26, 0.05)):
            body.append(
                f'<path d="M {-r * 0.78:.1f} {(-r * 0.18) + r * offset:.1f} '
                f'C {-r * 0.4:.1f} {(-r * 0.6) + r * offset:.1f} {-r * 0.05:.1f} {(r * 0.3) + r * offset:.1f} {r * 0.26:.1f} {(r * 0.02) + r * offset:.1f} '
                f'S {r * 0.68:.1f} {(-r * 0.34) + r * offset:.1f} {r * 0.82:.1f} {(r * 0.14) + r * offset:.1f}" '
                f'fill="none" stroke="#A9643A" stroke-width="{r * width:.1f}" stroke-linecap="round" opacity="0.92"/>'
            )
        for _ in range(9):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(0.28, 0.8) * r
            size = rng.uniform(1.3, 2.6)
            body.append(
                f'<rect x="{math.cos(ang) * rad:.1f}" y="{math.sin(ang) * rad:.1f}" width="{size:.1f}" '
                f'height="{size:.1f}" fill="#FFF9ED" opacity="0.9" transform="rotate(20 {math.cos(ang) * rad:.1f} {math.sin(ang) * rad:.1f})"/>'
            )

    if name == "classic":
        for _ in range(5):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(0.35, 0.8) * r
            body.append(dot(math.cos(ang) * rad, math.sin(ang) * rad, rng.uniform(1.2, 2.2), "#FFF6E5", 0.85))

    markup = (
        f'<g transform="translate({cx} {cy}) rotate({rotate})">'
        f'<ellipse cx="0" cy="{r * 0.94:.1f}" rx="{r * 0.84:.1f}" ry="{r * 0.16:.1f}" fill="{BROWN}" opacity="0.13"/>'
        + "".join(body)
        + "</g>"
    )
    return defs, markup


def crumbs(seed, cx, cy, spread, count=14, colors=None):
    rng = random.Random(seed)
    colors = colors or ["#C98B58", "#A9643A", "#E9B872", "#F3C4CE"]
    parts = []
    for _ in range(count):
        ang = rng.uniform(0, math.tau)
        rad = rng.uniform(spread * 0.55, spread)
        parts.append(
            dot(
                cx + math.cos(ang) * rad,
                cy + math.sin(ang) * rad,
                rng.uniform(2.2, 5.5),
                colors[rng.randrange(len(colors))],
                rng.uniform(0.35, 0.8),
            )
        )
    return "".join(parts)


def base_defs(extra=""):
    return (
        '<defs>'
        '<filter id="soft" x="-30%" y="-30%" width="160%" height="160%">'
        '<feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#4A2B1D" flood-opacity="0.18"/>'
        "</filter>"
        '<filter id="wob" x="-8%" y="-8%" width="116%" height="116%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.014" numOctaves="2" seed="9" result="noise"/>'
        '<feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G"/>'
        "</filter>"
        '<filter id="grain">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" result="n"/>'
        '<feColorMatrix in="n" type="saturate" values="0"/>'
        "</filter>"
        + extra
        + "</defs>"
    )


def grain_rect(width, height, opacity=0.035):
    return (
        f'<rect width="{width}" height="{height}" filter="url(#grain)" opacity="{opacity}" '
        'style="mix-blend-mode:multiply"/>'
    )


# --------------------------------------------------------------------------
# product illustrations
# --------------------------------------------------------------------------
def product(name):
    width = height = 600
    bg1, bg2, accent = PRODUCT_BG[name]
    defs, cookie_markup = cookie(name, 300, 300, 196, rotate=-8, seed=hash(name) % 9999, uid=name)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600" role="img">
{base_defs(defs)}
<defs>
  <linearGradient id="bg-{name}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{bg1}"/>
    <stop offset="1" stop-color="{bg2}"/>
  </linearGradient>
</defs>
<rect width="600" height="600" fill="url(#bg-{name})"/>
<circle cx="84" cy="92" r="118" fill="{accent}" opacity="0.34"/>
<circle cx="546" cy="538" r="152" fill="{PINK}" opacity="0.24"/>
{dots_field(600, 600, 40, 1.5, "#FFFFFF", 0.26)}
<circle cx="300" cy="314" r="228" fill="#FFFDF8" opacity="0.62"/>
<circle cx="300" cy="314" r="228" fill="none" stroke="{accent}" stroke-opacity="0.28" stroke-width="2"/>
<circle cx="300" cy="314" r="204" fill="#FFFFFF" opacity="0.22"/>
{cookie_markup}
{crumbs(hash(name) % 777, 300, 306, 268, 16)}
{star(88, 486, 13, GOLD, 0.9)}
{sparkle(512, 108, 15, PINK_STRONG, 0.75)}
{heart(76, 188, 10, PINK_STRONG, 0.6, -12)}
{star(520, 430, 9, "#FFFFFF", 0.8)}
{grain_rect(600, 600, 0.03)}
</svg>
'''


# --------------------------------------------------------------------------
# hero illustration
# --------------------------------------------------------------------------
def hero():
    width = height = 1000
    pieces = []
    defs = []

    def add_cookie(variant, cx, cy, r, rotate, uid):
        d, m = cookie(variant, cx, cy, r, rotate=rotate, seed=uid * 37 + 5, uid=variant + str(uid))
        defs.append(d)
        pieces.append(m)

    # background
    body = [
        '<rect width="1000" height="1000" fill="#FFF6E9"/>',
        '<defs>'
        '<radialGradient id="hero-pink" cx="20%" cy="14%" r="58%">'
        f'<stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>'
        "</radialGradient>"
        '<radialGradient id="hero-sky" cx="88%" cy="76%" r="54%">'
        f'<stop offset="0" stop-color="{SKY}"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/>'
        "</radialGradient>"
        '<radialGradient id="hero-gold" cx="60%" cy="90%" r="42%">'
        f'<stop offset="0" stop-color="{GOLD}" stop-opacity="0.5"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>'
        "</radialGradient>"
        "</defs>",
        '<rect width="1000" height="1000" fill="url(#hero-pink)"/>',
        '<rect width="1000" height="1000" fill="url(#hero-sky)"/>',
        '<rect width="1000" height="1000" fill="url(#hero-gold)"/>',
        dots_field(1000, 1000, 58, 1.4, "#B98A63", 0.16),
    ]

    # soft border doodles
    body.append(f'<circle cx="500" cy="505" r="438" fill="none" stroke="{CARAMEL}" stroke-opacity="0.22" stroke-width="2" stroke-dasharray="2 13"/>')
    body.append(f'<circle cx="500" cy="505" r="470" fill="none" stroke="{PINK_STRONG}" stroke-opacity="0.16" stroke-width="2" stroke-dasharray="2 17"/>')

    # napkin
    body.append(
        f'<rect x="192" y="206" width="616" height="616" rx="86" fill="#F9D7DE" opacity="0.62" '
        'transform="rotate(-7 500 514)"/>'
    )
    body.append(
        f'<rect x="222" y="236" width="556" height="556" rx="70" fill="none" stroke="#E88CA2" '
        'stroke-opacity="0.35" stroke-width="2" stroke-dasharray="10 12" transform="rotate(-7 500 514)"/>'
    )

    # plate
    body.append('<ellipse cx="500" cy="560" rx="328" ry="318" fill="#4A2B1D" opacity="0.12"/>')
    body.append('<circle cx="500" cy="515" r="322" fill="#FFFDF8"/>')
    body.append('<circle cx="500" cy="515" r="322" fill="none" stroke="#EED7BB" stroke-width="4"/>')
    body.append('<circle cx="500" cy="515" r="286" fill="none" stroke="#F3C4CE" stroke-opacity="0.55" stroke-width="2" stroke-dasharray="2 10"/>')
    body.append('<circle cx="500" cy="515" r="296" fill="#FFF6E5" opacity="0.24"/>')

    # cookies on the plate — back to front
    add_cookie("classic", 405, 420, 130, -12, 1)
    add_cookie("double", 616, 440, 118, 10, 2)
    add_cookie("pistachio", 394, 638, 120, -7, 3)
    add_cookie("strawberry", 618, 646, 124, 15, 4)
    add_cookie("caramel", 512, 536, 116, 3, 5)

    # loose cookies outside the plate
    add_cookie("oat", 146, 268, 70, -18, 6)
    add_cookie("classic", 862, 764, 66, 22, 7)

    # crumbs + garnish
    body.append(crumbs(31, 500, 520, 440, 30))
    body.append(crumbs(44, 152, 342, 92, 9))
    body.append(crumbs(55, 862, 690, 82, 8))

    # decorations
    body.append(star(190, 712, 15, GOLD, 0.95))
    body.append(star(824, 286, 11, GOLD, 0.9))
    body.append(sparkle(208, 132, 18, PINK_STRONG, 0.8))
    body.append(sparkle(796, 500, 13, PINK_STRONG, 0.65))
    body.append(heart(838, 158, 15, PINK_STRONG, 0.72, 12))
    body.append(heart(120, 844, 12, PINK_STRONG, 0.55, -8))
    body.append(star(742, 872, 9, "#FFFFFF", 0.85))
    body.append(grain_rect(1000, 1000, 0.035))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000" role="img">
{base_defs("".join(defs))}
{"".join(body)}
{"".join(pieces)}
</svg>
'''


# --------------------------------------------------------------------------
# bakery storefront
# --------------------------------------------------------------------------
def about():
    width, height = 1000, 820
    pieces = []
    defs = []

    def add_cookie(variant, cx, cy, r, rotate, uid):
        d, m = cookie(variant, cx, cy, r, rotate=rotate, seed=uid * 53 + 11, uid="about" + variant + str(uid))
        defs.append(d)
        pieces.append(m)

    # background
    body = [
        '<rect width="1000" height="820" fill="#FFF3E6"/>',
        '<defs>'
        '<linearGradient id="about-sky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#FDE7D8"/><stop offset="1" stop-color="#FFF6E9"/>'
        "</linearGradient>"
        '<radialGradient id="about-sun" cx="50%" cy="50%" r="50%">'
        '<stop offset="0" stop-color="#FFE9A6"/><stop offset="1" stop-color="#F7C96B"/>'
        "</radialGradient>"
        "</defs>",
        '<rect width="1000" height="820" fill="url(#about-sky)"/>',
        dots_field(1000, 820, 52, 1.3, "#C98B58", 0.12),
        '<circle cx="132" cy="138" r="78" fill="url(#about-sun)" opacity="0.85"/>',
        '<circle cx="132" cy="138" r="96" fill="#F7C96B" opacity="0.12"/>',
    ]

    # clouds
    for cx, cy, s in ((806, 126, 1.0), (286, 96, 0.72)):
        body.append(
            f'<g opacity="0.85" transform="translate({cx} {cy}) scale({s})">'
            f'<ellipse cx="0" cy="0" rx="62" ry="26" fill="#FFFFFF"/>'
            f'<ellipse cx="-44" cy="8" rx="34" ry="20" fill="#FFFFFF"/>'
            f'<ellipse cx="42" cy="8" rx="38" ry="22" fill="#FFFFFF"/>'
            "</g>"
        )

    # sidewalk / ground
    body.append('<rect x="0" y="694" width="1000" height="126" fill="#EAD3BA"/>')
    body.append('<rect x="0" y="694" width="1000" height="10" fill="#D8B995"/>')
    body.append('<path d="M 0 756 H 1000 M 0 788 H 1000" stroke="#D8B995" stroke-width="2" opacity="0.5" stroke-dasharray="34 22"/>')

    # plant pots behind building
    body.append('<ellipse cx="118" cy="690" rx="58" ry="18" fill="#4A2B1D" opacity="0.12"/>')
    body.append('<path d="M 88 628 h 60 l -8 62 h -44 Z" fill="#C98B58"/>')
    body.append('<path d="M 96 628 h 44" stroke="#A9643A" stroke-width="4"/>')
    for lx, ly, rot in ((104, 592, -28), (132, 580, 8), (122, 604, -2), (82, 610, -52), (148, 610, 38)):
        body.append(ellipse(lx, ly, 24, 10, "#8FB067", 1, rot, "#6E8F4A", 1.5))

    # shop body
    body.append('<ellipse cx="500" cy="704" rx="370" ry="26" fill="#4A2B1D" opacity="0.13"/>')
    body.append('<rect x="178" y="194" width="644" height="510" rx="26" fill="#F7D3D9" stroke="#5A3524" stroke-width="5"/>')
    body.append('<rect x="198" y="214" width="604" height="470" rx="18" fill="#FBE2E5" opacity="0.55"/>')

    # awning
    body.append('<rect x="150" y="168" width="700" height="92" rx="24" fill="#FFF9F0" stroke="#5A3524" stroke-width="5"/>')
    stripes = 10
    start_x = 166
    stripe_w = 668 / stripes
    for i in range(stripes):
        if i % 2 == 0:
            body.append(
                f'<rect x="{start_x + i * stripe_w:.1f}" y="174" width="{stripe_w:.1f}" height="58" fill="#E88CA2"/>'
            )
    for i in range(stripes):
        cx = start_x + i * stripe_w + stripe_w / 2
        body.append(
            f'<path d="M {cx - stripe_w / 2:.1f} 232 Q {cx:.1f} 276 {cx + stripe_w / 2:.1f} 232 Z" '
            f'fill="{"#E88CA2" if i % 2 == 0 else "#FFF9F0"}" stroke="#5A3524" stroke-width="3"/>'
        )
    body.append('<rect x="160" y="246" width="680" height="8" rx="4" fill="#E9B872" opacity="0.7"/>')

    # hanging sign
    body.append('<path d="M 372 96 V 146 M 628 96 V 146" stroke="#5A3524" stroke-width="4"/>')
    body.append('<rect x="322" y="132" width="356" height="92" rx="18" fill="#FFF9F0" stroke="#5A3524" stroke-width="5" filter="url(#soft)"/>')
    body.append('<circle cx="368" cy="178" r="24" fill="#D9A05E"/>')
    body.append(dot(360, 172, 4, BROWN))
    body.append(dot(376, 184, 3.4, BROWN))
    body.append(dot(358, 186, 3, BROWN))
    body.append('<text x="500" y="172" text-anchor="middle" font-family="Georgia, serif" font-size="25" font-weight="700" fill="#5A3524" letter-spacing="4">COOKIE NOOK</text>')
    body.append('<text x="500" y="200" text-anchor="middle" font-family="Verdana, sans-serif" font-size="11" font-weight="700" fill="#C98B58" letter-spacing="5">BAKERY &amp; CO.</text>')

    # window
    body.append('<rect x="222" y="330" width="312" height="272" rx="22" fill="#5A3524"/>')
    body.append('<rect x="234" y="342" width="288" height="248" rx="15" fill="#CFEAF5"/>')
    body.append('<rect x="234" y="342" width="288" height="248" rx="15" fill="url(#about-sun)" opacity="0.12"/>')
    # interior shelves
    body.append('<rect x="252" y="372" width="252" height="8" rx="4" fill="#FFF9F0" opacity="0.9"/>')
    body.append('<rect x="252" y="460" width="252" height="8" rx="4" fill="#FFF9F0" opacity="0.9"/>')
    body.append('<rect x="252" y="546" width="252" height="8" rx="4" fill="#FFF9F0" opacity="0.9"/>')
    for i, (vx, vy) in enumerate(((288, 358), (342, 358), (398, 358), (452, 358),
                                  (292, 446), (348, 446), (406, 446), (460, 446),
                                  (300, 532), (362, 532), (426, 532))):
        add_cookie(("classic", "strawberry", "pistachio", "oat")[i % 4], vx, vy, 19, i * 17 - 20, 20 + i)
    # window mullions
    body.append('<rect x="372" y="342" width="10" height="248" fill="#5A3524"/>')
    body.append('<rect x="234" y="408" width="288" height="6" fill="#5A3524" opacity="0.7"/>')
    body.append('<rect x="222" y="330" width="312" height="272" rx="22" fill="none" stroke="#5A3524" stroke-width="5"/>')
    body.append('<path d="M 212 310 H 544" stroke="#5A3524" stroke-width="4" stroke-linecap="round"/>')

    # small window awning
    for i in range(6):
        sx = 236 + i * 46
        body.append(f'<path d="M {sx} 298 h 46 v 14 a 23 14 0 0 1 -46 0 Z" fill="{"#E88CA2" if i % 2 == 0 else "#FFF9F0"}" stroke="#5A3524" stroke-width="2.5"/>')

    # door
    body.append('<rect x="590" y="338" width="196" height="366" rx="18" fill="#5A3524"/>')
    body.append('<rect x="604" y="352" width="168" height="338" rx="10" fill="#A9643A"/>')
    body.append('<rect x="620" y="372" width="136" height="132" rx="8" fill="#CFEAF5" stroke="#FFF6E5" stroke-width="4"/>')
    body.append('<path d="M 632 486 L 694 400 L 744 486 Z" fill="#FFF6E5" opacity="0.32"/>')
    body.append('<rect x="620" y="526" width="136" height="8" rx="4" fill="#E9B872" opacity="0.8"/>')
    body.append('<rect x="620" y="560" width="136" height="8" rx="4" fill="#E9B872" opacity="0.5"/>')
    body.append('<circle cx="746" cy="560" r="8" fill="#E9B872" stroke="#5A3524" stroke-width="3"/>')
    body.append('<rect x="606" y="628" width="164" height="10" rx="5" fill="#5A3524"/>')
    body.append('<rect x="590" y="338" width="196" height="366" rx="18" fill="none" stroke="#5A3524" stroke-width="5"/>')
    body.append('<text x="682" y="662" text-anchor="middle" font-family="Verdana, sans-serif" font-size="11" font-weight="700" fill="#FFF6E5" letter-spacing="2" opacity="0.8">OPEN</text>')

    # welcome mat
    body.append('<rect x="612" y="702" width="152" height="18" rx="9" fill="#E88CA2" stroke="#5A3524" stroke-width="3"/>')
    body.append('<path d="M 630 711 h 116" stroke="#FFF9F0" stroke-width="2" stroke-dasharray="8 7"/>')

    # plants by door
    for px in (842,):
        body.append(f'<ellipse cx="{px}" cy="694" rx="42" ry="14" fill="#4A2B1D" opacity="0.13"/>')
        body.append(f'<path d="M {px - 30} 640 h 60 l -8 56 h -44 Z" fill="#E9B872" stroke="#5A3524" stroke-width="3"/>')
        for lx, ly, rot in ((px - 18, 604, -24), (px + 14, 594, 18), (px - 2, 620, -2), (px - 34, 620, -54), (px + 34, 618, 48)):
            body.append(ellipse(lx, ly, 25, 10, "#8FB067", 1, rot, "#6E8F4A", 1.4))

    # cat
    body.append('<ellipse cx="872" cy="700" rx="50" ry="10" fill="#4A2B1D" opacity="0.15"/>')
    body.append('<path d="M 838 692 q 34 -104 78 -58 q 16 6 8 58 Z" fill="#E9B872" stroke="#5A3524" stroke-width="3"/>')
    body.append('<path d="M 844 646 l -6 -30 l 24 16 Z" fill="#E9B872" stroke="#5A3524" stroke-width="3"/>')
    body.append('<path d="M 894 636 l 8 -28 l -24 18 Z" fill="#E9B872" stroke="#5A3524" stroke-width="3"/>')
    body.append('<circle cx="869" cy="640" r="3" fill="#5A3524"/><circle cx="889" cy="638" r="3" fill="#5A3524"/>')
    body.append('<path d="M 874 647 q 4 4 8 0" stroke="#5A3524" stroke-width="2" fill="none" stroke-linecap="round"/>')
    body.append('<path d="M 914 682 q 28 -8 18 -30" stroke="#5A3524" stroke-width="8" fill="none" stroke-linecap="round"/>')
    body.append('<path d="M 856 676 h 8 M 868 676 h 8 M 880 676 h 8" stroke="#C98B58" stroke-width="2" opacity="0.8"/>')

    # details: birds / hearts / string lights
    body.append('<path d="M 224 168 Q 300 196 376 168 M 624 168 Q 700 196 776 168" stroke="#5A3524" stroke-width="2.5" fill="none" opacity="0.55"/>')
    for lx in (232, 272, 312, 352, 664, 704, 744, 784):
        body.append(dot(lx, 162, 4, "#FFF9F0", 0.9))
        body.append(dot(lx, 162, 2.2, "#F7C96B", 1))
    body.append(heart(138, 244, 12, PINK_STRONG, 0.65, -10))
    body.append(heart(868, 262, 9, PINK_STRONG, 0.55, 12))
    body.append(star(920, 370, 12, GOLD, 0.9))
    body.append(star(84, 400, 9, GOLD, 0.75))
    # bird
    body.append('<path d="M 756 262 q 12 -12 24 0 q 12 -12 24 0" fill="none" stroke="#5A3524" stroke-width="3" stroke-linecap="round" opacity="0.6"/>')

    body.append(grain_rect(1000, 820, 0.03))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 820" width="1000" height="820" role="img">
{base_defs("".join(defs))}
{"".join(body)}
{''.join(pieces)}
</svg>
'''


# --------------------------------------------------------------------------
# favicon
# --------------------------------------------------------------------------
def favicon():
    defs, cookie_markup = cookie("classic", 32, 34, 24, rotate=-8, seed=17, uid="fav")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
<defs>
  <linearGradient id="fav-bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#FFF9F0"/><stop offset="1" stop-color="#F9D7DE"/>
  </linearGradient>
</defs>
<rect width="64" height="64" rx="16" fill="url(#fav-bg)"/>
{cookie_markup}
{star(50, 15, 4.5, "#E9B872", 0.95)}
</svg>
'''


# --------------------------------------------------------------------------
# write files
# --------------------------------------------------------------------------
FILES = {
    "hero-cookies.svg": hero,
    "about-bakery.svg": about,
    "favicon.svg": favicon,
}

for variant in VARIANTS:
    FILES[f"cookie-{variant}.svg"] = (lambda v=variant: product(v))

for filename, builder in FILES.items():
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(builder())
    print("wrote", filename)
