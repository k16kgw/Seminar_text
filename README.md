# 卒業研究準備セミナー：数理モデリングとシミュレーション

このリポジトリは、大学情報数理学科4年生の卒業研究準備セミナー用教材を作成・公開するためのものです。

学生はすでに Strogatz『Nonlinear Dynamics and Chaos』を輪講し、力学系の基礎を学んでいる。次の2週間では、各学生が自分の卒業研究テーマに接続できる数理モデルと数値シミュレーションを学ぶ。各学生は50分×2回の輪講を担当する。

本教材は、MyST Markdown による book 形式で作成し、GitHub Actions を用いて GitHub Pages に公開する。また、各章に対応する Jupyter Notebook を用意し、学生がコピーして自分の環境で実行できるようにする。

---

## 1. 教材の目的

本教材の目的は、以下の4つである。

1. 力学系の基礎を、具体的な卒業研究テーマに接続する。
2. 現象を状態変数・パラメータ・方程式・アルゴリズムとして表す方法を学ぶ。
3. 最小モデルを作り、数値シミュレーションで可視化する。
4. 卒業研究開始時点で、各学生が「何を比較し、何を図にし、何を検証するか」を説明できるようにする。

---

## 2. 対象読者

対象読者は、情報数理学科4年生である。

前提知識は以下とする。

* 常微分方程式の初歩
* 線形安定性解析の初歩
* 固有値・固有ベクトル
* 相図
* Python の基本文法
* NumPy と matplotlib の初歩
* Strogatz『Nonlinear Dynamics and Chaos』の前半程度

有限要素法、偏微分方程式の厳密解、マルチエージェントシミュレーション、画像解析、ネットワーク科学については、初学者として扱う。

---

## 3. 輪講構成

共通読書資料は全員が読むが、輪講対象にはしない。本文8章を、4人の学生が2章ずつ担当する。

| 区分     | ファイル                                      | 内容                                | 輪講  |
| ------ | ----------------------------------------- | --------------------------------- | --- |
| 共通読書資料 | `chapters/00_research_design.md`          | 研究設計と数理モデリングの作法                   | しない |
| 第1章    | `chapters/01_stegosaurus_heat_basic.md`   | ステゴサウルス背板の放熱 I：熱方程式とフィンモデル        | する  |
| 第2章    | `chapters/02_stegosaurus_heat_shape.md`   | ステゴサウルス背板の放熱 II：トゲ状構造から板状構造への形態比較 | する  |
| 第3章    | `chapters/03_reaction_diffusion_basic.md` | ヘビ模様の反応拡散 I：反応拡散方程式とチューリング型パターン   | する  |
| 第4章    | `chapters/04_reaction_diffusion_snake.md` | ヘビ模様の反応拡散 II：写真画像との比較とパラメータ探索     | する  |
| 第5章    | `chapters/05_agent_boarding_basic.md`     | 電車乗降のマルチエージェント I：最小セルオートマトンモデル    | する  |
| 第6章    | `chapters/06_agent_boarding_behavior.md`  | 電車乗降のマルチエージェント II：ドア付近滞留者の行動ルール   | する  |
| 第7章    | `chapters/07_love_dynamics_basic.md`      | 恋愛モデル I：ストロガッツの2人モデルと外力項          | する  |
| 第8章    | `chapters/08_love_dynamics_network.md`    | 恋愛モデル II：複数人・三角関係・ネットワーク恋愛力学      | する  |

---

## 4. 作成するリポジトリ構成

Claude Code は以下の構成でファイルを作成すること。

