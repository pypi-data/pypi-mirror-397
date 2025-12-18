"""Test suite for scorio.eval module."""

import numpy as np
import pytest
from scorio import eval


class TestAvg:
    """Tests for avg() function."""

    def test_avg_basic(self):
        """Test simple average calculation."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])
        result = eval.avg(R)
        assert result == 0.7

    def test_avg_all_zeros(self):
        """Test average with all zeros."""
        R = np.array([[0, 0, 0], [0, 0, 0]])
        result = eval.avg(R)
        assert result == 0.0

    def test_avg_all_ones(self):
        """Test average with all ones."""
        R = np.array([[1, 1, 1], [1, 1, 1]])
        result = eval.avg(R)
        assert result == 1.0

    def test_avg_single_row(self):
        """Test average with single row."""
        R = np.array([[0, 1, 1, 0]])
        result = eval.avg(R)
        assert result == 0.5


class TestBayes:
    """Tests for bayes() function."""

    def test_bayes_with_prior(self):
        """Test Bayesian evaluation with prior outcomes."""
        R = np.array([[0, 1, 2, 2, 1], [1, 1, 0, 2, 2]])
        w = np.array([0.0, 0.5, 1.0])
        R0 = np.array([[0, 2], [1, 2]])

        mu, sigma = eval.bayes(R, w, R0)
        assert abs(mu - 0.575) < 1e-6
        assert abs(sigma - 0.084275) < 1e-6

    def test_bayes_without_prior(self):
        """Test Bayesian evaluation without prior outcomes."""
        R = np.array([[0, 1, 2, 2, 1], [1, 1, 0, 2, 2]])
        w = np.array([0.0, 0.5, 1.0])

        mu, sigma = eval.bayes(R, w)
        assert abs(mu - 0.5625) < 1e-6
        assert abs(sigma - 0.091998) < 1e-6

    def test_bayes_binary(self):
        """Test Bayesian evaluation with binary outcomes."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])
        w = np.array([0.0, 1.0])

        mu, sigma = eval.bayes(R, w)
        assert 0.0 <= mu <= 1.0
        assert sigma > 0

    def test_bayes_single_system(self):
        """Test Bayesian evaluation with single system."""
        R = np.array([[1, 1, 0, 1, 1]])
        w = np.array([0.0, 1.0])

        mu, sigma = eval.bayes(R, w)
        assert 0.0 <= mu <= 1.0
        assert sigma >= 0

    def test_bayes_invalid_entries(self):
        """Test that invalid entries raise ValueError."""
        R = np.array([[0, 1, 3]])  # 3 is invalid for C=1
        w = np.array([0.0, 1.0])

        with pytest.raises(ValueError, match="Entries of R must be integers"):
            eval.bayes(R, w)


class TestPassAtK:
    """Tests for pass_at_k() function."""

    def test_pass_at_k_basic(self):
        """Test Pass@k with basic example."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])

        result_k1 = eval.pass_at_k(R, 1)
        assert abs(result_k1 - 0.7) < 1e-6

        result_k2 = eval.pass_at_k(R, 2)
        assert abs(result_k2 - 0.95) < 1e-6

    def test_pass_at_k_all_correct(self):
        """Test Pass@k when all trials are correct."""
        R = np.array([[1, 1, 1, 1, 1]])
        result = eval.pass_at_k(R, 3)
        assert result == 1.0

    def test_pass_at_k_all_incorrect(self):
        """Test Pass@k when all trials are incorrect."""
        R = np.array([[0, 0, 0, 0, 0]])
        result = eval.pass_at_k(R, 3)
        assert result == 0.0

    def test_pass_at_k_k_equals_n(self):
        """Test Pass@k when k equals N."""
        R = np.array([[1, 0, 1], [0, 1, 1]])
        result = eval.pass_at_k(R, 3)
        assert 0.0 <= result <= 1.0

    def test_pass_at_k_invalid_k(self):
        """Test that invalid k raises ValueError."""
        R = np.array([[1, 0, 1]])

        with pytest.raises(ValueError, match="k must satisfy"):
            eval.pass_at_k(R, 0)

        with pytest.raises(ValueError, match="k must satisfy"):
            eval.pass_at_k(R, 4)


class TestPassHatK:
    """Tests for pass_hat_k() function."""

    def test_pass_hat_k_basic(self):
        """Test Pass^k with basic example."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])

        result_k1 = eval.pass_hat_k(R, 1)
        assert abs(result_k1 - 0.7) < 1e-6

        result_k2 = eval.pass_hat_k(R, 2)
        assert abs(result_k2 - 0.45) < 1e-6

    def test_pass_hat_k_all_correct(self):
        """Test Pass^k when all trials are correct."""
        R = np.array([[1, 1, 1, 1, 1]])
        result = eval.pass_hat_k(R, 3)
        assert result == 1.0

    def test_pass_hat_k_all_incorrect(self):
        """Test Pass^k when all trials are incorrect."""
        R = np.array([[0, 0, 0, 0, 0]])
        result = eval.pass_hat_k(R, 3)
        assert result == 0.0

    def test_pass_hat_k_comparison_with_pass_at_k(self):
        """Test that Pass^k <= Pass@k."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])
        k = 2

        pass_k = eval.pass_at_k(R, k)
        pass_hat = eval.pass_hat_k(R, k)
        assert pass_hat <= pass_k


class TestGPassAtK:
    """Tests for g_pass_at_k() function."""

    def test_g_pass_at_k_alias(self):
        """Test that g_pass_at_k is an alias for pass_hat_k."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])

        result_alias = eval.g_pass_at_k(R, 2)
        result_original = eval.pass_hat_k(R, 2)
        assert result_alias == result_original


