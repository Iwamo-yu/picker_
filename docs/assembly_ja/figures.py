"""組立手順書用の図: 実測箇所図 (正面・側面)。python docs/assembly_ja/figures.py"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "cad"))
import params as p  # noqa: E402
from model import build, posed  # noqa: E402

# Japanese font: IPAexGothic (IPA Font License). Set JP_FONT or place ipaexg.ttf next to this file.
for cand in (os.environ.get("JP_FONT", ""), os.path.join(HERE, "ipaexg.ttf"),
             "/tmp/claude-0/jf/japanize-matplotlib-1.1.3/japanize_matplotlib/fonts/ipaexg.ttf"):
    if cand and os.path.exists(cand):
        font_manager.fontManager.addfont(cand)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=cand).get_name()
        break

IMG = os.path.join(HERE, "img")
RED = "#c0392f"
FILL = {"ix73": "#d9dee0", "condenser": "#c4b9e6", "plate": "#f4f7f8", "frame": "#9fb3c1", "actuator": "#8fb7c8",
        "motor": "#7d878c", "moving": "#9ed6bd", "holder": "#6cc39f", "pump": "#c9cccd", "electronics": "#c9cccd",
        "table": "#eceeef", "switch": "#e0a84a", "cable": "#c0c6c9"}


def draw(ax, m, proj, only=None):
    items = []
    for q, s in posed(m):
        if q.category in ("tubing", "capillary", "zone"):
            continue
        if only and q.category not in only:
            continue
        b = s.bounding_box()
        if proj == "xz":
            r, d = (b.min.X, b.min.Z, b.max.X - b.min.X, b.max.Z - b.min.Z), -b.min.Y
        else:
            r, d = (b.min.Y, b.min.Z, b.max.Y - b.min.Y, b.max.Z - b.min.Z), b.max.X
        items.append((d, q, r))
    for _, q, r in sorted(items, key=lambda t: t[0]):
        if proj == "xz" and q.name == "ix73_obs_tube_eyepieces":
            ax.add_patch(Rectangle(r[:2], r[2], r[3], fc="none", ec="#888", ls="--", lw=0.8))
            continue
        if proj == "yz" and q.group != "fixed" and q.group != "S" and q.category not in ("ix73", "condenser"):
            a = 0.35
        else:
            a = 0.95
        ax.add_patch(Rectangle(r[:2], r[2], r[3], fc=FILL.get(q.category, "#ddd"), ec="#555", lw=0.5, alpha=a))


def arrow(ax, a, b, text, off=(0, 0), ha="center", rot=0):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="<->", color=RED, lw=1.4))
    ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], text, color=RED, fontsize=9, ha=ha,
            va="center", rotation=rot, bbox=dict(fc="white", ec=RED, lw=0.6, pad=2))


def tag(ax, x, y, text, ha="left"):
    ax.text(x, y, text, color=RED, fontsize=9, ha=ha, va="center", bbox=dict(fc="white", ec=RED, lw=0.6, pad=2))


def measure_points():
    m = build("R08", "IX-ULWCD", "WB")
    T = -p.STAGE_TOP_ABOVE_TABLE.v
    wd = p.CONDENSERS["IX-ULWCD"]["WD"].v
    zc = p.WELL_BOTTOM_Z.v + wd
    rc = p.COND_D.v / 2
    L = p.layout("WB")
    fig, axs = plt.subplots(1, 2, figsize=(16, 8.2))
    # ---------------- 正面 (オペレータ側から)
    ax = axs[0]
    draw(ax, m, "xz")
    arrow(ax, (-215, T), (-215, 0), "M1 定盤 → ステージ上面\n(現在 仮 200 mm)", off=(-8, 0), rot=90)
    arrow(ax, (-rc, zc + 85), (rc, zc + 85), "M6 コンデンサ外径\n(仮 Ø80)", off=(0, 18))
    arrow(ax, (75, p.PLATE_H.v), (75, zc), "M8 プレート上面 → コンデンサ下端\n(ピント合わせ状態で)", off=(95, 0), ha="center")
    arrow(ax, (-p.STAGE_X.v / 2, -40), (p.STAGE_X.v / 2, -40), "M3 ステージ外形・クリップ", off=(0, -14))
    arrow(ax, (p.IX73_W.v / 2, T + 60), (L["tower_x"] + 120, T + 60), "M15 本体右側面 → 定盤端 の空き", off=(0, 16))
    tag(ax, -15, 38, "M4 ステージ中心 ↔ 光軸", ha="right")
    ax.plot([0, 0], [-30, 70], color=RED, ls=":", lw=1)
    tag(ax, L["tower_x"] - 40, T + 22, "M16 定盤の穴ピッチ (M6/25 mm か ¼-20/1\")")
    ax.set_xlim(-300, 620); ax.set_ylim(T - 30, 480); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_title("正面図(オペレータ側から見る)", fontsize=12)
    ax.set_xlabel("X [mm](光軸 = 0)"); ax.set_ylabel("Z [mm](ステージ上面 = 0)")
    # ---------------- 側面 (右から)
    ax = axs[1]
    draw(ax, m, "yz", only=("ix73", "condenser", "plate", "table"))
    arrow(ax, (-p.COND_ARM_W.v / 2 - 10, zc + p.COND_BODY_H.v), (-p.COND_ARM_W.v / 2 - 10, zc + p.COND_BODY_H.v + 60),
          "M7 コンデンサ保持アーム\n(幅・最下点)", off=(-70, 0))
    tag(ax, 120, 420, "M9 照明支柱の位置・断面")
    tag(ax, 150, 500, "M10 照明支柱を後ろへ倒した時の外形", ha="left")
    tag(ax, -370, 230, "M12 観察鏡筒・接眼部の外形\n(前側。ここに架台を置かない)", ha="left")
    tag(ax, -120, -150, "M13 ステージハンドル・焦点ノブ位置", ha="left")
    tag(ax, -120, 60, "M11 コンデンサ最上位置での空き高さ", ha="left")
    ax.set_xlim(-400, 480); ax.set_ylim(T - 30, 540); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_title("側面図(右側から見る。顕微鏡側のみ)", fontsize=12)
    ax.set_xlabel("Y [mm](オペレータから遠ざかる向きが +)"); ax.set_ylabel("Z [mm]")
    fig.suptitle("実測が必要な箇所(赤)。灰色の IX73 形状は仮の外形で、実寸ではありません", fontsize=13)
    fig.tight_layout()
    os.makedirs(IMG, exist_ok=True)
    fig.savefig(os.path.join(IMG, "measure_points.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    measure_points()
    print("ok")