```text
.
├── README.md
├── myst.yml
├── requirements.txt
├── environment.yml
├── pyproject.toml
├── .gitignore
├── .github/
│   └── workflows/
│       └── pages.yml
├── chapters/
│   ├── index.md
│   ├── 00_research_design.md
│   ├── 01_stegosaurus_heat_basic.md
│   ├── 02_stegosaurus_heat_shape.md
│   ├── 03_reaction_diffusion_basic.md
│   ├── 04_reaction_diffusion_snake.md
│   ├── 05_agent_boarding_basic.md
│   ├── 06_agent_boarding_behavior.md
│   ├── 07_love_dynamics_basic.md
│   └── 08_love_dynamics_network.md
├── notebooks/
│   ├── 01_stegosaurus_heat_1d_fin.ipynb
│   ├── 02_stegosaurus_shape_comparison.ipynb
│   ├── 03_reaction_diffusion_gray_scott.ipynb
│   ├── 04_snake_pattern_features.ipynb
│   ├── 05_train_boarding_ca.ipynb
│   ├── 06_train_boarding_behavior_rules.ipynb
│   ├── 07_love_dynamics_two_person.ipynb
│   └── 08_love_dynamics_network.ipynb
├── scripts/
│   ├── check_notebooks.py
│   └── make_placeholder_assets.py
├── assets/
│   ├── figures/
│   └── data/
└── tests/
    └── test_notebooks_exist.py
```

---

## 5. MyST book 設定

`myst.yml` を作成し、少なくとも以下を満たすこと。

* 日本語タイトルを設定する。
* `chapters/index.md` をトップページにする。
* 共通読書資料と第1章から第8章を順番に table of contents に入れる。
* 各章のページタイトルが左ナビゲーションに出るようにする。
* notebook へのリンクを各章から張る。
* GitHub repository URL を設定できる形式にしておく。
* HTML build が `_build/html` に出力されることを前提にする。

`myst.yml` の初期案は以下とする。

```yaml
version: 1
project:
  title: 卒業研究準備セミナー：数理モデリングとシミュレーション
  description: 力学系から熱伝導、反応拡散、マルチエージェント、恋愛モデルへ接続する学部4年生向け教材
  keywords:
    - 数理モデル
    - 力学系
    - シミュレーション
    - 反応拡散
    - マルチエージェント
    - 熱伝導
    - ネットワーク
  authors:
    - name: Keiichiro Kagawa
  github: https://github.com/REPLACE_ME/REPLACE_ME
  toc:
    - file: chapters/index.md
    - file: chapters/00_research_design.md
    - title: ステゴサウルス背板の放熱
      children:
        - file: chapters/01_stegosaurus_heat_basic.md
        - file: chapters/02_stegosaurus_heat_shape.md
    - title: ヘビ模様の反応拡散
      children:
        - file: chapters/03_reaction_diffusion_basic.md
        - file: chapters/04_reaction_diffusion_snake.md
    - title: 電車乗降のマルチエージェント
      children:
        - file: chapters/05_agent_boarding_basic.md
        - file: chapters/06_agent_boarding_behavior.md
    - title: 恋愛モデル
      children:
        - file: chapters/07_love_dynamics_basic.md
        - file: chapters/08_love_dynamics_network.md
  settings:
    output_matplotlib_strings: remove
    output_stderr: remove-warn
site:
  template: book-theme
  title: 卒業研究準備セミナー
```

---

## 6. 各 Markdown 章の共通フォーマット

各章は独立して読めるようにする。各章は以下の構造を基本とする。

```markdown
---
title: 章タイトル
---

# 章タイトル

## この章の目的

## 現象の説明

## 最小モデル

## 数式による定式化

## パラメータの意味

## 数値シミュレーション

## Notebook

## 卒業研究への接続

## 演習問題

## 発展課題

## 参考文献・キーワード
```

各章には、対応する notebook へのリンクを必ず含めること。

例：

```markdown
対応 notebook: [01_stegosaurus_heat_1d_fin.ipynb](../notebooks/01_stegosaurus_heat_1d_fin.ipynb)
```

各章の分量は、目安として日本語で 3,000〜6,000字程度とする。ただし、数式・図・表・演習を含めてよい。

---

## 7. 共通読書資料の内容

