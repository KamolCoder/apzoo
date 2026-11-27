"""Animal Planet mascot: a flat vector giraffe built from parts, posed by rotating them.

One rig, two outputs:
  * static files — static/mascot/giraffe-<pose>.svg (+ -mono.svg, one colour = currentColor), see make_mascot;
  * the inline rig for the site — templates/includes/mascot_rig.svg: every part and variant (eyes, mouth,
    accessories) in one SVG, poses switched by a class on the <svg> (CSS transitions move the parts).

Canvas 640×1000, ground line y=960, the giraffe faces left. Parts and pivots are in canvas coordinates.
"""
W, H, GROUND = 640, 1000, 960
HEAD_SCALE = 1.32   # the head is drawn small and scaled up around the neck top: a friendlier mascot
FIG_SCALE = 0.86    # the whole figure, around the ground centre: leaves headroom for the hat and the jump

PALETTE = {
    "body": "#F07F1B",     # main orange (brand)
    "far": "#D86A10",      # legs / ear on the far side
    "spot": "#B9520A",     # spots, mane
    "cream": "#F3EFE7",    # muzzle, inner ear
    "ink": "#111111",      # eyes, hooves, ossicone tips, lines
    "white": "#FFFFFF",    # eye highlight
    "red": "#D7261E",      # hat, scarf
    "green": "#3BAA4A",
    "pink": "#FF5FA2",
    "yellow": "#FFD23F",
    "violet": "#9B6BFF",
}
# mono version: everything visible is the silhouette (white in the mask), details are cut out (black)
MONO = {"body": "#fff", "far": "#fff", "spot": "#000", "cream": "#fff", "ink": "#000", "white": "#fff",
        "red": "#fff", "green": "#fff", "pink": "#fff", "yellow": "#fff", "violet": "#fff",
        "hoof": "#fff", "tip": "#fff", "band": "#000"}

# pivots
P_NECK = (300, 600)
P_HEAD = (214, 214)
P_EAR = (246, 134)
P_TAIL = (528, 598)
P_LEG = {"fn": (282, 652), "ff": (330, 652), "bf": (452, 660), "bn": (500, 660)}

# pose → part → (rotate°, translate (x, y), scale (x, y))
POSES = {
    "idle": {},
    "stretch": {"neck": (7, (0, 0), (1, 1.07)), "head": (-10, (0, 0), (1, 1)), "ear": (24, (0, 0), (1, 1))},
    "talk": {"head": (-12, (0, 0), (1, 1)), "neck": (3, (0, 0), (1, 1)), "leg-fn": (32, (0, 0), (1, 1))},
    "win": {"all": (0, (0, -70), (1, 1)), "leg-fn": (38, (0, 0), (1, 1)), "leg-ff": (28, (0, 0), (1, 1)),
            "leg-bf": (-28, (0, 0), (1, 1)), "leg-bn": (-38, (0, 0), (1, 1)), "tail": (-48, (0, 0), (1, 1)),
            "head": (-8, (0, 0), (1, 1)), "ear": (20, (0, 0), (1, 1))},
    "sleep": {"neck": (-10, (0, 0), (1, 1)), "head": (30, (0, 0), (1, 1)), "ear": (38, (0, 0), (1, 1)),
              "tail": (8, (0, 0), (1, 1))},
    "wave": {"leg-fn": (128, (0, 0), (1, 1)), "head": (-4, (0, 0), (1, 1))},
}
PIVOT = {"all": (W / 2, GROUND), "neck": P_NECK, "head": P_HEAD, "ear": P_EAR, "tail": P_TAIL,
         **{f"leg-{k}": v for k, v in P_LEG.items()}}
# which face / extras a pose shows
FACE = {"idle": ("open", "smile"), "stretch": ("happy", "smile"), "talk": ("open", "open"),
        "win": ("happy", "open"), "sleep": ("closed", "none"), "wave": ("open", "smile")}
