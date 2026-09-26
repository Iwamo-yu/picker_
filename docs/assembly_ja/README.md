# 組立手順書(日本語)

- `assembly_guide_ja.html` … 生成物(直接編集しない)
- `guide.src.html` … 本文テンプレート。`{{KEY}}` は `cad/keynums.py` の数値、`{{IMG:x.png}}` は画像。
- `build_guide.py` … テンプレート → HTML(画像を埋め込み、未実測の仮値一覧と変更履歴を自動挿入)
- `figures.py` … 実測箇所図(日本語フォント IPAex ゴシックが必要: `JP_FONT` か同じフォルダの `ipaexg.ttf`)
- `render_steps.js` … 3D ビューアから工程図を撮影

一括更新: `python tools/build_all.py`(3D 工程図も撮り直すなら `RENDER_JS=docs/assembly_ja/render_steps.js` と `CHROME`、`THREE_DIR` を設定)。
