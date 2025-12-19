import pytest
import tempfile
from pathlib import Path
from invoice_lint.cli import diff

class TestDiff:
    @pytest.fixture
    def mock_sch_files(self, tmp_path):
        d1 = tmp_path / "v1"
        d1.mkdir()
        (d1 / "test-UBL.sch").write_text("""
        <sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
            <sch:assert id="RULE-1">Msg 1</sch:assert>
            <sch:assert id="RULE-2">Msg 2</sch:assert>
        </sch:schema>
        """)
        
        d2 = tmp_path / "v2"
        d2.mkdir()
        (d2 / "test-UBL.sch").write_text("""
        <sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
            <sch:assert id="RULE-2">Msg 2 Changed</sch:assert>
            <sch:assert id="RULE-3">Msg 3</sch:assert>
        </sch:schema>
        """)
        return d1, d2

    def test_diff_engine_cli(self, mock_sch_files):
        from click.testing import CliRunner
        from invoice_lint.cli import main
        import invoice_lint.cli
        
        path1, path2 = mock_sch_files
        
        # Patch ArtifactManager to return local paths
        import pytest
        with pytest.MonkeyPatch.context() as m:
            m.setattr("invoice_lint.artifact_manager.ArtifactManager.get_artifact_path", 
                      lambda self, v: path1 if v == "1.0" else path2)
            
            runner = CliRunner()
            result = runner.invoke(main, ["diff", "--from", "1.0", "--to", "2.0"])
            
            assert result.exit_code == 0
            import json
            data = json.loads(result.output)
            
            assert len(data["rule_changes"]["added"]) == 1
            assert len(data["rule_changes"]["removed"]) == 1
            
            # Impact analysis check (default empty)
            assert data["impact_analysis"]["files_analyzed"] == 0
            
    def test_diff_impact_analysis(self, mock_sch_files):
        from click.testing import CliRunner
        from invoice_lint.cli import main
        import invoice_lint.cli
        from unittest.mock import MagicMock
        
        path1, path2 = mock_sch_files
        
        # Create a mock file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xml") as tmp:
             # Mock Validation results
             # v1: Pass
             # v2: Fail with NEW-RULE
             
             import pytest
             with pytest.MonkeyPatch.context() as m:
                m.setattr("invoice_lint.artifact_manager.ArtifactManager.get_artifact_path", 
                          lambda self, v: path1 if v == "1.0" else path2)
                
                # We need to ensure Validator uses our mocked behavior or real behavior.
                # Since unit test mocks artifacts, real Validator might fail to load XSLT.
                # We should mock Validator.validate.
                
                mock_v1 = MagicMock()
                mock_v1.validate.return_value = {"errors": []}
                
                mock_v2 = MagicMock()
                mock_v2.validate.return_value = {"errors": [{"rule_id": "NEW-RULE"}]}
                
                # The CLI creates new Validator instances. We need to intercept based on path or order.
                # Validator(path_from) -> v1, Validator(path_to) -> v2
                
                def mock_validator_init(path):
                    if path == path1: return mock_v1
                    return mock_v2
                    
                m.setattr("invoice_lint.cli.Validator", mock_validator_init)
                
                runner = CliRunner()
                result = runner.invoke(main, ["diff", "--from", "1.0", "--to", "2.0", tmp.name])
                
                assert result.exit_code == 0
                import json
                data = json.loads(result.output)
                
                assert data["impact_analysis"]["files_analyzed"] == 1
                assert len(data["impact_analysis"]["regressions"]) == 1
                # Check if NEW-RULE is in the returned errors list objects
                new_errors_list = data["impact_analysis"]["regressions"][0]["new_errors"]
                assert any(e['rule_id'] == "NEW-RULE" for e in new_errors_list)
