"""
GALRRegressor: Gated Asymmetric Linear Regression

特徴量に応じて上振れ/下振れのペナルティを学習する回帰モデル
"""

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_X_y, check_array
from sklearn.utils import check_random_state


def softplus(z):
    """
    softplus関数: log(1 + exp(z))
    数値安定性のため、zが大きい場合はz + log(1 + exp(-z))を使用
    """
    return np.where(z > 50, z, np.log1p(np.exp(z)))


def sigmoid(z):
    """
    sigmoid関数: 1 / (1 + exp(-z))
    softplusの導関数
    """
    # 数値安定性のため
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


class GALRRegressor(BaseEstimator, RegressorMixin):
    """
    Gated Asymmetric Linear Regression

    特徴量に応じて上振れ（過大予測）と下振れ（過小予測）の
    ペナルティを学習する回帰モデル。

    Parameters
    ----------
    gate : {'linear'}, default='linear'
        ゲート関数のタイプ。現在は'linear'のみ対応。
    fit_intercept : bool, default=True
        切片を学習するかどうか。
    optimizer : {'sgd'}, default='sgd'
        オプティマイザ。現在は'sgd'のみ対応。
    lr : float, default=0.01
        学習率。
    n_iter : int, default=1000
        最大イテレーション数。
    tol : float, default=1e-6
        収束判定の閾値（損失の変化量）。
    lambda_beta : float, default=0.01
        回帰係数βのL2正則化係数。
    lambda_gate : float, default=0.01
        ゲートパラメータθのL2正則化係数。
    epsilon : float, default=1e-6
        softplusの下限値（重みが0にならないようにする）。
    standardize : bool, default=True
        内部でStandardScalerを使用して特徴量を標準化するか。
    random_state : int or RandomState instance, default=None
        乱数シード。
    """

    def __init__(
        self,
        gate="linear",
        fit_intercept=True,
        optimizer="sgd",
        lr=0.01,
        n_iter=1000,
        tol=1e-6,
        lambda_beta=0.01,
        lambda_gate=0.01,
        epsilon=1e-6,
        standardize=True,
        random_state=None,
    ):
        self.gate = gate
        self.fit_intercept = fit_intercept
        self.optimizer = optimizer
        self.lr = lr
        self.n_iter = n_iter
        self.tol = tol
        self.lambda_beta = lambda_beta
        self.lambda_gate = lambda_gate
        self.epsilon = epsilon
        self.standardize = standardize
        self.random_state = random_state

    def _initialize_parameters(self, n_features):
        """パラメータの初期化"""
        rng = check_random_state(self.random_state)

        # 回帰係数
        self.beta_ = rng.normal(0, 0.01, size=n_features)
        self.intercept_ = 0.0 if self.fit_intercept else None

        # ゲートパラメータ（線形ゲート: g(x) = x^T * theta + c）
        self.theta_ = rng.normal(0, 0.01, size=n_features)
        self.gate_intercept_ = 0.0

    def _compute_weights(self, X):
        """
        ゲート関数から重みを計算

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            特徴量

        Returns
        -------
        w_under : array-like of shape (n_samples,)
            下振れ（過小予測）の重み
        w_over : array-like of shape (n_samples,)
            上振れ（過大予測）の重み
        gate_values : array-like of shape (n_samples,)
            ゲート関数の値 g(x)
        """
        # 線形ゲート: g(x) = X @ theta + c
        gate_values = X @ self.theta_ + self.gate_intercept_

        # 重みの計算
        w_under = softplus(gate_values) + self.epsilon
        w_over = softplus(-gate_values) + self.epsilon

        return w_under, w_over, gate_values

    def _compute_loss(self, X, y):
        """
        損失関数を計算

        L = (1/n) * sum_i [1(e_i>0) * w_under(x_i) + 1(e_i<0) * w_over(x_i)] * e_i^2
            + lambda_beta * ||beta||^2 + lambda_gate * ||theta||^2
        """
        # 予測
        y_pred = X @ self.beta_
        if self.fit_intercept:
            y_pred += self.intercept_

        # 残差
        residuals = y - y_pred

        # 重みの計算
        w_under, w_over, _ = self._compute_weights(X)

        # 損失の計算
        # 下振れ（e > 0）と上振れ（e < 0）で異なる重みを適用
        mask_under = residuals > 0
        mask_over = residuals < 0

        weighted_squared_errors = (
            mask_under * w_under * residuals**2 + mask_over * w_over * residuals**2
        )
        data_loss = np.mean(weighted_squared_errors)

        # 正則化項
        reg_beta = self.lambda_beta * np.sum(self.beta_**2)
        reg_gate = self.lambda_gate * (np.sum(self.theta_**2) + self.gate_intercept_**2)

        total_loss = data_loss + reg_beta + reg_gate

        return total_loss, data_loss, reg_beta, reg_gate

    def _compute_gradients(self, X, y):
        """
        勾配を計算

        Returns
        -------
        grad_beta : array-like of shape (n_features,)
            回帰係数βの勾配
        grad_intercept : float or None
            切片の勾配（fit_intercept=Trueの場合）
        grad_theta : array-like of shape (n_features,)
            ゲートパラメータθの勾配
        grad_gate_intercept : float
            ゲート切片の勾配
        """
        n_samples, n_features = X.shape

        # 予測と残差
        y_pred = X @ self.beta_
        if self.fit_intercept:
            y_pred += self.intercept_
        residuals = y - y_pred

        # 重みとゲート値
        w_under, w_over, gate_values = self._compute_weights(X)

        # マスク
        mask_under = residuals > 0
        mask_over = residuals < 0

        # sigmoid(gate_values) と sigmoid(-gate_values) を計算
        sig_gate = sigmoid(gate_values)
        sig_neg_gate = sigmoid(-gate_values)

        # betaの勾配
        # dL/dbeta = -(2/n) * sum_i [1(e_i>0) * w_under(x_i) + 1(e_i<0) * w_over(x_i)] * e_i * x_i
        #            + 2 * lambda_beta * beta
        grad_beta = (
            -2.0
            / n_samples
            * np.sum(
                (mask_under * w_under + mask_over * w_over)[:, np.newaxis]
                * residuals[:, np.newaxis]
                * X,
                axis=0,
            )
            + 2 * self.lambda_beta * self.beta_
        )

        # interceptの勾配（fit_intercept=Trueの場合）
        if self.fit_intercept:
            grad_intercept = (
                -2.0 / n_samples * np.sum((mask_under * w_under + mask_over * w_over) * residuals)
            )
        else:
            grad_intercept = None

        # thetaの勾配
        # dL/dtheta = (1/n) * sum_i [1(e_i>0) * sigmoid(g(x_i)) - 1(e_i<0) * sigmoid(-g(x_i))] * e_i^2 * x_i
        #            + 2 * lambda_gate * theta
        grad_theta = (
            1.0
            / n_samples
            * np.sum(
                (mask_under * sig_gate - mask_over * sig_neg_gate)[:, np.newaxis]
                * (residuals**2)[:, np.newaxis]
                * X,
                axis=0,
            )
            + 2 * self.lambda_gate * self.theta_
        )

        # gate_interceptの勾配
        grad_gate_intercept = (
            1.0
            / n_samples
            * np.sum((mask_under * sig_gate - mask_over * sig_neg_gate) * residuals**2)
            + 2 * self.lambda_gate * self.gate_intercept_
        )

        return grad_beta, grad_intercept, grad_theta, grad_gate_intercept

    def fit(self, X, y):
        """
        モデルを学習

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            訓練データ
        y : array-like of shape (n_samples,)
            ターゲット値

        Returns
        -------
        self : object
            学習済みモデル
        """
        X, y = check_X_y(X, y, y_numeric=True)

        # 標準化
        if self.standardize:
            self.scaler_ = StandardScaler()
            X = self.scaler_.fit_transform(X)
        else:
            self.scaler_ = None

        n_samples, n_features = X.shape

        # パラメータの初期化
        self._initialize_parameters(n_features)

        # 学習履歴（オプション）
        self.loss_history_ = []

        # SGDで最適化
        prev_loss = np.inf
        for iteration in range(self.n_iter):
            # 損失の計算
            loss, _, _, _ = self._compute_loss(X, y)
            self.loss_history_.append(loss)

            # 収束判定
            if abs(prev_loss - loss) < self.tol:
                break
            prev_loss = loss

            # 勾配の計算
            grad_beta, grad_intercept, grad_theta, grad_gate_intercept = self._compute_gradients(
                X, y
            )

            # パラメータの更新
            self.beta_ -= self.lr * grad_beta
            if self.fit_intercept:
                self.intercept_ -= self.lr * grad_intercept
            self.theta_ -= self.lr * grad_theta
            self.gate_intercept_ -= self.lr * grad_gate_intercept

        self.n_iter_ = iteration + 1
        return self

    def predict(self, X):
        """
        予測を実行

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            予測対象のデータ

        Returns
        -------
        y_pred : array-like of shape (n_samples,)
            予測値
        """
        check_array(X)
        if not hasattr(self, "beta_"):
            raise ValueError("モデルが学習されていません。fit()を先に実行してください。")

        # 標準化
        if self.scaler_ is not None:
            X = self.scaler_.transform(X)

        # 予測
        y_pred = X @ self.beta_
        if self.fit_intercept:
            y_pred += self.intercept_

        return y_pred

    def get_gate_values(self, X):
        """
        ゲート関数の値を取得

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            データ

        Returns
        -------
        gate_values : array-like of shape (n_samples,)
            ゲート関数の値 g(x)
        """
        check_array(X)
        if not hasattr(self, "theta_"):
            raise ValueError("モデルが学習されていません。fit()を先に実行してください。")

        # 標準化
        if self.scaler_ is not None:
            X = self.scaler_.transform(X)

        gate_values = X @ self.theta_ + self.gate_intercept_
        return gate_values

    def get_weights(self, X):
        """
        重み（w_under, w_over）を取得

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            データ

        Returns
        -------
        w_under : array-like of shape (n_samples,)
            下振れ（過小予測）の重み
        w_over : array-like of shape (n_samples,)
            上振れ（過大予測）の重み
        """
        check_array(X)
        if not hasattr(self, "theta_"):
            raise ValueError("モデルが学習されていません。fit()を先に実行してください。")

        # 標準化
        if self.scaler_ is not None:
            X = self.scaler_.transform(X)

        w_under, w_over, _ = self._compute_weights(X)
        return w_under, w_over
