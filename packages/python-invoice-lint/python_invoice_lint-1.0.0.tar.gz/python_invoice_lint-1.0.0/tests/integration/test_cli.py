import pytest
import json
from click.testing import CliRunner
from invoice_lint.cli import main

class TestCLI:
    def test_validate_no_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["validate", "--artifact", "1.0.0", "nonexistent.xml"])
        assert result.exit_code != 0
        assert "Path 'nonexistent.xml' does not exist" in result.output

    # def test_validate_success_mock(self, tmp_path):
    #     # Integration test using mocks (Commented out as E2E test covers this scenario better)
    #     pass

    def test_validate_fail_exit_code(self, tmp_path):
        with pytest.MonkeyPatch.context() as m:
            from unittest.mock import MagicMock
            mock_validator = MagicMock()
            mock_validator.validate.return_value = {"result": "FAIL", "errors": [{}]}
            
            m.setattr("invoice_lint.cli.Validator", lambda path: mock_validator)
            m.setattr("invoice_lint.cli.ArtifactManager.get_artifact_path", lambda self, v: Path("/tmp"))
            
            f = tmp_path / "invoice.xml"
            f.write_text("<root/>")
            
            runner = CliRunner()
            result = runner.invoke(main, ["validate", "--artifact", "1.0.0", str(f)])
            
            assert result.exit_code == 1
            assert '"result": "FAIL"' in result.output
