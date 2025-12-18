"""Tests for emptyDir size parameter validation."""
import pytest
from aiauto.core import _parse_size_to_gi


class TestParseSizeToGi:
    """Test size parsing helper function."""

    def test_parse_mi_to_gi(self):
        """Test Mi to Gi conversion."""
        assert _parse_size_to_gi("500Mi") == pytest.approx(0.48828125, rel=1e-6)
        assert _parse_size_to_gi("1024Mi") == pytest.approx(1.0, rel=1e-6)
        assert _parse_size_to_gi("2048Mi") == pytest.approx(2.0, rel=1e-6)

    def test_parse_gi(self):
        """Test Gi parsing."""
        assert _parse_size_to_gi("1Gi") == 1.0
        assert _parse_size_to_gi("4Gi") == 4.0
        assert _parse_size_to_gi("0.5Gi") == 0.5

    def test_parse_empty_string(self):
        """Test empty string returns 0."""
        assert _parse_size_to_gi("") == 0.0

    def test_parse_invalid_format(self):
        """Test invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid size format"):
            _parse_size_to_gi("500")
        with pytest.raises(ValueError, match="Invalid size format"):
            _parse_size_to_gi("abc")
        with pytest.raises(ValueError, match="Invalid size format"):
            _parse_size_to_gi("500 Mi")

    def test_parse_unsupported_unit(self):
        """Test unsupported unit raises ValueError."""
        # Note: Current implementation actually supports only Mi, Gi, M, G
        # If Ki, Ti etc are not supported, they should raise an error
        with pytest.raises(ValueError, match="Invalid size format"):
            _parse_size_to_gi("500Ki")


# Note: The following tests require mocking the HTTP client
# since optimize() makes actual network requests.
# For now, we document the expected behavior:

# class TestOptimizeValidation:
#     """Test optimize() parameter validation.
#
#     These tests require mocking ConnectRPCClient to avoid actual network calls.
#     """
#
#     def test_cpu_with_custom_dev_shm_size_raises_error(self, mock_client):
#         """CPU 사용 시 dev_shm_size 커스텀 지정하면 오류."""
#         ac = AIAutoController('<test-token>')
#         study_wrapper = ac.create_study('test-study', direction='minimize')
#
#         with pytest.raises(ValueError, match="can only be used with GPU"):
#             study_wrapper.optimize(
#                 lambda trial: 1.0,
#                 n_trials=1,
#                 use_gpu=False,  # CPU
#                 dev_shm_size="4Gi"  # Custom size
#             )
#
#     def test_dev_shm_size_exceeds_max_raises_error(self, mock_client):
#         """dev_shm_size max 4Gi 초과 시 오류."""
#         ac = AIAutoController('<test-token>')
#         study_wrapper = ac.create_study('test-study', direction='minimize')
#
#         with pytest.raises(ValueError, match="exceeds maximum allowed size of 4Gi"):
#             study_wrapper.optimize(
#                 lambda trial: 1.0,
#                 n_trials=1,
#                 use_gpu=True,
#                 dev_shm_size="8Gi"  # Exceeds 4Gi
#             )
#
#     def test_tmp_cache_size_exceeds_max_raises_error(self, mock_client):
#         """tmp_cache_size max 4Gi 초과 시 오류."""
#         ac = AIAutoController('<test-token>')
#         study_wrapper = ac.create_study('test-study', direction='minimize')
#
#         with pytest.raises(ValueError, match="exceeds maximum allowed size of 4Gi"):
#             study_wrapper.optimize(
#                 lambda trial: 1.0,
#                 n_trials=1,
#                 tmp_cache_size="10Gi"  # Exceeds 4Gi
#             )
#
#     def test_invalid_size_format_raises_error(self, mock_client):
#         """잘못된 크기 형식은 오류."""
#         ac = AIAutoController('<test-token>')
#         study_wrapper = ac.create_study('test-study', direction='minimize')
#
#         with pytest.raises(ValueError, match="Invalid size format"):
#             study_wrapper.optimize(
#                 lambda trial: 1.0,
#                 n_trials=1,
#                 use_gpu=True,
#                 dev_shm_size="500"  # Missing unit
#             )
