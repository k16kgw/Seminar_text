# 概念図の編集用データ

このディレクトリのSVGは，MyST本文で表示する図である．SVG自体もInkscapeなどで編集できる．PowerPointで編集する場合は，次のファイルを使用する．

- `concept_diagrams_editable.pptx`：文字，箱，矢印，格子点などをPowerPoint図形として個別編集できる元データ

PowerPointを再生成する場合は，プロジェクトの仮想環境で次を実行する．

```bash
python scripts/build_concept_diagrams_pptx.py
```

SVGを変更した場合は，対応するPowerPointスライドも変更し，両者の説明内容を一致させる．
