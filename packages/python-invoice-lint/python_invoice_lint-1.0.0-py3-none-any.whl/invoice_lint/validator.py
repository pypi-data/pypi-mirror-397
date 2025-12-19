import logging
from pathlib import Path
from lxml import etree
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class ValidationError:
    def __init__(self, rule_id: str, message: str, xpath: str, severity: str = "ERROR"):
        self.rule_id = rule_id
        self.message = message
        self.xpath = xpath
        self.severity = severity

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "xpath": self.xpath,
            "message": self.message,
            # "human_fix": ... # To be implemented via mapping later
        }

class Validator:
    def __init__(self, artifact_path: Path):
        self.artifact_path = artifact_path
    
    def validate(self, xml_path: Path, syntax: str = "UBL") -> Dict[str, Any]:
        """
        Main validation entry point. 
        """
        if not xml_path.exists():
            raise FileNotFoundError(f"XML file not found: {xml_path}")

        try:
            doc = etree.parse(str(xml_path))
        except etree.XMLSyntaxError as e:
             return {
                "result": "FAIL",
                "errors": [{"rule_id": "XML_SYNTAX", "message": str(e), "severity": "FATAL", "xpath": "N/A"}],
                "warnings": []
            }

        # 1. XSD Validation (To be implemented - requires locating schema in artifact)
        # For now, we focus on Schematron as it's the core logic for EN16931 business rules

        # 2. Schematron Validation (via XSLT)
        errors = self.validate_schematron(doc, syntax)
        
        result_status = "PASS" if not errors else "FAIL"
        
        return {
            "result": result_status,
            "errors": [e.to_dict() for e in errors],
            "warnings": [] # SVRL warnings could be parsed here
        }

    def validate_schematron(self, doc: etree._ElementTree, syntax: str) -> List[ValidationError]:
        """
        Apply XSLT validation artifacts.
        """
        from saxonche import PySaxonProcessor

        pattern = f"*{syntax}*.xsl*" 
        xslt_files = list(self.artifact_path.rglob(pattern))
        if not xslt_files:
             logger.warning(f"No XSLT found for syntax {syntax} in {self.artifact_path}")
             return []

        target_xslt = next((f for f in xslt_files if 'schematron' in f.name.lower() or 'validation' in f.name.lower()), xslt_files[0])
        logger.info(f"Using XSLT: {target_xslt}")

        # Saxon implementation
        try:
            with PySaxonProcessor(license=False) as proc:
                xsltproc = proc.new_xslt30_processor()
                executable = xsltproc.compile_stylesheet(stylesheet_file=str(target_xslt))
                
                # Transform (apply XSLT to XML)
                # doc is lxml ElementTree, but Saxon needs file or string.
                # Assuming doc was parsed from self.xml_path, but validate_schematron receives doc.
                # Ideally pass file path to Saxon for efficiency.
                # We can dump doc to string or allow validate_schematron to take path.
                # Let's verify signature: validate_schematron(self, doc: etree._ElementTree, syntax: str)
                # For MVP, serialize doc to string.
                xml_string = etree.tostring(doc, encoding='unicode')
                
                # Saxon requires XdmNode for string input
                xdm_node = proc.parse_xml(xml_text=xml_string)
                svrl_string = executable.transform_to_string(xdm_node=xdm_node)
                
                if not svrl_string:
                    logger.error("Saxon returned empty result")
                    return []

                # Parse result back to lxml for processing
                svrl_doc = etree.XML(svrl_string.encode('utf-8'))
                return self._parse_svrl(svrl_doc)
                
        except Exception as e:
            logger.error(f"Saxon validation failed: {e}")
            return [ValidationError(rule_id="SAXON_ERROR", message=str(e), xpath="N/A", severity="FATAL")]

    def _parse_svrl(self, svrl_output: etree._ElementTree) -> List[ValidationError]:
        errors = []
        ns = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}
        
        failed_asserts = svrl_output.xpath('//svrl:failed-assert', namespaces=ns)
        for fa in failed_asserts:
            rule_id = fa.get('id') or fa.get('role') or 'UNKNOWN'
            location = fa.get('location') or 'UNKNOWN'
            text_node = fa.xpath('svrl:text/text()', namespaces=ns)
            message = text_node[0] if text_node else "No message"
            
            errors.append(ValidationError(
                rule_id=rule_id,
                message=message,
                xpath=location,
                severity="ERROR"
            ))
            
        return errors
