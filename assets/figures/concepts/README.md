# 概念図の編集用データ

MyST本文では，このディレクトリのPNGを表示する．PNGは編集用PowerPointを高解像度で書き出したものである．図を変更する場合は，次のファイルを使用する．

- `concept_diagrams_editable.pptx`：文字，箱，矢印，格子点などをPowerPoint図形として個別編集できる元データ．数式はOffice Math数式，行列はOffice Mathの行列要素として収録している

PowerPointだけを再生成する場合は，`python-pptx` とPandocを利用できる環境で次を実行する．

```bash
python scripts/build_concept_diagrams_pptx.py
```

PowerPointから本文用PNGまで再生成する場合は，macOSのKeynoteと`pdftoppm`を利用できる環境で次を実行する．

```bash
python scripts/export_concept_diagrams.py
```

SVGは旧版との比較や補助的なベクターデータとして残している．本文用PNGと内容が異なる場合は，PowerPointを正とする．