`chapters/00_research_design.md` は、全員が読む共通資料である。輪講対象にはしない。

含める内容は以下。

### 7.1 現象からモデルへ

* 現象を言葉で説明する。
* 何を知りたいかを問いにする。
* 観測量と状態変数を区別する。
* パラメータを決める。
* 最小モデルから始める。
* 複雑なモデルは後から足す。

### 7.2 研究テーマを数理化する手順

1. 対象現象を決める。
2. 比較したい条件を決める。
3. 状態変数を決める。
4. パラメータを決める。
5. 時間発展または更新規則を決める。
6. 初期条件と境界条件を決める。
7. 評価指標を決める。
8. 図にする。
9. 先行研究との差分を書く。

### 7.3 よい卒研テーマの条件

* 最小モデルが1か月以内に動く。
* 最初の図がすぐに作れる。
* パラメータを変えた比較ができる。
* 先行研究または実データとの比較ができる。
* 結果が予想と違っても卒論になる。

### 7.4 各テーマへの接続

* ステゴサウルス背板：形状差と放熱効率。
* ヘビ模様：反応拡散パターンと実画像の特徴量。
* 電車乗降：ドア付近の行動ルールと停車時間。
* 恋愛モデル：人物関係の時系列とネットワーク力学。

---

## 8. 第1章：ステゴサウルス背板の放熱 I

ファイル名：

```text
chapters/01_stegosaurus_heat_basic.md
notebooks/01_stegosaurus_heat_1d_fin.ipynb
```

### 章の目的

ステゴサウルスの背板を放熱フィンとして単純化し、熱方程式・境界条件・フィン効率を学ぶ。

### 含める内容

* ステゴサウルス背板の放熱仮説。
* 背板を「熱を逃がすフィン」として見る考え方。
* 熱伝導方程式。
* 定常熱伝導。
* 対流境界条件。
* 放射境界条件は発展扱い。
* 1次元フィン方程式。
* フィン効率。
* 表面積だけでなく、内部まで熱が届くかが重要であること。

### 数式

熱方程式：

```math
\rho c \frac{\partial T}{\partial t}
=
\nabla \cdot (k \nabla T) + Q
```

定常熱伝導：

```math
\nabla \cdot (k \nabla T) + Q = 0
```

対流境界条件：

```math
-k \frac{\partial T}{\partial n}
=
h(T - T_{\mathrm{air}})
```

1次元フィン方程式：

```math
\frac{d^2 \theta}{dx^2} - m^2 \theta = 0,
\quad
\theta = T - T_{\mathrm{air}}
```

### notebook 要件

`01_stegosaurus_heat_1d_fin.ipynb` では、1次元フィンの温度分布を計算する。

必須セル：

1. ライブラリ読み込み。
2. パラメータ設定。
3. 解析解または差分法による温度分布。
4. フィン長を変えた比較。
5. 放熱量の近似計算。
6. 図の表示。
7. 学生が変更する課題セル。

---

## 9. 第2章：ステゴサウルス背板の放熱 II

ファイル名：

```text
chapters/02_stegosaurus_heat_shape.md
notebooks/02_stegosaurus_shape_comparison.ipynb
```

### 章の目的

トゲ状構造、偏平なトゲ、板状構造を同条件で比較し、放熱効率の観点から形態差を評価する。

### 注意

「進化前後で必ずトゲから板へ一方向に変化した」と断定しないこと。教材中では、次の表現を用いる。

```text
剣竜類の皮骨構造に見られるトゲ状構造と板状構造を、放熱効率という観点から比較する。
```

または、

```text
トゲ状から板状へ連続的に変形する仮想形態系列を作り、形状変化が放熱性能に与える影響を数値的に調べる。
```

### 含める内容

