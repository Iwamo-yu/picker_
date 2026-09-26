"""
Dimensioned 2D engineering views (top / front / side / approach-angle detail) and the
functional + electrical block diagrams.  Dimension text colour = data confidence:
  green  = standard / manufacturer      blue = derived / design choice
  amber  = approximate envelope         red  = PLACEHOLDER, measure on the real IX73

    python cad/views.py  -> docs/img/*.png + *.svg
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import params as p  # noqa: E402
from model import Z_PICK, build, head_geometry, well_xy  # noqa: E402

WF = p.DEFAULT_WORKFLOW                       # dimensioned views show the baseline workflow
WFL = {"WA": "W-A", "WB": "W-B"}[WF]
ARM_L = p.layout(WF)["arm_l"]

IMG = os.path.join(os.path.dirname(__file__), "..", "docs", "img")
os.makedirs(IMG, exist_ok=True)
SC = {"STD": "#2f7d4f", "MFR": "#2f7d4f", "DER": "#3a64b0", "DES": "#3a64b0", "APX": "#b7791f", "PH": "#c0392f"}
FILL = {"ix73": "#cfd6d9", "condenser": "#b9aee0", "frame": "#7f98aa", "actuator": "#5f97ae", "motor": "#4a555b",
        "moving": "#6cc39f", "holder": "#2f8f6d", "plate": "#eef3f5", "pump": "#b0b4b7", "electronics": "#9aa7ae",
        "switch": "#e0a84a", "cable": "#9aa3a8", "tubing": "#e7b92f", "table": "#e9eced", "capillary": "#38c4d8"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})


def bbox(s):
    b = s.bounding_box()
    return b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z


def dim(ax, a, b, text, status, off=(0, 0), fs=7.5, rot=0):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="<->", color=SC[status], lw=0.9))
    mx, my = (a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1]
    ax.text(mx, my, text, color=SC[status], fontsize=fs, ha="center", va="center", rotation=rot,
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))


def label(ax, x, y, text, status, ha="left", fs=7.5):
    ax.text(x, y, text, color=SC[status], fontsize=fs, ha=ha, va="center",
            bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.85))


def legend(ax, loc="lower left"):
    from matplotlib.lines import Line2D
    h = [Line2D([0], [0], color=SC["STD"], lw=3, label="standard / manufacturer data"),
         Line2D([0], [0], color=SC["DER"], lw=3, label="derived / design choice"),
         Line2D([0], [0], color=SC["APX"], lw=3, label="approximate catalogue envelope"),
         Line2D([0], [0], color=SC["PH"], lw=3, label="PLACEHOLDER - measure on real IX73"),
         Rectangle((0, 0), 1, 1, fc="white", ec=SC["PH"], hatch="////", label="part whose geometry is placeholder")]
    ax.legend(handles=h, loc=loc, fontsize=7, framealpha=0.95)


def draw_parts(ax, m, proj, pose=(0, 0, 0), skip=(), ghost=()):
    """proj: 'xy' | 'xz' | 'yz'.  Draws bounding-box outlines ordered by depth."""
    from model import posed
    items = []
    for q, s in posed(m, *pose):
        if q.category in skip or q.category in ("tubing", "capillary", "zone"):
            continue
        x0, y0, z0, x1, y1, z1 = bbox(s)
        if proj == "xy":
            r, depth = (x0, y0, x1 - x0, y1 - y0), z1
        elif proj == "xz":
            r, depth = (x0, z0, x1 - x0, z1 - z0), -y0
        else:
            r, depth = (y0, z0, y1 - y0, z1 - z0), x1
        items.append((depth, q, r))
    items.sort(key=lambda t: t[0])
    for _, q, r in items:
        if q.category == "plate":
            continue
        if q.name in ghost:
            ax.add_patch(Rectangle(r[:2], r[2], r[3], fc="none", ec=SC["PH"], lw=0.9, ls="--"))
            continue
        cyl = q.name.startswith("condenser_I") or q.name == "ix73_objective_zone"
        if proj == "xy" and cyl:
            ax.add_patch(Circle((r[0] + r[2] / 2, r[1] + r[3] / 2), r[2] / 2, fc=FILL.get(q.category, "#ddd"),
                                ec="#333", lw=0.5, alpha=0.9, hatch="////" if q.status == "PH" else None))
            continue
        ax.add_patch(Rectangle(r[:2], r[2], r[3], fc=FILL.get(q.category, "#ddd"), ec="#333", lw=0.5,
                               alpha=0.9 if q.category != "table" else 0.5,
                               hatch="////" if q.status == "PH" and q.category != "table" else None))


def capillary_line(ax, proj, theta, pose=(0, 0, 0)):
    hg = head_geometry(theta)
    t, c = hg["tip"], hg["cap_top"]
    n, h = hg["nose"], hg["hold_top"]
    dx, dy, dz = pose
    if proj == "xz":
        ax.plot([t[0] + dx, c[0] + dx], [t[2] + dz, c[2] + dz], color="#1596a8", lw=1.4)
        ax.plot([n[0] + dx, h[0] + dx], [n[2] + dz, h[2] + dz], color=FILL["holder"], lw=5, solid_capstyle="butt")
    elif proj == "yz":
        ax.plot([dy, dy], [t[2] + dz, c[2] + dz], color="#1596a8", lw=1.4)


# ---------------------------------------------------------------------------- TOP
def top_view():
    m = build("R08", "IX-ULWCD", WF)
    fig, ax = plt.subplots(figsize=(13, 9.2))
    draw_parts(ax, m, "xy", skip=("table",))
    L, W = p.PLATE_L.v, p.PLATE_W.v
    ax.add_patch(Rectangle((-L / 2, -W / 2), L, W, fc=FILL["plate"], ec="#222", lw=1.0))
    for r in range(8):
        for c in range(12):
            x, y = well_xy(r, c)
            ax.add_patch(Circle((x, y), p.WELL_D_TOP.v / 2, fc="white", ec="#555", lw=0.4))
            ax.plot(x, y, ".", color="#0f7483", ms=2)
    LY = p.layout(WF)
    hx, hy = LY["travel_x"] / 2, LY["travel_y"] / 2
    ax.add_patch(Rectangle((LY["x_min"], LY["y_min"]), LY["travel_x"], LY["travel_y"], fc="none", ec="#3a64b0",
                           lw=1.4, ls="--"))
    ax.text(LY["x_min"] + 2, LY["y_max"] + 4, f"{WFL} capillary-tip XY travel {LY['travel_x']:.0f} x {LY['travel_y']:.0f}",
            color=SC["DES"], fontsize=7.5)
    ax.add_patch(Circle((0, 0), p.COND_D.v / 2 + 10, fc="none", ec=SC["PH"], lw=1, ls=":"))
    ax.text(-70, -62, "condenser keep-out\n(Ø80 PH + 10)", color=SC["PH"], ha="right", fontsize=7)
    # capillary + arm at reference pose
    ax.plot([0, ARM_L], [0, 0], color=FILL["moving"], lw=4)
    ax.plot(0, 0, "o", color="#1596a8", ms=4)
    # extreme arm positions (ghosts)
    for tx, ty in [(LY["x_min"], LY["y_max"]), (LY["x_max"], LY["y_min"])]:
        ax.plot([tx, tx + ARM_L], [ty, ty], color=FILL["moving"], lw=1.5, alpha=0.5, ls="--")
        ax.add_patch(Rectangle((tx + ARM_L, ty - 13), 30, 26, fc=FILL["actuator"], ec="#333", alpha=0.35, lw=0.5))
    # dims
    dim(ax, (-L / 2, -W / 2 - 14), (L / 2, -W / 2 - 14), "plate 127.76 (SLAS 1)", "STD")
    dim(ax, (-L / 2 - 14, -W / 2), (-L / 2 - 14, W / 2), "85.48", "STD", rot=90)
    x0, y0 = well_xy(0, 0)
    x1, y1 = well_xy(7, 11)
    dim(ax, (x0, W / 2 + 8), (x1, W / 2 + 8), "A1-A12 centres 99.0 (9 mm pitch)", "STD")
    dim(ax, (L / 2 + 10, y1), (L / 2 + 10, y0), "63.0", "STD", rot=90)
    label(ax, x0 - 4, y0 + 7, "A1", "STD", ha="right")
    dim(ax, (-p.STAGE_X.v / 2, -p.STAGE_Y.v / 2 - 12), (p.STAGE_X.v / 2, -p.STAGE_Y.v / 2 - 12),
        "stage 232 (MFR plain stage), position PH", "MFR")
    dim(ax, (-p.IX73_W.v / 2, p.BODY_Y_FRONT.v - 22), (p.IX73_W.v / 2, p.BODY_Y_FRONT.v - 22),
        "IX73 body W 323 (MFR); front face y=-235 PH", "MFR")
    dim(ax, (0, -hy - 30), (ARM_L, -hy - 30), f"dog-leg arm {ARM_L:.0f} (tip -> Z carriage)", "DES")
    tx = LY["tower_x"]
    dim(ax, (p.IX73_W.v / 2, 150), (tx, 150), f"{tx - p.IX73_W.v / 2:.0f} clear gap body -> tower axis", "DES")
    dim(ax, (0, 290), (tx + 90, 290), f"tower footprint reaches x = +{tx + 90:.0f} from optical axis", "DES")
    label(ax, 90, 60, "X support beam + X actuator (Y group)", "APX")
    label(ax, 410, -210, "posts + Y beam on base plate\n(bolted to optical table)", "DES")
    label(ax, 525, -140, "existing syringe pump\n(footprint PH)", "PH")
    label(ax, 0, 205, "illumination pillar + condenser arm (PH)", "PH", ha="center")
    label(ax, 0, -300, "observation tube / eyepieces envelope (PH)", "PH", ha="center")
    ax.set_xlim(-260, 800); ax.set_ylim(-420, 420); ax.set_aspect("equal")
    ax.set_xlabel("X (mm) - operator's right"); ax.set_ylabel("Y (mm) - away from operator")
    ax.set_title(f"TOP VIEW ({WFL}) - reference pose (tip on optical axis, well plate centred). Origin = optical axis.", fontsize=10)
    ax.grid(alpha=0.25); legend(ax, "lower right")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "dim_top.png"), dpi=150); fig.savefig(os.path.join(IMG, "dim_top.svg"))
    plt.close(fig)


# ---------------------------------------------------------------------------- FRONT
def front_view():
    m = build("R08", "IX-ULWCD", WF)
    fig, ax = plt.subplots(figsize=(13, 9.2))
    draw_parts(ax, m, "xz", ghost=("ix73_obs_tube_eyepieces",))
    capillary_line(ax, "xz", 8)
    label(ax, 75, -120, "dashed red = observation tube / eyepieces\n(in front of section, PH)", "PH", fs=7)
    T = -p.STAGE_TOP_ABOVE_TABLE.v
    # condenser alternatives
    for name, c in p.CONDENSERS.items():
        zc = p.WELL_BOTTOM_Z.v + c["WD"].v
        ax.plot([-60, 60], [zc, zc], color="#7d6aa8", lw=1, ls="-" if name == "IX-ULWCD" else "--")
        label(ax, -64, zc, f"{name} front, WD {c['WD'].v:.0f} (MFR) -> z={zc:.1f}", "MFR", ha="right", fs=7)
    # levels
    for z, zt, t, s in [(0, -24, "stage top / plate datum z=0 (height above table PH)", "PH"),
                        (p.PLATE_H.v, 8, "plate top 14.35 (SLAS 2)", "STD"),
                        (p.SAFE_Z_TIP.v, 24, f"tip safe-Z {p.SAFE_Z_TIP.v:.2f} (plate +5)", "DER"),
                        (p.WELL_BOTTOM_Z.v, -8, "well bottom ~3.05 (derived, plate specific)", "DER")]:
        ax.plot([80, 120, 128], [z, z, zt], color=SC[s], lw=0.8)
        label(ax, 131, zt, t, s, fs=7)
    dim(ax, (-230, T), (-230, 0), "table -> stage top 200 ?\nPLACEHOLDER (M1)", "PH", rot=90)
    dim(ax, (-200, T), (-200, T + p.IX73_H.v), "IX73 H 656 (MFR, incl. pillar)", "MFR", rot=90, off=(-12, 0))
    zb = Z_PICK + 30
    dim(ax, (ARM_L + 45, zb + 60), (ARM_L + 45, zb + 60 + p.layout(WF)["travel_z"]), f"Z stroke {p.layout(WF)['travel_z']:.0f}", "DES", rot=90, off=(8, 0))
    label(ax, ARM_L + 50, zb + 200, "Z actuator lead 1 mm (self-holding\nvia detent / brake option)", "APX")
    label(ax, 20, 64, "thin arm 12x12, runs under condenser", "DES")
    label(ax, 280, 205, f"X actuator {p.layout(WF)['travel_x']:.0f} stroke on stiff support beam", "APX")
    label(ax, 330, 120, f"Y actuator {p.layout(WF)['travel_y']:.0f} stroke\non fixed beam", "APX")
    ax.set_xlim(-330, 800); ax.set_ylim(T - 30, 520); ax.set_aspect("equal")
    ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm) above stage top")
    ax.set_title(f"FRONT VIEW ({WFL}, from operator, -Y) - 8° near-vertical dog-leg head under IX-ULWCD, tip at pick height",
                 fontsize=10)
    ax.grid(alpha=0.25); legend(ax, "upper right")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "dim_front.png"), dpi=150); fig.savefig(os.path.join(IMG, "dim_front.svg"))
    plt.close(fig)


# ---------------------------------------------------------------------------- SIDE (section at x=0)
def side_view():
    m = build("R08", "IX-ULWCD", WF)
    fig, ax = plt.subplots(figsize=(13, 9.2))
    # only parts that cross the x=0 plane +- 60 mm, plus the tower for reference (ghost)
    from model import posed
    for q, s in posed(m):
        if q.category in ("tubing", "capillary", "table"):
            continue
        x0, y0, z0, x1, y1, z1 = bbox(s)
        near = x0 < 60 and x1 > -60
        if not near and q.group == "fixed" and q.category not in ("frame",):
            continue
        a = 0.9 if near else 0.18
        ax.add_patch(Rectangle((y0, z0), y1 - y0, z1 - z0, fc=FILL.get(q.category, "#ddd"), ec="#333", lw=0.5,
                               alpha=a, hatch="////" if q.status == "PH" and near else None))
    capillary_line(ax, "yz", 8)
    T = -p.STAGE_TOP_ABOVE_TABLE.v
    ax.plot([-600, 600], [T, T], color="#555", lw=1)
    hy = p.layout(WF)["travel_y"] / 2
    dim(ax, (-hy, -30), (hy, -30), f"{WFL} tip Y travel {2 * hy:.0f}", "DES")
    dim(ax, (-p.PLATE_W.v / 2, -48), (p.PLATE_W.v / 2, -48), "plate 85.48", "STD")
    dim(ax, (p.BODY_Y_FRONT.v, T - 15), (p.BODY_Y_FRONT.v + p.IX73_D.v, T - 15), "IX73 body D 475 (MFR); position PH", "MFR")
    zc = p.WELL_BOTTOM_Z.v + 73
    dim(ax, (-70, p.WELL_BOTTOM_Z.v), (-70, zc), "WD 73 (IX-ULWCD, MFR)", "MFR", rot=90, off=(-9, 0))
    label(ax, 160, 330, "illumination pillar + condenser arm\n(section, position PH, M7-M10)", "PH")
    label(ax, -380, 60, "observation tube / eyepieces\n(PH, M12) - reason the frame\nis NOT a front bridge", "PH")
    label(ax, -380, 250, f"tower posts (ghosted, x = +{p.layout(WF)['tower_x']})", "DES")
    ax.set_xlim(-470, 480); ax.set_ylim(T - 40, 520); ax.set_aspect("equal")
    ax.set_xlabel("Y (mm) - away from operator"); ax.set_ylabel("Z (mm)")
    ax.set_title("SIDE SECTION at optical axis (x = 0, viewed from +X). Tower beyond section shown ghosted.", fontsize=10)
    ax.grid(alpha=0.25); legend(ax, "upper left")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "dim_side.png"), dpi=150); fig.savefig(os.path.join(IMG, "dim_side.svg"))
    plt.close(fig)


# ---------------------------------------------------------------------------- ANGLE DETAIL
def angle_detail():
    fig, axs = plt.subplots(1, 4, figsize=(15, 6.2), sharey=True)
    rt, rb, dep, top = p.WELL_D_TOP.v / 2, p.WELL_D_BOT.v / 2, p.WELL_DEPTH.v, p.PLATE_H.v
    wb = p.WELL_BOTTOM_Z.v
    for ax, th in zip(axs, (0, 8, 30, 45)):
        # plate section with 3 wells (x = -9, 0, 9)
        ax.add_patch(Rectangle((-16, 0), 32, top, fc="#dfe6e8", ec="none"))
        for cx in (-9, 0, 9):
            ax.add_patch(Polygon([(cx - rb, wb), (cx - rt, top), (cx + rt, top), (cx + rb, wb)], fc="white", ec="#555", lw=0.6))
        t = math.radians(th)
        # capillary with tip at well-bottom centre (shown in red if it violates the rim)
        from analysis import well_access
        a = well_access(th)
        L = p.CAP_EXPOSED.v
        tip = (0, wb + p.TIP_CLEAR_BOTTOM.v)
        end = (tip[0] + L * math.sin(t), tip[1] + L * math.cos(t))
        col = "#1596a8" if a["bottom_reachable_centre"] else "#c0392f"
        ax.plot([tip[0], end[0]], [tip[1], end[1]], color=col, lw=2.2)
        # holder
        h1 = (tip[0] + (L + p.HOLDER_L.v) * math.sin(t), tip[1] + (L + p.HOLDER_L.v) * math.cos(t))
        ax.plot([end[0], h1[0]], [end[1], h1[1]], color=FILL["holder"], lw=10, solid_capstyle="butt")
        # condenser fronts
        for name, c in p.CONDENSERS.items():
            zc = wb + c["WD"].v
            ax.plot([-40, 40], [zc, zc], color="#7d6aa8", lw=1, ls="-" if name == "IX-ULWCD" else "--")
            ax.text(-39, zc + 1, name, color="#7d6aa8", fontsize=6.5)
        # light cone NA 0.3
        h = 73
        r = h * math.tan(math.asin(0.3))
        ax.fill([0, -r, r], [wb, wb + h, wb + h], color="#f3e7a1", alpha=0.35, zorder=0)
        txt = (f"rim clearance {a['rim_clearance_centre']:+.2f} mm\nbottom centre reachable" if a["bottom_reachable_centre"]
               else f"hits rim; reaches only {a['max_centred_depth']:.1f} mm\nbelow rim")
        ax.set_title(f"{th}° from vertical" + ("  (recommended)" if th == 8 else ""), fontsize=10)
        ax.text(0, -6, txt, ha="center", fontsize=8, color=col)
        ax.set_xlim(-42, 42); ax.set_ylim(-12, 85); ax.set_aspect("equal"); ax.grid(alpha=0.2)
        ax.set_xlabel("mm")
    axs[0].set_ylabel("Z (mm) above plate datum")
    fig.suptitle("Capillary approach angle vs 96-well geometry (Corning 7007: rim Ø6.86, depth 11.30) and condenser fronts "
                 "(yellow = NA 0.3 illumination cone)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "approach_angles.png"), dpi=150)
    fig.savefig(os.path.join(IMG, "approach_angles.svg")); plt.close(fig)


# ---------------------------------------------------------------------------- DIAGRAMS
def boxes(ax, spec, arrows):
    pos = {}
    for key, (x, y, w, h, text, col) in spec.items():
        ax.add_patch(Rectangle((x, y), w, h, fc=col, ec="#2b3439", lw=0.9))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.2)
        pos[key] = (x, y, w, h)
    for a, b, t, style in arrows:
        xa, ya, wa, ha = pos[a]
        xb, yb, wb, hb = pos[b]
        if abs((ya + ha / 2) - (yb + hb / 2)) < 1e-6 or xb >= xa + wa:
            s, e = (xa + wa, ya + ha / 2), (xb, yb + hb / 2)
        elif yb > ya:   # target above source
            s, e = (xa + wa / 2, ya + ha), (xb + wb / 2, yb)
        else:
            s, e = (xa + wa / 2, ya), (xb + wb / 2, yb + hb)
        ax.add_patch(FancyArrowPatch(s, e, arrowstyle="-|>", mutation_scale=11, lw=1.1,
                                     color="#2b3439", ls=style, shrinkA=2, shrinkB=2))
        if t:
            ax.text((s[0] + e[0]) / 2, (s[1] + e[1]) / 2 + 1.6, t, ha="center", fontsize=7, color="#3a4650")


def functional_diagram():
    fig, ax = plt.subplots(figsize=(13, 6.2))
    F, M, C, S = "#fff3c4", "#d8efe4", "#dfe8f5", "#eceff0"
    spec = {
        "pump": (2, 40, 17, 11, "Existing Harvard / Tecan\nsyringe pump\n(withdraw + infuse)\nFIXED, off-frame", F),
        "tube": (25, 40, 17, 11, "Liquid-filled tubing\nPTFE/FEP 1/16\" OD\nfixed clamp -> loops\n-> Z-carriage clamp", F),
        "hold": (48, 40, 15, 11, "Capillary holder\ncollet + depth stop\non break-away mount", M),
        "cap": (69, 40, 14, 11, "Glass capillary\nOD 1.0 / ID 0.6\nL 40, 8° lean", M),
        "obj": (88, 40, 11, 11, "Target object\nin 96-well\n(U-bottom)", S),
        "pc": (2, 12, 17, 11, "PC\n(later: vision +\nsequencing)", C),
        "ctl": (25, 12, 17, 11, "Motion controller\nG-code / serial\nTMC5160-class drivers", C),
        "xyz": (48, 12, 15, 11, "Y -> X -> Z stages\n(ball screw,\nhome switches)", C),
        "ix": (88, 12, 11, 11, "IX73 + camera\n(fixed, observes\nfrom below)", S),
    }
    arrows = [("pump", "tube", "volume", "-"), ("tube", "hold", "", "-"), ("hold", "cap", "", "-"), ("cap", "obj", "aspirate / expel", "-"),
              ("pc", "ctl", "USB", "-"), ("ctl", "xyz", "step/dir or SPI", "-"), ("xyz", "hold", "positions", "-"),
              ("ix", "obj", "", "--")]
    boxes(ax, spec, arrows)
    ax.add_patch(FancyArrowPatch((20.5, 23), (20.5, 40), arrowstyle="-|>", mutation_scale=10, lw=1, ls="--", color="#777"))
    ax.text(21.3, 31, "pump serial\n(later)", fontsize=7, color="#555")
    ax.text(50, 58, "Fluid path (yellow) and motion path (blue) are mechanically separate; only the holder joins them.",
            ha="center", fontsize=9)
    ax.set_xlim(0, 101); ax.set_ylim(8, 62); ax.axis("off")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "functional_diagram.png"), dpi=150)
    fig.savefig(os.path.join(IMG, "functional_diagram.svg")); plt.close(fig)


def electrical_diagram():
    fig, ax = plt.subplots(figsize=(13, 7.2))
    P, C, D, I, S = "#fde2cf", "#dfe8f5", "#d8efe4", "#eceff0", "#f6d0cc"
    spec = {
        "mains": (1, 44, 12, 9, "Mains\n100 V AC", I),
        "psu": (17, 44, 14, 9, "24 V DC PSU\n~150 W, fused", P),
        "estop": (35, 44, 15, 9, "E-stop (NC) +\nsafety relay / contactor\ncuts MOTOR power", S),
        "logic": (17, 12, 14, 9, "5 V / 3.3 V logic\n(DC-DC from 24 V)", P),
        "ctl": (35, 26, 15, 13, "Motion controller\n(e.g. 32-bit board,\nG-code over USB)", C),
        "pc": (1, 28, 12, 9, "PC\nUSB", I),
        "dx": (56, 48, 13, 7, "X driver\nTMC5160", D), "dy": (56, 38, 13, 7, "Y driver\nTMC5160", D),
        "dz": (56, 28, 13, 7, "Z driver\nTMC5160", D),
        "mx": (74, 48, 13, 7, "X NEMA17", D), "my": (74, 38, 13, 7, "Y NEMA17", D), "mz": (74, 28, 13, 7, "Z NEMA17\n(+ brake opt.)", D),
        "sw": (35, 8, 15, 11, "Inputs\nX/Y/Z home (NC)\nopt. far limits (NC)\nE-stop status", I),
        "il": (56, 8, 13, 11, "Optional\ninterlock\n(e.g. lid/door)", I),
    }
    arrows = [("mains", "psu", "", "-"), ("psu", "estop", "24 V", "-"), ("psu", "logic", "", "-"), ("logic", "ctl", "logic", "-"), ("estop", "dx", "", "-"), ("estop", "dy", "", "-"),
              ("estop", "dz", "", "-"), ("pc", "ctl", "", "-"), ("ctl", "dx", "", "-"), ("ctl", "dy", "", "-"), ("ctl", "dz", "SPI/step", "-"),
              ("dx", "mx", "", "-"), ("dy", "my", "", "-"), ("dz", "mz", "", "-"), ("sw", "ctl", "", "-"), ("il", "ctl", "", "--")]
    boxes(ax, spec, arrows)
    ax.text(50, 62, "Preliminary electrical block diagram (stage 1, not frozen). Motor power is cut by the E-stop; "
            "logic stays up so the controller reports the stop.\nZ must not fall when motor power is removed "
            "(1 mm lead + detent torque; add a brake if Z carries >0.5 kg).", ha="center", fontsize=8.5)
    ax.set_xlim(0, 90); ax.set_ylim(5, 66); ax.axis("off")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "electrical_block_diagram.png"), dpi=150)
    fig.savefig(os.path.join(IMG, "electrical_block_diagram.svg")); plt.close(fig)


def d1_compare():
    """Top-view comparison of the two workflows against 'observe while picking'."""
    fig, axs = plt.subplots(1, 2, figsize=(15, 7.4))
    wells = [(well_xy(r, c), r, c) for r in range(8) for c in range(12)]
    L, W = p.PLATE_L.v, p.PLATE_W.v
    fov = p.FOV_4X.v / 2
    # --- W-A
    ax = axs[0]
    LA = p.layout("WA")
    ax.add_patch(Rectangle((-L / 2, -W / 2), L, W, fc="#eef3f5", ec="#222"))
    for (x, y), r, c in wells:
        seen = math.hypot(x, y) <= fov
        ax.add_patch(Circle((x, y), p.WELL_D_TOP.v / 2, fc="#6cc39f" if seen else "#d7dcde", ec="#666", lw=0.4))
    ax.add_patch(Rectangle((LA["x_min"], LA["y_min"]), LA["travel_x"], LA["travel_y"], fc="none", ec="#3a64b0",
                           lw=1.6, ls="--"))
    ax.add_patch(Circle((0, 0), fov, fc="none", ec="#c0392f", lw=1.4))
    ax.set_title(f"W-A  stage fixed, picker travel {LA['travel_x']:.0f} x {LA['travel_y']:.0f}\n"
                 "picker reaches 96/96, but only the well on the optical axis is SEEN (red circle = 4x FOV)",
                 fontsize=9.5)
    ax.text(0, -W / 2 - 22, "grey = reachable but not observed (blind); a centred plate puts NO well on the axis",
            ha="center", fontsize=8)
    # --- W-B
    ax = axs[1]
    LB = p.layout("WB")
    need = (99.0, 63.0)
    cols = {"IX3-SVR (manual)": "#2f7d4f", "IX3-SSU (ultrasonic, motorised)": "#c0392f",
            "Maerzhaeuser SCAN IM for IX73": "#3a64b0"}
    for sname, st in p.STAGES.items():
        tx, ty = st["travel"]
        ax.add_patch(Rectangle((-tx / 2, -ty / 2), tx, ty, fc="none", ec=cols[sname], lw=1.4,
                               label=f"{sname}: {tx:.0f} x {ty:.0f}"))
    ax.add_patch(Rectangle((-need[0] / 2, -need[1] / 2), need[0], need[1], fc="#6cc39f", alpha=0.25, ec="#2b3439",
                           ls=":", label="required: well span 99 x 63"))
    for (x, y), r, c in wells:
        ax.plot(-x, -y, ".", color="#2b3439", ms=3)
    ax.add_patch(Rectangle((LB["x_min"], LB["y_min"]), LB["travel_x"], LB["travel_y"], fc="none", ec="#3a64b0",
                           lw=1.6, ls="--"))
    ax.text(LB["x_max"] + 2, LB["y_max"] + 2, f"picker tip travel {LB['travel_x']:.0f} x {LB['travel_y']:.0f}\n"
            "(-15..+85: +X = park outside keep-out)", fontsize=7.5, color=SC["DES"])
    ax.add_patch(Circle((0, 0), fov, fc="none", ec="#c0392f", lw=1.4))
    ax.legend(loc="lower left", fontsize=7.5)
    ax.set_title("W-B  stage moves each source/destination well to the axis\n"
                 "dots = required stage offsets (one per well); every pick and dispense is SEEN", fontsize=9.5)
    for a in axs:
        a.set_xlim(-95, 120); a.set_ylim(-75, 75); a.set_aspect("equal"); a.grid(alpha=0.25)
        a.set_xlabel("X (mm, optical axis at 0)"); a.set_ylabel("Y (mm)")
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "d1_workflows.png"), dpi=150)
    fig.savefig(os.path.join(IMG, "d1_workflows.svg")); plt.close(fig)


def formats_angles():
    """Recommended angle block and exposed length per plate format: well section, capillary, holder, condenser."""
    from analysis import format_angle_matrix
    _, rec = format_angle_matrix()
    fmts = list(p.PLATE_FORMATS)
    fig, axs = plt.subplots(1, len(fmts), figsize=(3.3 * len(fmts), 5.2), sharey=True)
    wd = p.CONDENSERS["IX-ULWCD"]["WD"].v
    for ax, fmt in zip(axs, fmts):
        f, r = p.PLATE_FORMATS[fmt], rec[fmt]
        rt, rb, dep = f["d_top"] / 2, f["d_bot"] / 2, f["depth"]
        wall = 4.0
        ax.add_patch(Polygon([(-rt - wall, dep), (-rt, dep), (-rb, 0), (rb, 0), (rt, dep), (rt + wall, dep),
                              (rt + wall, -1.2), (-rt - wall, -1.2)], fc="#dfe6e8", ec="#555", lw=0.7))
        ax.plot([-45, 45], [wd, wd], color="#7d6aa8", lw=1.2)
        ax.text(-44, wd + 1.5, "IX-ULWCD front", color="#7d6aa8", fontsize=7)
        ax.axhline(dep + 5, color="#3a64b0", lw=0.8, ls=":")
        ax.text(-44, dep + 6, "safe-Z (rim + 5)", color="#3a64b0", fontsize=7)
        if r:
            t = math.radians(r["theta"]); L = r["exposed"]
            tip = (0.0, p.TIP_CLEAR_BOTTOM.v)
            nose = (L * math.sin(t), tip[1] + L * math.cos(t))
            top = ((L + p.HOLDER_L.v) * math.sin(t), tip[1] + (L + p.HOLDER_L.v) * math.cos(t))
            ax.plot([tip[0], nose[0]], [tip[1], nose[1]], color="#1596a8", lw=2)
            ax.plot([nose[0], top[0]], [nose[1], top[1]], color=FILL["holder"], lw=9, solid_capstyle="butt")
            ax.plot([top[0] - 4, top[0] + 30], [top[1], top[1]], color=FILL["moving"], lw=5)
            ax.set_title(f"{fmt.split(' (')[0]}\nblock {r['theta']:.0f}°, exposed {L:.0f} mm", fontsize=9.5)
            ax.text(0, -11, f"rim {r['rim']:.1f} · cond {r['cond']:.1f} mm\nlight blocked {r['block']:.0%}",
                    ha="center", fontsize=8)
        ax.set_xlim(-46, 46); ax.set_ylim(-18, 82); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    axs[0].set_ylabel("mm above well bottom")
    fig.suptitle("Angle block and exposed length per plate format (tip at well-bottom centre; condenser geometry PH)",
                 fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(IMG, "formats_angle_blocks.png"), dpi=150); plt.close(fig)


if __name__ == "__main__":
    formats_angles()
    d1_compare()
    top_view(); front_view(); side_view(); angle_detail(); functional_diagram(); electrical_diagram()
    print("views written to", os.path.abspath(IMG))
