"""Part map: which physical part is which CAD solid, which parts-list line (P01-P42), which assembly
step, and which measurements/parameters it depends on.  Single source for docs/13_part_map_ja.md,
docs/assembly_ja/part_map_ja.html, the numbered call-out renders and the viewer's assembly steps.

CAD names are matched after stripping the workflow prefix ("WB__") and the head prefix ("R08__",
"V20__", ...).  check() fails if a W-B CAD part or a parts-list ID is not mapped exactly once."""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# assembly steps of the Japanese guide (moved here from viewer/build_viewer.py)
STEPS = [
    dict(n=1, parts=[r"^base_plate$"]),
    dict(n=2, parts=[r"^post_\d$", r"^post_brace_\d$"]),
    dict(n=3, parts=[r"^y_beam$"]),
    dict(n=4, parts=[r"^Y_actuator_body$", r"^Y_motor$", r"^Y_home_switch$"]),
    dict(n=5, parts=[r"^Y_carriage$", r"^X_support_beam$", r"^X_actuator_body$", r"^X_motor$", r"^X_home_switch$"]),
    dict(n=6, parts=[r"^X_carriage_bracket$", r"^Z_actuator_body$", r"^Z_motor$", r"^Z_home_switch_top$",
                     r"^Z_reference_switch$", r"^R08__Z_carriage$"]),
    dict(n=7, parts=[r"^R08__breakaway_kinematic_mount$", r"^R08__arm_thin$", r"^R08__arm_deep$", r"^R08__capillary_holder_collet$"]),
    dict(n=8, parts=[r"^Y_cable_chain$", r"^X_cable_chain$", r"^motion_controller_24V$"]),
    dict(n=9, parts=[r"tubing", r"^syringe_pump_existing$"]),
    dict(n=10, parts=[r"^R08__glass_capillary"]),
]

