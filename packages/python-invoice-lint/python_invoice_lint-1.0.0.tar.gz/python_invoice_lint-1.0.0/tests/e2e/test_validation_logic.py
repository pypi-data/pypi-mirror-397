import pytest
from invoice_lint.artifact_manager import ArtifactManager
from invoice_lint.validator import Validator

@pytest.mark.e2e
class TestE2E:
    # Requires network or cached artifacts
    # We use the version we know exists/we downloaded: 1.3.15
    
    def test_valid_invoice_pass(self, sample_invoice_path):
        # Ensure artifact is ready (ArtifactManager handles download)
        manager = ArtifactManager()
        path = manager.get_artifact_path("1.3.15")
        
        v = Validator(path)
        result = v.validate(sample_invoice_path, syntax="UBL")
        
        assert result["result"] == "PASS", f"Errors: {result['errors']}"

    def test_invalid_invoice_fail(self, invalid_invoice_path):
        # Contains broken calculation
        manager = ArtifactManager()
        path = manager.get_artifact_path("1.3.15")
        
        v = Validator(path)
        result = v.validate(invalid_invoice_path, syntax="UBL")
        
        assert result["result"] == "FAIL"
        # Check for specific rule if possible. 
        # The invalid_invoice fixture breaks PayableAmount. 
        # Expected rule might be BR-CO-25 or similar.
        error_rules = [e['rule_id'] for e in result['errors']]
        # Assert at least one error
        assert len(error_rules) > 0