* 形状比較の考え方。
* 円錐状トゲ、偏平トゲ、三角板、楕円板の比較。
* 同じ体積で比較する場合。
* 同じ高さで比較する場合。
* 同じ投影面積で比較する場合。
* 評価指標の違い。
* 総放熱量、体積あたり放熱量、表面積あたり放熱量。
* 風速・外気温・血流パラメータへの感度分析。

### 数式

総放熱量：

```math
Q_{\mathrm{out}}
=
\int_{\partial \Omega}
h(T - T_{\mathrm{air}})\, dS
```

体積あたり放熱効率：

```math
E_V
=
\frac{Q_{\mathrm{out}}}{V}
```

表面積あたり放熱効率：

```math
E_A
=
\frac{Q_{\mathrm{out}}}{A}
```

血流を含む簡略モデル：

```math
\rho c \frac{\partial T}{\partial t}
=
\nabla \cdot (k \nabla T)
+
\omega_b c_b (T_b - T)
```

### notebook 要件

`02_stegosaurus_shape_comparison.ipynb` では、厳密な3D FEMではなく、教育用の簡略モデルで形状比較を行う。

必須セル：

1. 形状パラメータの定義。
2. トゲ状・偏平トゲ・板状の幾何量の計算。
3. 表面積、体積、代表長さの計算。
4. 簡略化した熱抵抗モデルによる放熱量推定。
5. 体積あたり効率の比較。
6. パラメータスイープ。
7. 図の表示。
8. 卒研でFEMに発展させる場合のメモ。

---

## 10. 第3章：ヘビ模様の反応拡散 I

ファイル名：

```text
chapters/03_reaction_diffusion_basic.md
notebooks/03_reaction_diffusion_gray_scott.ipynb
```

### 章の目的

反応拡散方程式により、空間パターンが自発的に生じる仕組みを学ぶ。

### 含める内容

* 拡散方程式。
* 反応項。
* 反応拡散方程式。
* チューリング型不安定性の直観。
* Gray-Scott モデル。
* 斑点、縞、迷路模様。
* 初期条件と境界条件。
* 差分法による数値計算。
* 数値安定性に関する注意。

### 数式

反応拡散方程式：

```math
\frac{\partial u}{\partial t}
=
D_u \Delta u + f(u,v)
```

```math
\frac{\partial v}{\partial t}
=
D_v \Delta v + g(u,v)
```

Gray-Scott モデル：

```math
\frac{\partial u}{\partial t}
=
D_u \Delta u - uv^2 + F(1-u)
```

```math
\frac{\partial v}{\partial t}
=
D_v \Delta v + uv^2 - (F+k)v
```

### notebook 要件

`03_reaction_diffusion_gray_scott.ipynb` では、Gray-Scott モデルを2次元格子で計算する。

必須セル：

1. ライブラリ読み込み。
2. パラメータ設定。
3. ラプラシアン関数。
4. 初期条件。
5. 時間発展。
6. パターンの可視化。
7. パラメータを変えた比較。
8. 学生がヘビ模様へ接続するための課題。

---

## 11. 第4章：ヘビ模様の反応拡散 II

ファイル名：

```text
chapters/04_reaction_diffusion_snake.md
notebooks/04_snake_pattern_features.ipynb
```

### 章の目的

反応拡散で生成した模様を、実際のヘビ写真と比較するための考え方を学ぶ。

### 含める内容

* 「ヘビっぽい」ではなく、特徴量で比較する。
* 二値化。
* 面積比。
* 斑点数。
* 縞方向。
* 空間自己相関。
* フーリエスペクトル。
* パラメータ探索。
* 実写真を使う場合の注意。
* 個体差、撮影角度、照明、曲面の影響。

### 数式

画素ごとの単純比較：

```math
L(\theta)
=
\| I_{\mathrm{snake}} - I_{\mathrm{sim}}(\theta) \|^2
```

特徴量による比較：

```math
L(\theta)
=
w_1 |r_{\mathrm{area}} - \hat{r}_{\mathrm{area}}|
+
w_2 |\lambda - \hat{\lambda}|
+
w_3 |n_{\mathrm{spot}} - \hat{n}_{\mathrm{spot}}|
```