# kind: 購入 = buy, 製作 = make, 既存 = already in the lab, 顕微鏡 = microscope side (not built)
# side: picker | microscope | reference (envelope only, shown for orientation)
GROUPS = [
    dict(n=1, name="ベース板", role="架台全体を定盤に固定する土台。長穴で位置と向きを調整する",
         cad=[r"^base_plate$"], pids=["P16", "P37"], kind="製作", side="picker", meas="M15, M16"),
    dict(n=2, name="支柱と筋交い", role="Y 梁を必要な高さに支える 2 本の柱",
         cad=[r"^post_\d$", r"^post_brace_\d$"], pids=["P17", "P20"], kind="購入", side="picker", meas="M1"),
    dict(n=3, name="Y 梁", role="両端で支えた固定梁。Y ステージを載せる",
         cad=[r"^y_beam$"], pids=["P18"], kind="購入", side="picker", meas="M1"),
    dict(n=4, name="Y ステージ", role="先端を Y(奥行き)方向に動かす軸",
         cad=[r"^Y_actuator_body$", r"^Y_motor$"], pids=["P03", "P04", "P06"], kind="購入", side="picker",
         meas="モーメント(03 §5b)"),
    dict(n=5, name="Y 原点スイッチ", role="Y の原点(手前側端)",
         cad=[r"^Y_home_switch$"], pids=["P30"], kind="購入", side="picker", meas=""),
    dict(n=6, name="Y キャリッジ", role="Y ステージの可動台。X 支持梁を載せる",
         cad=[r"^Y_carriage$"], pids=["P15"], kind="製作", side="picker", meas=""),
    dict(n=7, name="X 支持梁", role="Y キャリッジから光軸側へ張り出す片持ち梁",
         cad=[r"^X_support_beam$"], pids=["P19"], kind="購入", side="picker", meas="M7"),
    dict(n=8, name="X ステージ", role="先端を X(左右)方向に動かす軸。待避位置もこの軸",
         cad=[r"^X_actuator_body$", r"^X_motor$"], pids=["P02", "P04", "P06"], kind="購入", side="picker", meas=""),
    dict(n=9, name="X 原点スイッチ", role="X の原点(外側端)",
         cad=[r"^X_home_switch$"], pids=["P30"], kind="購入", side="picker", meas=""),
    dict(n=10, name="X キャリッジブラケット", role="X の可動台に Z ステージを鉛直に固定する",
         cad=[r"^X_carriage_bracket$"], pids=["P15"], kind="製作", side="picker", meas=""),
    dict(n=11, name="Z ステージ", role="先端を上下させる軸。着地精度と停電時に落ちないことが要",
         cad=[r"^Z_actuator_body$", r"^Z_motor$"], pids=["P01", "P05", "P06"], kind="購入", side="picker", meas=""),
    dict(n=12, name="Z 上端リミットスイッチ", role="行き過ぎ防止のみ。安全な位置ではない",
         cad=[r"^Z_home_switch_top$"], pids=["P30"], kind="購入", side="picker", meas=""),
    dict(n=13, name="Z 基準スイッチ", role="Z の原点。ヘッド最上部がコンデンサ下端より余裕を残す高さ(1 個だけ)",
         cad=[r"^Z_reference_switch$"], pids=["P42"], kind="購入", side="picker", meas="M8, M23"),
    dict(n=14, name="Z キャリッジ", role="Z ステージの可動台。マウントとアームを付ける",
         cad=[r"^Z_carriage$"], pids=["P15"], kind="製作", side="picker", meas=""),
    dict(n=15, name="キネマティックマウント", role="衝突で外れ、同じ位置に戻る(力の制限ではない)",
         cad=[r"^breakaway_kinematic_mount$"], pids=["P12"], kind="購入", side="picker", meas=""),
    dict(n=16, name="ドッグレッグアーム", role="コンデンサの下へ差し込む薄い腕。Z 本体を光軸の外に置く",
         cad=[r"^arm_thin$", r"^arm_deep$"], pids=["P14"], kind="製作", side="picker", meas="M6, M7, M8"),
    dict(n=17, name="キャピラリホルダーと角度ブロック", role="コレットでキャピラリをつかみ、ブロックで傾き(8°/20°/30°)を決める",
         cad=[r"^capillary_holder_collet$"], pids=["P10", "P11", "P13"], kind="製作", side="picker", meas="M23"),
    dict(n=18, name="ガラスキャピラリ", role="対象物を吸う先端。対象の大きさで太さを選ぶ(消耗品)",
         cad=[r"^glass_capillary"], pids=["P21", "P22", "P23", "P24"], kind="購入", side="picker", meas=""),
    dict(n=19, name="チューブとクランプ", role="ポンプからキャピラリまでの液の経路。サービスループで動きを逃がす",
         cad=[r"^tubing_", r"^tubing_clamp_Zbody$", r"^tubing_fixed_clamp$"], pids=["P25", "P26"], kind="購入",
         side="picker", meas=""),
    dict(n=20, name="シリンジポンプ", role="吸引と吐出。架台には載せない",
         cad=[r"^syringe_pump_existing$"], pids=["P38", "P40", "P27", "P41"], kind="既存", side="picker", meas="M17"),
    dict(n=21, name="ケーブルチェーン", role="モーターとスイッチの配線を可動部の奥側で逃がす",
         cad=[r"^X_cable_chain$", r"^Y_cable_chain$"], pids=["P34", "P35"], kind="購入", side="picker", meas=""),
    dict(n=22, name="制御箱", role="コントローラ、ドライバ、24 V 電源、非常停止回路",
         cad=[r"^motion_controller_24V$"], pids=["P28", "P29", "P31", "P32", "P33", "P36"], kind="購入",
         side="picker", meas=""),
    dict(n=23, name="電動 XY ステージとプレートホルダー", role="W-B でウェルを光軸へ運ぶ(ピッカーは触れない)",
         cad=[r"^ix73_stage$"], pids=["P07", "P08", "P39"], kind="顕微鏡", side="microscope", meas="M3, M4"),
    dict(n=24, name="96 穴プレート(Corning 7007)", role="V1 の対象プレート。蓋は外して使う",
         cad=[r"^plate_96_SLAS$"], pids=[], kind="既存", side="microscope", meas="M19"),
    dict(n=25, name="コンデンサ(IX-ULWCD)と保持アーム", role="透過照明。アームはこの下を通る",
         cad=[r"^condenser_IX-ULWCD", r"^condenser_carrier_arm$", r"^illum_arm_to_pillar$"], pids=["P09"], kind="顕微鏡",
         side="microscope", meas="M6, M7, M8"),
    dict(n=26, name="IX73 本体(外形の目安)", role="位置関係を見るための仮の外形。寸法は実測で置き換える",
         cad=[r"^ix73_(body_lower|stage_support|objective_zone|obs_tube_eyepieces|stage_handle|illum_pillar|lamp_house)$",
              r"^optical_table_patch$"], pids=[], kind="顕微鏡", side="reference", meas="M1, M5, M9, M12–M14"),
    dict(n=27, name="比較用の外形", role="別のコンデンサと、照明支柱を倒した状態。比較のためだけに表示",
         cad=[r"^condenser_IX2-(LWUCD|MLWCD)", r"^illum_arm_tilted_back$"], pids=[], kind="顕微鏡", side="reference",
         meas="M10"),
]
KIND_ORDER = {"製作": 0, "購入": 1, "既存": 2, "顕微鏡": 3}


def strip(key):
    k = key.split("__", 1)[1] if key.startswith(("WB__", "WA__", "COND[")) else key
    k = re.sub(r"^(R08|V00|V20|V30|V45)__", "", k)
    return k


def group_of(key):
    k = strip(key)
    hits = [g["n"] for g in GROUPS if any(re.search(r, k) for r in g["cad"])]
    return hits


def step_of(key):
    k = key.split("__", 1)[1] if key.startswith("WB__") else key
    for st in STEPS:
        if any(re.search(r, k) for r in st["parts"]):
            return st["n"]
    return None


def load_parts():
    meta = json.load(open(os.path.join(ROOT, "cad", "out", "parts.json")))
    return {k: v for k, v in meta["parts"].items()
            if v.get("workflow") in ("WB", "all") and v["category"] != "zone"}


def load_pids():
    with open(os.path.join(HERE, "candidates.csv"), encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def check():
    """Every W-B CAD part maps to exactly one group; every parts-list ID appears in a group."""
    errs = []
    for key in load_parts():
        g = group_of(key)
        if len(g) != 1:
            errs.append(f"CAD part {key}: groups {g}")
    used = {p for g in GROUPS for p in g["pids"]}
    pids = load_pids()
    errs += [f"parts-list {p} not in any group" for p in pids if p not in used]
    errs += [f"group refers to unknown {p}" for p in used if p not in pids]
    return errs


def steps_of_group(g, parts):
    s = sorted({step_of(k) for k in parts if group_of(k) == [g["n"]] and k.startswith("WB__")} - {None})
    return s
