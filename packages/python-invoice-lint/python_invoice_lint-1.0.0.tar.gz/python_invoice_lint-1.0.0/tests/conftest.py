import pytest
from pathlib import Path

@pytest.fixture
def sample_invoice_path():
    return Path(__file__).parent.parent / "invoice.xml"

@pytest.fixture
def invalid_invoice_path(tmp_path):
    # Create an invoice that fails a specific Schematron rule
    # E.g. PayableAmount != TaxInclusiveAmount for BR-CO-25 (simplified)
    # We will just take the valid one and break a calculation
    valid = (Path(__file__).parent.parent / "invoice.xml").read_text()
    
    # Break total amount
    invalid = valid.replace("<cbc:PayableAmount currencyID=\"EUR\">1656.25</cbc:PayableAmount>", "<cbc:PayableAmount currencyID=\"EUR\">9999.99</cbc:PayableAmount>")
    
    p = tmp_path / "invalid_invoice.xml"
    p.write_text(invalid)
    return p

@pytest.fixture
def malformed_invoice_path(tmp_path):
    p = tmp_path / "malformed.xml"
    p.write_text("<Invoice>Unclosed Tag")
    return p