### notebook 要件

`04_snake_pattern_features.ipynb` では、外部画像なしでも動くように、擬似的な模様画像を生成して特徴量抽出を行う。任意で `assets/data/` に画像を置けば差し替えられる構造にする。

必須セル：

1. 模様画像の生成または読み込み。
2. グレースケール化。
3. 二値化。
4. 面積比の計算。
5. 連結成分数の計算。
6. 2次元FFTによる周波数特徴量。
7. 反応拡散パターンとの比較。
8. 写真を追加する場合のセル。

---

## 12. 第5章：電車乗降のマルチエージェント I

ファイル名：

```text
chapters/05_agent_boarding_basic.md
notebooks/05_train_boarding_ca.ipynb
```

### 章の目的

電車の乗降を、格子上のマルチエージェントモデルとして表現する。

### 含める内容

* エージェントとは何か。
* 連続モデルと離散モデル。
* セルオートマトン。
* 車内、ドア、ホームの空間表現。
* 乗車客、降車客、車内滞留客。
* 出入口付近のボトルネック。
* 更新順序の重要性。
* 停車時間に相当する評価指標。

### 数式・記法

エージェントの位置：

```math
x_i(t)
```

連続時間風の更新：

```math
x_i(t+\Delta t)
=
x_i(t)
+
v_i(t)\Delta t
```

停車時間の簡略指標：

```math
T_{\mathrm{dwell}}
=
T_{\mathrm{alight}} + T_{\mathrm{board}}
```

### notebook 要件

`05_train_boarding_ca.ipynb` では、2次元格子の簡単な乗降シミュレーションを実装する。

必須セル：

1. 空間グリッドの定義。
2. エージェントの初期配置。
3. 降車客の移動ルール。
4. 乗車客の移動ルール。
5. 衝突回避。
6. ドア付近に固定障害物を置く条件。
7. シミュレーション実行。
8. 完了時間と密度分布の可視化。

---

## 13. 第6章：電車乗降のマルチエージェント II

ファイル名：

```text
chapters/06_agent_boarding_behavior.md
notebooks/06_train_boarding_behavior_rules.ipynb
```

### 章の目的

ドア付近に立つ人を単なる障害物ではなく、行動ルールを持つエージェントとして扱う。

### 含める内容

* 固定型。
* 横移動型。
* 一時降車型。
* 協調型。
* 非協調型。
* 周囲密度への反応。
* 効用関数。
* 行動ルールの比較。
* 確率的行動。
* シナリオ比較。

### 数式

効用関数の例：

```math
U_i
=
-\alpha d_i
-
\beta \rho_i
-
\gamma C_i
+
\delta P_i
```

行動選択：

```math
a_i(t)
=
\arg\max_a U_i(a)
```

または確率的選択：

```math
P(a_i = a)
=
\frac{\exp(\lambda U_i(a))}
{\sum_{a'} \exp(\lambda U_i(a'))}
```

### notebook 要件

`06_train_boarding_behavior_rules.ipynb` では、ドア付近滞留者の行動タイプを切り替えられるようにする。

必須セル：

1. 第5章のモデルの再利用。
2. 行動タイプの定義。
3. 固定型、横移動型、一時降車型の比較。
4. 複数回シミュレーション。
5. 停車時間の分布。
6. 箱ひげ図またはヒストグラム。
7. 密度ヒートマップ。
8. 卒研で実測動画に接続するためのメモ。

---

## 14. 第7章：恋愛モデル I

ファイル名：

```text
chapters/07_love_dynamics_basic.md
notebooks/07_love_dynamics_two_person.ipynb
```

### 章の目的

ストロガッツの2人恋愛モデルを復習し、外力項や飽和項を加えて物語への応用を考える。

### 含める内容