FILES = {  # file → (pose, accessories)
    "idle": ("idle", ()), "stretch": ("stretch", ()), "talk": ("talk", ()), "win": ("win", ()),
    "sleep": ("sleep", ("zzz",)), "newyear": ("idle", ("hat", "scarf")), "navruz": ("idle", ("flowers", "wreath")),
    "wave": ("wave", ()),
}


def _fmt(n):
    return f"{n:g}"


def svg_transform(part, pose):
    """SVG transform attribute for a part in a pose ('' when it does not move)."""
    rot, (tx, ty), (sx, sy) = POSES[pose].get(part, (0, (0, 0), (1, 1)))
    if not rot and not tx and not ty and sx == sy == 1:
        return ""
    px, py = PIVOT[part]
    out = []
    if tx or ty:
        out.append(f"translate({_fmt(tx)} {_fmt(ty)})")
    if rot:
        out.append(f"rotate({_fmt(rot)} {_fmt(px)} {_fmt(py)})")
    if sx != 1 or sy != 1:
        out.append(f"translate({_fmt(px)} {_fmt(py)}) scale({_fmt(sx)} {_fmt(sy)}) translate({_fmt(-px)} {_fmt(-py)})")
    return f' transform="{" ".join(out)}"'


SEASON_ACCESSORIES = {"newyear": ("hat", "scarf"), "navruz": ("flowers", "wreath"), "night": ("zzz",)}


def css_rules(scope=".mascot"):
    """CSS for the inline rig. The pose / season classes (is-stretch, is-newyear…) sit on an ancestor of the svg."""
    r = [f"{scope} .m-part{{transform-box:view-box;transition:transform .45s cubic-bezier(.3,1.4,.5,1)}}"]
    for part, (px, py) in PIVOT.items():
        r.append(f"{scope} .m-{part}{{transform-origin:{_fmt(px)}px {_fmt(py)}px}}")
    for pose, parts in POSES.items():
        for part, (rot, (tx, ty), (sx, sy)) in parts.items():
            t = []
            if tx or ty:
                t.append(f"translate({_fmt(tx)}px,{_fmt(ty)}px)")
            if rot:
                t.append(f"rotate({_fmt(rot)}deg)")
            if sx != 1 or sy != 1:
                t.append(f"scale({_fmt(sx)},{_fmt(sy)})")
            r.append(f".is-{pose} {scope} .m-{part}{{transform:{' '.join(t)}}}")
    r.append(f"{scope} .m-eyes,{scope} .m-mouth,{scope} .m-acc{{display:none}}")
    r.append(f"{scope} .m-eyes-open,{scope} .m-mouth-smile{{display:inline}}")
    for pose, (eyes, mouth) in FACE.items():
        r.append(f".is-{pose} {scope} .m-eyes,.is-{pose} {scope} .m-mouth{{display:none}}")
        r.append(f".is-{pose} {scope} .m-eyes-{eyes},.is-{pose} {scope} .m-mouth-{mouth}{{display:inline}}")
    for season, accs in SEASON_ACCESSORIES.items():
        ctx = ".is-night.is-sleep" if season == "night" else f".is-{season}"  # «Zzz» only while asleep
        r.append(",".join(f"{ctx} {scope} .m-acc-{a}" for a in accs) + "{display:inline}")
    r.append(f"@media (prefers-reduced-motion:reduce){{{scope} .m-part{{transition:none}}}}")
    return "".join(r)


# ── parts ─────────────────────────────────────────────────────────────────────

def _leg(cx, fill, c):
    top, knee, hoof = 640, 800, GROUND - 26
    return (f'<path fill="{c[fill]}" d="M{cx - 23} {top}H{cx + 23}L{cx + 15} {knee}Q{cx + 19} {knee + 12} {cx + 14} {knee + 24}'
            f'L{cx + 13} {hoof}H{cx - 13}L{cx - 14} {knee + 24}Q{cx - 19} {knee + 12} {cx - 15} {knee}Z"/>'
            f'<path fill="{c.get("hoof", c["ink"])}" d="M{cx - 15} {hoof}H{cx + 15}L{cx + 17} {GROUND}H{cx - 17}Z"/>')


