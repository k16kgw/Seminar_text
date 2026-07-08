# プロジェクト精査：修正候補リスト

生成日: 2026-07-08
対象: `Seminar_text`（MyST 教材＋Notebook＋スクリプト）全体

## 使い方

- 各項目の `判定:` 欄に **修正する / 削除（対応しない）** のどちらかを記入してください（初期値は空欄）。
- 「削除」と書いた項目は対応しません。「修正する」と書いた項目だけ、次のステップで私がこのファイルを見ながら一括修正します。
- 重要度の目安: **[高]** 内容・整合性に影響 / **[中]** 一貫性・保守性 / **[低]** 気になれば程度・情報共有。

---

## 全体所見（先に結論）

大きな内容上の誤り（数式・図の対応・リンク切れ・cite キー不整合）は**見つかりませんでした**。
- 章 16 本の相互リンク・図参照はすべて実在ファイルに解決。
- `{cite}` で使われている 7 キーはすべて `references.bib` に定義済み（過不足なし）。
- 章から参照される Notebook 図 24 枚はすべて存在。
- `pytest` は 96 passed / 7 skipped で緑。
- `export_notebook_figures.py` が参照する図出力セル ID もすべて実在。
- 数値の抜き取り確認（NB21 `Du,Dv=0.16,0.08` / NB31 `MAX_STEPS=600` / NB32 `n_repeats=200`）は本文記述と一致。

以下は主に**一貫性・保守性・細部**の指摘です。

---

## A. 参考文献の書式・欠落 [中]

`参考文献・キーワード` の書き方が章によって `{cite}` とプレーンテキストで混在しています。
一部はプレーンテキストで挙げた文献が `references.bib` に**存在しない**（＝相互参照できない）状態です。

### A-1. [中] bib に定義済みなのにプレーンテキスト表記（`{cite}` へ統一すべき）
- `chapters/20_pattern_foundations.md:191-192`
  - `- Turing, The Chemical Basis of Morphogenesis, 1952.` → `{cite}`turing1952chemical``
  - `- Strogatz, Nonlinear Dynamics and Chaos.` → `{cite}`strogatz2015nonlinear``
- `chapters/40_network_foundations.md:210`
  - `- Strogatz, Nonlinear Dynamics and Chaos.` → `{cite}`strogatz2015nonlinear``

判定:修正する

### A-2. [中] bib に未登録の文献（ダングリング参照）
- `chapters/30_agent_foundations.md:190`
  - `- Helbing and Molnár, Social force model for pedestrian dynamics, 1995.`
  - 同章の本文は既存キー `helbing2010pedestrian` を使用。対応案: (a) `helbing1995social` を `references.bib` に追加して `{cite}` 化、または (b) 既存キーに置換、または (c) 行削除。
- `chapters/40_network_foundations.md:211`
  - `- Newman, Networks: An Introduction.`
  - `references.bib` に未登録。対応案: (a) `newman2018networks` を追加、または (b) 行削除。

判定:修正する

---

## B. スクリプトと実アセットの不一致 [中]

- `scripts/make_placeholder_assets.py`
  - docstring（13行目）と出力（50行目）は `sample_snake_pattern.png` を生成する記述。
  - 一方リポジトリに実在するデータ資産は `assets/data/sample_snake_pattern.jpeg`（拡張子・形式が異なる）。
  - さらにこの `.jpeg` は、どの Notebook・章からも参照されていない**未使用ファイル**（`grep` 済み。参照はスクリプトの `.png` 出力のみ）。
  - 対応案: ①スクリプトを `.jpeg` 出力に合わせる、②未使用の `.jpeg` を削除、③どちらかに名前を統一。教材本体の動作には必須でないスクリプトなので、方針だけ決めれば十分。

判定:修正する

---

## C. ドキュメント文字列のハードコード [低]

- `scripts/check_notebooks.py:4`
  - docstring に `12 個の notebook` と数値が直書き。現状 `NOTEBOOKS` は 12 本で一致するが、Notebook を増減すると docstring だけ古くなる。
  - 対応案: 「12 個の」→「全ての」等、数値に依存しない表現へ（実行時出力は `len(NOTEBOOKS)` を使っており問題なし）。

判定:修正する

---

## D. 保守性：図出力セル ID の結合が脆い [低・情報共有]

- `scripts/export_notebook_figures.py` は章掲載図を Notebook の**セル ID**で固定しています。
  - 一部は意味のある ID（`stable-code`, `comparison`, `visualization` 等）ですが、
  - 一部は位置由来に見える ID（`cell-0008`, `cell-0010`, `cell-0039`, `cell-0041`, `cell-0067`, `cell-0069`）です。
- 現状はすべて解決しますが、対象より上のセルを挿入・削除すると、**エラーにならないまま別セルの図を書き出す**リスクがあります（ID がたまたま残ると誤図、消えると `KeyError`）。
- 対応案: すべて意味のある固定 ID（セルタグ）へ寄せると、章とのひも付けが壊れにくくなります。急ぎではありません。

判定:修正する

---

## E. 実行依存の数値記述（要注意点の共有）[低・情報共有]

- 本文には Notebook 出力に由来する具体数値・図タイトルが埋め込まれています（例: `chapters/32_agent_boarding_behavior.md` の「約61.5付近」、図タイトルの `T=600` 等）。
- 入力側パラメータ（`MAX_STEPS=600`, `Du/Dv`, `n_repeats=200` 等）は本文と一致することを確認済みですが、これらの**派生数値は Notebook を再実行しない限り最終確認できません**。
- 対応は不要です。ただし今後 Notebook のコードを変更した場合は、`export_notebook_figures.py` で図を再生成し、本文中の数値・図タイトルを再確認してください（README の運用どおり）。

判定:修正する

---

## 参考：問題なしを確認済みの項目（対応不要）

- 章間リンク・画像パス: 全解決（欠落 0）。
- `{cite}` キー ⇔ `references.bib`: 完全一致（7/7）。
- Notebook 図ファイル 24 枚: 全存在、`test_exported_notebook_figure_exists` 緑。
- `.gitignore`: `.venv/`・`.DS_Store`・`_build/` は追跡されていない（`git ls-files` で確認、混入 0）。
- CI（`.github/workflows/pages.yml`）: `BASE_URL` 設定・notebook チェック・HTML ビルド検証あり、構成上の問題なし。
- 依存関係: `pyproject.toml` / `requirements.txt` / `environment.yml` の 3 者は整合（`environment.yml` のみ追加で `mystmd` を pip 導入、これは意図的）。