* Romeo and Juliet 型モデル。
* 2変数線形常微分方程式。
* 固有値。
* 相図。
* 安定性。
* 渦状の関係。
* 外部イベント。
* 感情の飽和。
* ドラマやアニメのエピソードへの対応。

### 数式

基本モデル：

```math
\frac{dR}{dt}
=
aR + bJ
```

```math
\frac{dJ}{dt}
=
cR + dJ
```

外力項付きモデル：

```math
\frac{dR}{dt}
=
aR + bJ + F_R(t)
```

```math
\frac{dJ}{dt}
=
cR + dJ + F_J(t)
```

飽和項付きモデル：

```math
\frac{dR}{dt}
=
aR + bJ - \lambda R^3
```

```math
\frac{dJ}{dt}
=
cR + dJ - \mu J^3
```

### notebook 要件

`07_love_dynamics_two_person.ipynb` では、2人モデルの相図と時系列を描く。

必須セル：

1. ライブラリ読み込み。
2. パラメータ設定。
3. ODE の定義。
4. 数値積分。
5. 時系列プロット。
6. 相図。
7. 外力イベントの追加。
8. パラメータを変えた比較。

---

## 15. 第8章：恋愛モデル II

ファイル名：

```text
chapters/08_love_dynamics_network.md
notebooks/08_love_dynamics_network.ipynb
```

### 章の目的

恋愛感情を複数人の有向重み付きネットワークとして表し、三角関係や群像劇に拡張する。

### 含める内容

* 複数人の感情変数。
* 感情行列。
* 有向重み付きネットワーク。
* 三角関係。
* 嫉妬、応援、ライバル意識。
* 物語イベント。
* 各話ごとのアノテーション。
* モデル予測と観測された感情変化の比較。
* ネットワーク図による可視化。

### 数式

人物 (i) が人物 (j) に抱く感情：

```math
x_{ij}(t)
```

複数人モデル：

```math
\frac{dx_{ij}}{dt}
=
a_{ij}x_{ij}
+
b_{ij}x_{ji}
+
\sum_{k \neq i,j} c_{ijk}x_{kj}
+
F_{ij}(t)
```

感情行列：

```math
X(t)
=
(x_{ij}(t))
```

予測誤差：

```math
L
=
\sum_t \|X_{t+1} - \hat{X}_{t+1}\|^2
```

### notebook 要件

`08_love_dynamics_network.ipynb` では、3人または4人の恋愛ネットワークをシミュレーションする。

必須セル：

1. 人物リストの定義。
2. 感情行列の初期化。
3. 更新規則。
4. 三角関係モデル。
5. 外部イベント。
6. 時系列プロット。
7. networkx による有向グラフ表示。
8. エピソードごとの仮想アノテーションとの比較。

---

## 16. Notebook 共通要件

すべての notebook は、以下を満たすこと。

* 上から順に実行できる。
* 外部データなしで動く。
* 乱数を使う場合は seed を固定する。
* 計算時間は通常のノートPCで1分以内を目安にする。
* 図は matplotlib で作る。
* seaborn は使わない。
* 章本文からリンクされている。
* notebook 冒頭に対応章へのリンクを含める。
* 最後に「自分で変更する課題」セルを置く。
* 学生がパラメータを変えやすいよう、設定セルを上部にまとめる。

各 notebook の冒頭には以下のような Markdown セルを入れる。

```markdown
# Notebook タイトル

対応章: `../chapters/xx_xxx.md`

この notebook は、卒業研究準備セミナーの数値実験用である。上から順に実行すれば、本文で説明した図を再現できる。
```

---

## 17. Python 環境

`requirements.txt` には以下を含める。

```text
numpy
scipy
matplotlib
pandas
scikit-image
networkx
jupyter
nbconvert
nbformat
pytest
```

`environment.yml` も作成する。

