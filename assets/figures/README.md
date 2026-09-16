# 図版の編集元

図版は種類に応じて，次の編集元から再生成する．

| 図版 | 編集元 |
| --- | --- |
| `concepts/*.png` | `concepts/concept_diagrams_editable.pptx`．各要素をPowerPoint図形として編集できる |
| `notebook/*.png` | 対応する `notebooks/*.ipynb`．グラフの計算条件，軸，配色をNotebook上で変更する |
| `12_single_plate_temperature.png` | `notebook/12_single_plate_temperature.png` と同じ図．書き出しスクリプトで同時に更新する |

Notebook図を更新した後は，次を実行して章掲載用画像を書き出す．

```bash
python scripts/export_notebook_figures.py
```

11・12章の図だけを更新する場合は，対象を指定できる．セル中心と境界面の模式図も，12のNotebook内の描画コードを編集して再生成する．

```bash
python scripts/export_notebook_figures.py --notebooks 11_stegosaurus_heat_1d_fin.ipynb 12_stegosaurus_single_plate_2d.ipynb
```

21・22章の成長率，濃度場，連結成分，FFTスペクトルの図も，対応Notebookの計算・描画コードが編集元である．Notebookを実行した後，次で章掲載版を更新する．

```bash
python scripts/export_notebook_figures.py --notebooks 21_reaction_diffusion_gray_scott.ipynb 22_snake_pattern_features.ipynb
```

31・32章の格子・距離場，占有率，反復分布，打切り比較も，対応Notebookを編集・実行してから書き出す．

```bash
python scripts/export_notebook_figures.py --notebooks 31_train_boarding_ca.ipynb 32_stochastic_simulation_repeats.ipynb
```

概念図のPowerPointを再生成する方法は，[concepts/README.md](concepts/README.md)を参照する．