class TestGPassAtKTao:
    """Tests for g_pass_at_k_tao() function."""

    def test_g_pass_at_k_tao_basic(self):
        """Test G-Pass@k_τ with basic example."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])

        result_tau_05 = eval.g_pass_at_k_tao(R, 2, 0.5)
        assert abs(result_tau_05 - 0.95) < 1e-6

        result_tau_10 = eval.g_pass_at_k_tao(R, 2, 1.0)
        assert abs(result_tau_10 - 0.45) < 1e-6

    def test_g_pass_at_k_tao_zero(self):
        """Test that τ=0 is equivalent to Pass@k."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])
        k = 2

        result_tau_zero = eval.g_pass_at_k_tao(R, k, 0.0)
        result_pass_k = eval.pass_at_k(R, k)
        assert abs(result_tau_zero - result_pass_k) < 1e-10

    def test_g_pass_at_k_tao_one(self):
        """Test that τ=1 is equivalent to Pass^k."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])
        k = 2

        result_tau_one = eval.g_pass_at_k_tao(R, k, 1.0)
        result_pass_hat = eval.pass_hat_k(R, k)
        assert abs(result_tau_one - result_pass_hat) < 1e-10

    def test_g_pass_at_k_tao_invalid_tau(self):
        """Test that invalid τ raises ValueError."""
        R = np.array([[1, 0, 1]])

        with pytest.raises(ValueError, match="tao must be in"):
            eval.g_pass_at_k_tao(R, 2, -0.1)

        with pytest.raises(ValueError, match="tao must be in"):
            eval.g_pass_at_k_tao(R, 2, 1.5)

    def test_g_pass_at_k_tao_monotonicity(self):
        """Test that G-Pass@k_τ decreases as τ increases."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])
        k = 3

        result_tau_0 = eval.g_pass_at_k_tao(R, k, 0.0)
        result_tau_05 = eval.g_pass_at_k_tao(R, k, 0.5)
        result_tau_1 = eval.g_pass_at_k_tao(R, k, 1.0)

        assert result_tau_0 >= result_tau_05 >= result_tau_1


class TestMGPassAtK:
    """Tests for mg_pass_at_k() function."""

    def test_mg_pass_at_k_basic(self):
        """Test mG-Pass@k with basic example."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])

        result_k2 = eval.mg_pass_at_k(R, 2)
        assert abs(result_k2 - 0.45) < 1e-6

        result_k3 = eval.mg_pass_at_k(R, 3)
        assert abs(result_k3 - 0.166667) < 1e-6

    def test_mg_pass_at_k_all_correct(self):
        """Test mG-Pass@k when all trials are correct."""
        R = np.array([[1, 1, 1, 1, 1]])
        result = eval.mg_pass_at_k(R, 3)
        assert result > 0

    def test_mg_pass_at_k_all_incorrect(self):
        """Test mG-Pass@k when all trials are incorrect."""
        R = np.array([[0, 0, 0, 0, 0]])
        result = eval.mg_pass_at_k(R, 3)
        assert result == 0.0

    def test_mg_pass_at_k_bounds(self):
        """Test that mG-Pass@k is in valid range."""
        R = np.array([[0, 1, 1, 0, 1], [1, 1, 0, 1, 1]])

        for k in range(1, 6):
            result = eval.mg_pass_at_k(R, k)
            assert 0.0 <= result <= 1.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_1d_array_conversion(self):
        """Test that 1D arrays are converted to 2D."""
        R = np.array([0, 1, 1, 0, 1])
        result = eval.avg(R)
        assert result == 0.6

    def test_single_trial(self):
        """Test functions with single trial."""
        R = np.array([[1], [0]])

        avg_result = eval.avg(R)
        assert avg_result == 0.5

        pass_result = eval.pass_at_k(R, 1)
        assert pass_result == 0.5

    def test_large_matrix(self):
        """Test with larger matrix."""
        np.random.seed(42)
        R = np.random.randint(0, 2, size=(100, 50))

        avg_result = eval.avg(R)
        assert 0.0 <= avg_result <= 1.0

        pass_result = eval.pass_at_k(R, 10)
        assert 0.0 <= pass_result <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