```yaml
name: modeling-seminar
channels:
  - conda-forge
dependencies:
  - python=3.11
  - numpy
  - scipy
  - matplotlib
  - pandas
  - scikit-image
  - networkx
  - jupyter
  - nbconvert
  - nbformat
  - pytest
  - pip
  - pip:
      - mystmd
```

ただし、`mystmd` の導入方法は環境により npm 経由の方が安定する可能性がある。GitHub Actions では Node.js をセットアップして `npm install -g mystmd` を使う。

---

## 18. GitHub Actions

`.github/workflows/pages.yml` を作成する。

目的は、`main` ブランチへの push または手動実行時に MyST book を HTML にビルドし、GitHub Pages に公開することである。

初期案は以下。

```yaml
name: Deploy MyST site to GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Setup Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.11'

      - name: Setup Node.js
        uses: actions/setup-node@v5
        with:
          node-version: '22'

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Install MyST
        run: |
          npm install -g mystmd

      - name: Check notebooks
        run: |
          python scripts/check_notebooks.py

      - name: Build MyST HTML
        run: |
          myst build --html

      - name: Configure Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v4
        with:
          path: _build/html

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

GitHub Actions のバージョンは、Claude Code が利用時点で妥当な最新版を確認し、必要なら調整すること。

---

## 19. notebook 確認スクリプト

`scripts/check_notebooks.py` を作成する。

目的は、notebook が存在し、最低限読み込めることを確認することである。時間が長くなる場合、CI では全 notebook の実行までは必須にしない。ただし、ローカルでは実行確認できるようにする。

初期案：

```python
from pathlib import Path
import nbformat

NOTEBOOKS = [
    "notebooks/01_stegosaurus_heat_1d_fin.ipynb",
    "notebooks/02_stegosaurus_shape_comparison.ipynb",
    "notebooks/03_reaction_diffusion_gray_scott.ipynb",
    "notebooks/04_snake_pattern_features.ipynb",
    "notebooks/05_train_boarding_ca.ipynb",
    "notebooks/06_train_boarding_behavior_rules.ipynb",
    "notebooks/07_love_dynamics_two_person.ipynb",
    "notebooks/08_love_dynamics_network.ipynb",
]

def main():
    for name in NOTEBOOKS:
        path = Path(name)
        if not path.exists():
            raise FileNotFoundError(f"Missing notebook: {path}")
        nbformat.read(path, as_version=4)
    print("All notebooks exist and are valid nbformat files.")

if __name__ == "__main__":
    main()
```

必要に応じて、`--execute` オプションを持つ実行確認モードを追加してよい。

---

## 20. ローカルでの使い方

### 20.1 環境構築

pip を使う場合：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
npm install -g mystmd
```

conda を使う場合：

```bash
conda env create -f environment.yml
conda activate modeling-seminar
npm install -g mystmd
```

### 20.2 ローカルプレビュー

```bash
myst start
```

### 20.3 HTML ビルド

```bash
myst build --html
```

HTML は以下に生成される。

```text
_build/html
```

---

## 21. GitHub Pages 公開手順

1. GitHub にリポジトリを作成する。
2. この教材一式を push する。
3. GitHub の Settings から Pages を開く。
4. Source を GitHub Actions に設定する。
5. `main` ブランチに push する。
6. Actions の `Deploy MyST site to GitHub Pages` が成功することを確認する。
7. Pages の URL から教材を確認する。

---

## 22. 文体と教育方針

本文は日本語で書く。

文体は、学部4年生向けの講義ノートとして、次の方針を守る。

* 厳密性よりも、モデル化の見通しを優先する。
* ただし、数式の意味は曖昧にしない。
* 変数とパラメータを必ず説明する。
* 「何を仮定したか」を明示する。
* 「何を無視したか」を明示する。
* 先行研究を断定的に言い過ぎない。
* 卒業研究で検証可能な問いに落とす。
* 数値実験の結果を、単なる絵ではなく評価指標と結びつける。

---

## 23. 科学的注意点

### 23.1 ステゴサウルス背板

