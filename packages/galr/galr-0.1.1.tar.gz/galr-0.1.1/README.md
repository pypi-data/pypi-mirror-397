# Gated Asymmetric Linear Regression (GALR)

「上振れ（過大予測）」と「下振れ（過小予測）」の**ペナルティを固定せず、特徴量に応じて学習する**"ゲート付き非対称線形回帰"パッケージ。

## 概要

従来の cost-sensitive 回帰（上振れ/下振れの重み固定）ではなく、**状況（特徴量 x）に応じてコスト比が変化する**現実の意思決定をモデル化します。

- sklearn 互換 API（`BaseEstimator`, `RegressorMixin`）
- プロダクション運用（再学習・評価・監視）まで想定
- 最小限の依存関係（numpy, scikit-learn）

## インストール

```bash
pip install galr
```

開発版をインストールする場合：

```bash
git clone https://github.com/yourusername/galr.git
cd galr
pip install -e .
```

## 使用方法

```python
from galr import GALRRegressor
import numpy as np

# データの準備
X = np.random.randn(100, 5)
y = np.random.randn(100)

# モデルの学習
model = GALRRegressor(
    gate='linear',
    fit_intercept=True,
    optimizer='sgd',
    lr=0.01,
    n_iter=1000,
    lambda_beta=0.01,
    lambda_gate=0.01,
    epsilon=1e-6,
    random_state=42
)
model.fit(X, y)

# 予測
y_pred = model.predict(X)

# ゲート関数の値を取得（オプション）
gate_values = model.get_gate_values(X)
```

## モデル詳細

### 予測器

```math
\hat{y} = x^\top \beta + b
```

### ゲート関数

ゲート関数 $g(x)$ が「この状況では下振れが痛い／上振れが痛い」を学習します。

```math
w_\mathrm{under}(x) = \mathrm{softplus}(g(x)) + \epsilon
```
```math
w_\mathrm{over}(x) = \mathrm{softplus}(-g(x)) + \epsilon
```

### 損失関数

```math
L(\beta, b, \theta) = \frac{1}{n} \sum_i \Big[ \mathbb{1}(e_i > 0) \cdot w_\mathrm{under}(x_i) + \mathbb{1}(e_i < 0) \cdot w_\mathrm{over}(x_i) \Big] e_i^2 + \lambda_\beta \|\beta\|_2^2 + \lambda_g \|\theta\|_2^2
```


## パラメータ

- `gate`: `'linear'` | `'mlp'`（現在は `'linear'` のみ対応）
- `fit_intercept`: bool - 切片を学習するか
- `optimizer`: `'sgd'` | `'adam'`（現在は `'sgd'` のみ対応）
- `lr`: float - 学習率
- `n_iter`: int - イテレーション数
- `tol`: float - 収束判定の閾値
- `lambda_beta`: float - 回帰係数のL2正則化係数
- `lambda_gate`: float - ゲートパラメータのL2正則化係数
- `epsilon`: float - softplusの下限値
- `standardize`: bool - 内部でStandardScalerを使用するか
- `random_state`: int - 乱数シード

## ライセンス

MIT License

## 開発状況

現在は MVP（最小実装）段階です。将来的には以下を追加予定：

- MLPゲートの実装
- Adamオプティマイザの実装
- より高度な最適化手法
- 詳細なドキュメントとチュートリアル

## CI/CD

このプロジェクトは**GitHub ActionsによるCI/CD**を採用しています。

### 継続的インテグレーション (CI)

**Pull Request作成時に自動実行**:
- **テスト**: 複数のPythonバージョン（3.8-3.13）でテストを実行
- **リント**: flake8によるコード品質チェック
- **型チェック**: mypyによる型チェック
- **ビルド**: パッケージのビルドと検証
- **バージョンチェック**: バージョン形式の検証

### 継続的デプロイ (CD)

- **developブランチからmainへのマージ**: 自動的にバージョンをインクリメントしてPyPIに公開（推奨）
- **mainブランチへの直接プッシュ**: 自動的にバージョンをインクリメントしてPyPIに公開
- **手動実行**: GitHub ActionsのUIからバージョンを指定してリリース可能

詳細は [RELEASE.md](RELEASE.md) を参照してください。

## 開発者向け情報

### PyPIへの公開手順

1. **必要なツールのインストール**
   ```bash
   pip install build twine
   ```

2. **パッケージのビルド**
   ```bash
   python -m build
   ```
   これにより `dist/` ディレクトリに配布用ファイルが生成されます。

3. **ビルドの確認（オプション）**
   ```bash
   # ローカルでテスト
   pip install dist/galr-*.whl
   
   # または、TestPyPIでテスト
   twine upload --repository testpypi dist/*
   ```

4. **PyPIへのアップロード**
   ```bash
   twine upload dist/*
   ```
   
   **注意**: 初回はTestPyPIでテストすることを推奨します：
   ```bash
   twine upload --repository testpypi dist/*
   ```

5. **バージョン更新**
   - `pyproject.toml` の `version` を更新
   - 変更をコミット・タグ付け
   - 再度ビルド・アップロード

### ローカル開発環境のセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/yut0takagi/galr.git
cd galr

# 開発環境のセットアップ
pip install -e ".[dev]"
```

### テスト

```bash
# テストの実行
pytest

# カバレッジ付きテスト
pytest --cov=galr --cov-report=html

# 特定のテストのみ実行
pytest tests/test_galr.py::TestGALRRegressor::test_fit_predict
```

### コード品質チェック

```bash
# リントチェック
flake8 src/ tests/

# コードフォーマットチェック
black --check src/ tests/

# コードフォーマット適用
black src/ tests/

# 型チェック
mypy src/galr
```

