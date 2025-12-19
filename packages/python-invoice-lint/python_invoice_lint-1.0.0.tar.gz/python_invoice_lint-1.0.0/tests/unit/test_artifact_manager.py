import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from invoice_lint.artifact_manager import ArtifactManager

class TestArtifactManager:
    @pytest.fixture
    def manager(self, tmp_path):
        return ArtifactManager(cache_dir=tmp_path / "cache")

    @patch("requests.get")
    def test_download_artifact_success(self, mock_get, manager):
        # Mock successful download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        
        # Create a dummy zip content
        import io
        import zipfile
        b = io.BytesIO()
        with zipfile.ZipFile(b, 'w') as zf:
            zf.writestr('test-version/dummy.txt', 'content')
        b.seek(0)
        
        mock_response.iter_content.return_value = [b.read()]
        mock_get.return_value = mock_response

        # Test
        path = manager.get_artifact_path("1.0.0")
        
        assert path.exists()
        # Zip file contained a top-level folder 'test-version'
        if not (path / "test-version" / "dummy.txt").exists():
            print(list(path.rglob("*")))
        assert (path / "test-version" / "dummy.txt").exists()
        assert (path / "test-version" / "dummy.txt").read_text() == "content"

    @patch("requests.get")
    def test_download_artifact_retry_with_validation_prefix(self, mock_get, manager):
        # Mock 404 for first call, 200 for second (validation-1.0.0)
        mock_resp_404 = MagicMock()
        mock_resp_404.status_code = 404
        
        mock_resp_200 = MagicMock()
        mock_resp_200.status_code = 200
        mock_resp_200.raise_for_status.return_value = None
        
        # Dummy zip
        import io
        import zipfile
        b = io.BytesIO()
        with zipfile.ZipFile(b, 'w') as zf:
            zf.writestr('validation-1.0.0/dummy.txt', 'content')
        b.seek(0)
        mock_resp_200.iter_content.return_value = [b.read()]

        # Side effect sequence
        mock_get.side_effect = [mock_resp_404, mock_resp_200]

        path = manager.get_artifact_path("1.0.0")
        
        assert path.exists()
        # Ensure it tried both urls
        assert mock_get.call_count == 2
        args1, _ = mock_get.call_args_list[0]
        args2, _ = mock_get.call_args_list[1]
        assert "validation-" not in args1[0] or "tags/1.0.0" in args1[0]
        assert "validation-1.0.0" in args2[0]

    def test_cache_hit(self, manager):
        # Prepare cache
        (manager.cache_dir / "1.2.3").mkdir(parents=True)
        
        with patch("invoice_lint.artifact_manager.ArtifactManager.download_artifact") as mock_dl:
            path = manager.get_artifact_path("1.2.3")
            assert path.exists()
            mock_dl.assert_not_called()