ステゴサウルス背板については、放熱機能を断定しない。

避ける表現：

```text
ステゴサウルスの背板は放熱のために進化した。
```

使う表現：

```text
ステゴサウルスの背板には、放熱機能があった可能性が議論されている。
```

または、

```text
本章では、放熱効率という観点から、トゲ状構造と板状構造を比較する。
```

### 23.2 ヘビ模様

反応拡散だけで実際のヘビ模様が完全に決まると断定しない。

遺伝、発生、成長、鱗構造、環境、撮影条件の影響を注意点として述べる。

### 23.3 電車乗降

実際の鉄道事業者の運用や安全基準を直接評価する教材ではない。あくまで、ドア付近の局所的行動が流れに与える影響を理解する簡略モデルである。

### 23.4 恋愛モデル

実在人物の評価には使わない。ドラマ・アニメ・仮想データを対象とし、数理モデルの教材として扱う。

---

## 24. 受け入れ条件

Claude Code は、作業完了前に以下を確認すること。

### ファイル構成

* [ ] `README.md` がある。
* [ ] `myst.yml` がある。
* [ ] `chapters/index.md` がある。
* [ ] `chapters/00_research_design.md` がある。
* [ ] 第1章から第8章までの `.md` がある。
* [ ] 対応する8個の `.ipynb` がある。
* [ ] `.github/workflows/pages.yml` がある。
* [ ] `requirements.txt` がある。
* [ ] `environment.yml` がある。

### 内容

* [ ] 各章が独立して読める。
* [ ] 各章に目的、モデル、数式、パラメータ説明、数値実験、卒研への接続、演習がある。
* [ ] 各章から対応 notebook にリンクしている。
* [ ] 各 notebook から対応章にリンクしている。
* [ ] 共通読書資料は輪講対象でないことが明記されている。
* [ ] ステゴサウルス背板の放熱機能を断定していない。
* [ ] 反応拡散によるヘビ模様を過度に断定していない。
* [ ] 電車乗降モデルが簡略モデルであることを明記している。
* [ ] 恋愛モデルが仮想・作品分析用であることを明記している。

### 実行

* [ ] `python scripts/check_notebooks.py` が成功する。
* [ ] `myst build --html` が成功する。
* [ ] `_build/html/index.html` が生成される。
* [ ] GitHub Actions workflow が構文的に妥当である。

---

## 25. Claude Code への作業指示

Claude Code は、この README.md を読んだうえで、以下の順に作業すること。

1. リポジトリ構造を作成する。
2. `myst.yml` を作成する。
3. `chapters/index.md` を作成する。
4. 共通読書資料を作成する。
5. 第1章から第8章の Markdown 原稿を作成する。
6. 各章に対応する notebook を作成する。
7. `requirements.txt` と `environment.yml` を作成する。
8. notebook 確認スクリプトを作成する。
9. GitHub Actions workflow を作成する。
10. ローカルで可能な範囲で検証する。
11. 不整合があれば修正する。

本文生成時には、章ごとの内容が浅くなりすぎないようにする。各章には、少なくとも1つの中心的な数式、1つの図示可能な数値実験、2つ以上の演習問題を含めること。

Notebook は、教育用の最小実装を優先する。過度に複雑なクラス設計や外部データ依存は避ける。学生がセルを読み、パラメータを変えて、結果の変化を確認できる構成にする。

---

## 26. 最終成果物

最終成果物は、以下の状態である。

```text
MyST book として読める日本語教材
+
学生が実行できる Jupyter Notebook
+
GitHub Pages で公開できる GitHub Actions 設定
```

この教材により、学生は2週間の輪講後に、自分の卒業研究について以下を説明できるようになることを目標とする。

* 何を状態変数にするか。
* 何をパラメータにするか。
* どの方程式または更新規則を使うか。
* どの数値シミュレーションを行うか。
* 何を評価指標にするか。
* 卒論に載せる最初の図は何か。

