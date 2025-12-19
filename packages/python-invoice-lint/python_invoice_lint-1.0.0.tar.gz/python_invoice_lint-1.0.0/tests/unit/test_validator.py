import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from lxml import etree
from invoice_lint.validator import Validator

class TestValidator:
    @pytest.fixture
    def mock_artifact_path(self, tmp_path):
        d = tmp_path / "artifacts"
        d.mkdir()
        # Create a dummy XSLT
        (d / "EN16931-UBL-validation.xslt").write_text("""
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
            <xsl:template match="/">
                <svrl:schematron-output>
                    <svrl:failed-assert id="TEST-RULE" location="/root">
                        <svrl:text>Test Error</svrl:text>
                    </svrl:failed-assert>
                </svrl:schematron-output>
            </xsl:template>
        </xsl:stylesheet>
        """)
        return d

    def test_xml_syntax_error(self, mock_artifact_path, tmp_path):
        v = Validator(mock_artifact_path)
        bad_xml = tmp_path / "bad.xml"
        bad_xml.write_text("<root>Unclosed")
        
        result = v.validate(bad_xml)
        assert result["result"] == "FAIL"
        assert result["errors"][0]["rule_id"] == "XML_SYNTAX"

    def test_missing_xml_file(self, mock_artifact_path):
        v = Validator(mock_artifact_path)
        with pytest.raises(FileNotFoundError):
            v.validate(Path("nonexistent.xml"))

    @patch("saxonche.PySaxonProcessor")
    def test_saxon_validation_mock(self, mock_proc_cls, mock_artifact_path, tmp_path):
        # We assume Saxon works, but verifying the piping logic
        mock_proc = mock_proc_cls.return_value.__enter__.return_value
        mock_xslt_proc = mock_proc.new_xslt30_processor.return_value
        mock_executable = mock_xslt_proc.compile_stylesheet.return_value
        
        # Mock SVRL output
        mock_executable.transform_to_string.return_value = """
        <svrl:schematron-output xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
             <svrl:failed-assert id="BR-mock">
                <svrl:text>Mock Error</svrl:text>
             </svrl:failed-assert>
        </svrl:schematron-output>
        """
        
        v = Validator(mock_artifact_path)
        good_xml = tmp_path / "good.xml"
        good_xml.write_text("<root></root>")
        
        result = v.validate(good_xml, syntax="UBL")
        
        assert result["result"] == "FAIL"
        assert result["errors"][0]["rule_id"] == "BR-mock"
        assert result["errors"][0]["message"] == "Mock Error"
