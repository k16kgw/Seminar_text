# 図版の編集元

図版は種類に応じて，次の編集元から再生成する．

| 図版 | 編集元 |
| --- | --- |
| `concepts/*.png` | `concepts/concept_diagrams_editable.pptx`．各要素をPowerPoint図形として編集できる |
| `notebook/*.png` | 対応する `notebooks/*.ipynb`．グラフの計算条件，軸，配色をNotebook上で変更する |
| `12_single_plate_temperature.png` | `notebooks/12_stegosaurus_single_plate_2d.ipynb` の保存セル |

Notebook図を更新した後は，次を実行して章掲載用画像を書き出す．

```bash
python scripts/export_notebook_figures.py
```

概念図のPowerPointを再生成する方法は，[concepts/README.md](concepts/README.md)を参照する．
