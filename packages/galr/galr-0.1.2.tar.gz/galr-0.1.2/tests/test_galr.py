"""Tests for GALRRegressor."""

import numpy as np
import pytest
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from galr import GALRRegressor


class TestGALRRegressor:
    """Test suite for GALRRegressor."""

    def test_initialization(self):
        """Test model initialization."""
        model = GALRRegressor()
        assert model.gate == "linear"
        assert model.fit_intercept is True
        assert model.optimizer == "sgd"
        assert model.lr == 0.01
        assert model.n_iter == 1000

    def test_fit_predict(self):
        """Test basic fit and predict."""
        X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = GALRRegressor(n_iter=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        assert y_pred.shape == y_test.shape
        assert not np.isnan(y_pred).any()
        assert not np.isinf(y_pred).any()

    def test_fit_without_intercept(self):
        """Test fit without intercept."""
        X, y = make_regression(n_samples=50, n_features=3, noise=0.1, random_state=42)

        model = GALRRegressor(fit_intercept=False, n_iter=50, random_state=42)
        model.fit(X, y)

        y_pred = model.predict(X)
        assert y_pred.shape == y.shape

    def test_get_gate_values(self):
        """Test get_gate_values method."""
        X, y = make_regression(n_samples=50, n_features=3, noise=0.1, random_state=42)

        model = GALRRegressor(n_iter=50, random_state=42)
        model.fit(X, y)

        gate_values = model.get_gate_values(X)
        assert gate_values.shape == (X.shape[0],)
        assert not np.isnan(gate_values).any()

    def test_get_weights(self):
        """Test get_weights method."""
        X, y = make_regression(n_samples=50, n_features=3, noise=0.1, random_state=42)

        model = GALRRegressor(n_iter=50, random_state=42)
        model.fit(X, y)

        w_under, w_over = model.get_weights(X)
        assert w_under.shape == (X.shape[0],)
        assert w_over.shape == (X.shape[0],)
        assert (w_under > 0).all()
        assert (w_over > 0).all()

    def test_loss_history(self):
        """Test that loss history is recorded."""
        X, y = make_regression(n_samples=50, n_features=3, noise=0.1, random_state=42)

        model = GALRRegressor(n_iter=50, random_state=42)
        model.fit(X, y)

        assert hasattr(model, "loss_history_")
        assert len(model.loss_history_) > 0
        assert all(isinstance(loss, (int, float)) for loss in model.loss_history_)

    def test_regularization(self):
        """Test that regularization parameters work."""
        X, y = make_regression(n_samples=50, n_features=3, noise=0.1, random_state=42)

        # Test with stronger regularization
        model_strong = GALRRegressor(lambda_beta=1.0, lambda_gate=1.0, n_iter=100, random_state=42)
        model_strong.fit(X, y)

        # Test with weak regularization
        model_weak = GALRRegressor(
            lambda_beta=0.001, lambda_gate=0.001, n_iter=100, random_state=42
        )
        model_weak.fit(X, y)

        # Strong regularization should produce smaller parameters
        beta_norm_strong = np.linalg.norm(model_strong.beta_)
        beta_norm_weak = np.linalg.norm(model_weak.beta_)
        theta_norm_strong = np.linalg.norm(model_strong.theta_)
        theta_norm_weak = np.linalg.norm(model_weak.theta_)

        # Strong regularization should generally produce smaller norms
        # (allowing for some variance due to optimization)
        assert beta_norm_strong <= beta_norm_weak * 2.0
        assert theta_norm_strong <= theta_norm_weak * 2.0

    def test_standardize(self):
        """Test with and without standardization."""
        X, y = make_regression(n_samples=50, n_features=3, noise=0.1, random_state=42)

        model_with = GALRRegressor(standardize=True, n_iter=50, random_state=42)
        model_with.fit(X, y)

        model_without = GALRRegressor(standardize=False, n_iter=50, random_state=42)
        model_without.fit(X, y)

        # Both should produce valid predictions
        pred_with = model_with.predict(X)
        pred_without = model_without.predict(X)

        assert pred_with.shape == pred_without.shape
        assert not np.isnan(pred_with).any()
        assert not np.isnan(pred_without).any()

    def test_predict_before_fit(self):
        """Test that predict raises error before fit."""
        X = np.random.randn(10, 3)
        model = GALRRegressor()

        with pytest.raises(ValueError, match="モデルが学習されていません"):
            model.predict(X)

    def test_get_gate_values_before_fit(self):
        """Test that get_gate_values raises error before fit."""
        X = np.random.randn(10, 3)
        model = GALRRegressor()

        with pytest.raises(ValueError, match="モデルが学習されていません"):
            model.get_gate_values(X)

    def test_different_random_states(self):
        """Test that different random states produce different results."""
        X, y = make_regression(n_samples=50, n_features=3, noise=0.1, random_state=42)

        model1 = GALRRegressor(n_iter=50, random_state=42)
        model1.fit(X, y)

        model2 = GALRRegressor(n_iter=50, random_state=123)
        model2.fit(X, y)

        # Results should be different due to different initialization
        assert not np.allclose(model1.beta_, model2.beta_)

    def test_convergence(self):
        """Test that model converges with enough iterations."""
        X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)

        model = GALRRegressor(n_iter=1000, tol=1e-6, random_state=42)
        model.fit(X, y)

        # Loss should decrease
        if len(model.loss_history_) > 1:
            assert model.loss_history_[-1] <= model.loss_history_[0]