def _spots(c, items):
    return "".join(f'<path fill="{c["spot"]}" stroke="{c["spot"]}" stroke-width="9" stroke-linejoin="round" d="{d}"/>'
                   for d in items)


BODY = "M246 612C240 552 286 516 342 514L472 540C518 550 540 584 534 628C528 674 506 704 460 708H302C266 708 248 684 246 650Z"
NECK = "M244 624C232 484 200 320 186 170L240 156C262 316 302 470 350 588Z"
HEAD = "M258 152C258 116 228 100 196 108L128 128C98 137 84 160 90 184C96 208 124 216 150 210L216 202C246 198 260 182 258 152Z"


def build(pose="idle", accessories=(), mono=False, rig=False, uid="g"):
    """One SVG. rig=True: every variant present, poses by CSS classes (no baked transforms)."""
    c = dict(PALETTE)
    if mono:
        c.update(MONO)
    tr = (lambda part: "") if rig else (lambda part: svg_transform(part, pose))
    cls = (lambda part: f' class="m-part m-{part}"') if rig else (lambda part: "")
    eyes, mouth = FACE.get(pose, FACE["idle"])
    show = (lambda kind, name: True) if rig else (lambda kind, name: (eyes if kind == "eyes" else mouth) == name)

    def leg(key, cx, fill):
        return f'<g{cls("leg-" + key)}{tr("leg-" + key)}>{_leg(cx, fill, c)}</g>'

    def acc(name, body):
        if rig:
            return f'<g class="m-acc m-acc-{name}">{body}</g>'
        return body if name in accessories else ""

    # eyes / mouth variants (in head coordinates)
    face = []
    if show("eyes", "open"):
        face.append(f'<g class="m-eyes m-eyes-open"><ellipse cx="190" cy="146" rx="11" ry="13" fill="{c["ink"]}"/>'
                    f'<circle cx="194" cy="141" r="4" fill="{c["white"]}"/></g>')
    if show("eyes", "happy"):
        face.append(f'<g class="m-eyes m-eyes-happy"><path d="M178 150Q190 134 202 150" fill="none" stroke="{c["ink"]}" '
                    f'stroke-width="6" stroke-linecap="round"/></g>')
    if show("eyes", "closed"):
        face.append(f'<g class="m-eyes m-eyes-closed"><path d="M178 146Q190 158 202 146" fill="none" stroke="{c["ink"]}" '
                    f'stroke-width="6" stroke-linecap="round"/></g>')
    if show("mouth", "smile"):
        face.append(f'<g class="m-mouth m-mouth-smile"><path d="M101 190Q118 202 138 194" fill="none" stroke="{c["ink"]}" '
                    f'stroke-width="5" stroke-linecap="round"/></g>')
    if show("mouth", "open"):
        face.append(f'<g class="m-mouth m-mouth-open"><path d="M100 188Q119 196 140 190Q136 210 118 210Q104 208 100 188Z" '
                    f'fill="{c["ink"]}"/></g>')
    if rig:
        face.append('<g class="m-mouth m-mouth-none"></g>')

    head = (
        f'<g{cls("head")}{tr("head")}><g transform="translate(214 214) scale({HEAD_SCALE}) translate(-214 -214)">'
        # far ear, ossicones, near ear
        f'<g{cls("ear")}{tr("ear")}><path fill="{c["far"]}" d="M240 118C262 92 292 86 308 90C298 108 270 124 244 128Z"/></g>'
        f'<path fill="{c["body"]}" d="M199 113L195 70H209L213 111Z"/><circle cx="202" cy="64" r="11" fill="{c.get("tip", c["ink"])}"/>'
        f'<path fill="{c["body"]}" d="M229 107L232 64H246L243 106Z"/><circle cx="239" cy="58" r="11" fill="{c.get("tip", c["ink"])}"/>'
        f'<clipPath id="{uid}-hc"><path d="{HEAD}"/></clipPath>'
        f'<path fill="{c["body"]}" d="{HEAD}"/>'
        f'<g clip-path="url(#{uid}-hc)"><ellipse cx="114" cy="172" rx="36" ry="46" fill="{c["cream"]}"/>'
        f'<path fill="{c["spot"]}" d="M232 168C246 160 262 166 262 182L262 214L222 214C220 196 222 176 232 168Z"/></g>'
        f'<ellipse cx="103" cy="160" rx="5" ry="7" fill="{c["ink"]}" transform="rotate(-20 103 160)"/>'
        + "".join(face) +
        f'<g{cls("ear")}{tr("ear")}><path fill="{c["body"]}" d="M246 130C270 112 302 108 318 114C306 132 276 146 250 146Z"/>'
        f'<path fill="{c["cream"]}" d="M256 133C274 122 294 119 306 121C296 132 276 140 258 141Z"/></g>'
        + acc("wreath",
              "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{c[col]}"/><circle cx="{x}" cy="{y}" r="3.5" fill="{c["yellow"] if col != "yellow" else c["pink"]}"/>'
                      for x, y, col in [(182, 116, "pink"), (198, 108, "yellow"), (216, 106, "violet"),
                                        (234, 103, "pink"), (252, 104, "yellow"), (268, 112, "violet")]))
        + acc("hat",
              f'<path fill="{c["red"]}" d="M174 122C182 80 214 46 252 40C278 36 302 46 308 66C294 60 278 64 272 76C266 86 264 98 264 108Z"/>'
              f'<circle cx="310" cy="68" r="13" fill="{c["white"] if not mono else c["body"]}"/>'
              f'<rect x="166" y="106" width="106" height="22" rx="11" fill="{c["white"] if not mono else c["band"]}" transform="rotate(-11 219 117)"/>')
        + "</g></g>"
    )

    neck = (
        f'<g{cls("neck")}{tr("neck")}>'
        f'<clipPath id="{uid}-nc"><path d="{NECK}"/></clipPath>'
        f'<path fill="{c["body"]}" d="{NECK}"/>'
        f'<g clip-path="url(#{uid}-nc)">'
        + _spots(c, ["M214 286L236 280L244 304L224 316L210 304Z", "M226 352L252 344L262 372L240 386L224 372Z",
                     "M238 428L268 420L280 452L256 468L238 452Z", "M258 506L290 498L304 532L278 550L258 534Z",
                     "M200 236L220 232L226 250L208 258Z"])
        + f'<path fill="{c["spot"]}" d="M240 156C262 316 302 470 350 588L364 578C318 466 280 316 258 152Z"/></g>'
        + acc("scarf",
              f'<path fill="{c["red"]}" stroke="{c["red"]}" stroke-width="6" stroke-linejoin="round" d="M188 288L268 266L276 302L196 326Z"/>'
              f'<path fill="{c["red"]}" stroke="{c["red"]}" stroke-width="6" stroke-linejoin="round" d="M238 300L264 296L282 392L256 398Z"/>'
              f'<path fill="{c["white"] if not mono else c["band"]}" d="M210 281L224 277L232 314L218 318ZM242 273L256 269L262 304L250 308ZM246 336L270 332L273 348L249 352Z"/>')
        + head + "</g>"
    )

    body = (
        f'<clipPath id="{uid}-bc"><path d="{BODY}"/></clipPath>'
        f'<path fill="{c["body"]}" d="{BODY}"/>'
        f'<g clip-path="url(#{uid}-bc)">'
        + _spots(c, ["M296 548L338 538L352 576L322 600L292 584Z", "M372 556L414 560L420 598L384 612L364 590Z",
                     "M444 572L486 580L490 618L456 630L438 608Z", "M318 626L360 620L372 660L338 680L310 662Z",
                     "M398 636L440 640L446 680L408 694L390 670Z", "M478 650L520 646L530 690L494 702Z",
                     "M262 640L284 632L292 668L266 686Z"])
        + "</g>"
    )

    tail = (f'<g{cls("tail")}{tr("tail")}><path d="M528 598C548 630 560 670 562 712" fill="none" stroke="{c["body"]}" '
            f'stroke-width="9" stroke-linecap="round"/><path fill="{c["ink"] if not mono else c["body"]}" '
            f'd="M562 700C574 712 578 736 566 756C552 744 546 718 562 700Z"/></g>')

    flowers = acc("flowers", "".join(
        f'<path d="M{x} {GROUND}V{GROUND - h}" stroke="{c["green"]}" stroke-width="5" stroke-linecap="round"/>'
        f'<path fill="{c["green"]}" d="M{x} {GROUND - 8}C{x - 16} {GROUND - 18} {x - 18} {GROUND - 34} {x - 14} {GROUND - 44}C{x - 4} {GROUND - 30} {x} {GROUND - 20} {x} {GROUND - 8}Z"/>'
        f'<path fill="{c[col]}" d="M{x - 13} {GROUND - h}C{x - 14} {GROUND - h - 22} {x - 8} {GROUND - h - 30} {x - 6} {GROUND - h - 30}L{x} {GROUND - h - 20}'
        f'L{x + 6} {GROUND - h - 30}C{x + 8} {GROUND - h - 30} {x + 14} {GROUND - h - 22} {x + 13} {GROUND - h}C{x + 10} {GROUND - h + 10} {x - 10} {GROUND - h + 10} {x - 13} {GROUND - h}Z"/>'
        for x, h, col in [(52, 62, "red"), (96, 44, "yellow"), (140, 70, "pink"), (380, 50, "violet"),
                          (566, 66, "red"), (606, 46, "yellow")]))

    # back to front: far legs, tail, near legs, neck (+ head), body — the body hides every joint
    inner = (
        leg("ff", 330, "far") + leg("bf", 452, "far") + tail
        + leg("fn", 282, "body") + leg("bn", 500, "body") + neck + body
    )
    zzz = acc("zzz", "".join(
        f'<text x="{x}" y="{y}" font-family="Unbounded, Arial Black, sans-serif" font-weight="700" font-size="{fs}" '
        f'fill="{c["body"]}">{t}</text>' for x, y, fs, t in [(232, 204, 40, "z"), (262, 160, 52, "z"), (300, 104, 68, "Z")]))
    inner = (f'<g{cls("all")}{tr("all")}><g transform="translate({W / 2:g} {GROUND}) scale({FIG_SCALE}) translate({-W / 2:g} {-GROUND})">'
             f'{inner}</g></g>' + flowers + zzz)

    attrs = f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"'
    if mono:
        return (f'<svg {attrs}><mask id="{uid}-m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                f'{inner}</mask><rect width="{W}" height="{H}" fill="currentColor" mask="url(#{uid}-m)"/></svg>')
    if rig:
        return (f'<svg {attrs} class="mascot" aria-hidden="true" focusable="false"><style>{css_rules()}</style>'
                f'{inner}</svg>')
    return f"<svg {attrs}>{inner}</svg>"


def portrait(mono=False, uid="h"):
    """Head + upper neck in a 640×640 square (avatars, stickers)."""
    inner = build("idle", mono=mono, uid=uid)
    body = inner[inner.index(">") + 1:inner.rindex("</svg>")]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="62 96 300 300">{body}</svg>')


def all_files():
    """{filename: svg} for static/mascot/."""
    out = {}
    for name, (pose, acc) in FILES.items():
        out[f"giraffe-{name}.svg"] = build(pose, acc, uid=f"g{name[:3]}")
        out[f"giraffe-{name}-mono.svg"] = build(pose, acc, mono=True, uid=f"m{name[:3]}")
    out["giraffe-head.svg"] = portrait(uid="hd")
    out["giraffe-head-mono.svg"] = portrait(mono=True, uid="hm")
    return out


def rig():
    return build(rig=True, uid="rig")


__all__ = ["build", "rig", "all_files", "css_rules", "POSES", "FILES"]
