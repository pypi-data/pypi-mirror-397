import click
import sys
import json
from pathlib import Path
from lxml import etree
from invoice_lint.artifact_manager import ArtifactManager
from invoice_lint.validator import Validator

@click.group()
def main():
    """EN16931 Invoice Validation Tool"""
    pass

@main.command()
@click.option('--standard', default='EN16931', help='Standard to validate against')
@click.option('--syntax', default='UBL', help='Syntax (UBL or CII)')
@click.option('--artifact', required=True, help='Validation artifact version (e.g. 1.3.15)')
@click.argument('path', type=click.Path(exists=True))
def validate(standard, syntax, artifact, path):
    """Validate an invoice XML file or directory of files."""
    manager = ArtifactManager()
    try:
        artifact_path = manager.get_artifact_path(artifact)
    except Exception as e:
        click.echo(json.dumps({"result": "FAIL", "errors": [{"message": f"Failed to load artifact: {str(e)}", "severity": "FATAL"}]}), err=True)
        sys.exit(1)

    validator = Validator(artifact_path)
    
    files_to_validate = []
    p = Path(path)
    if p.is_dir():
        files_to_validate = list(p.glob('**/*.xml'))
    else:
        files_to_validate = [p]

    if not files_to_validate:
        click.echo(json.dumps({"result": "PASS", "message": "No XML files found.", "errors": []}, indent=2))
        sys.exit(0)

    overall_failure = False
    results = []

    for file_path in files_to_validate:
        res = validator.validate(file_path, syntax=syntax)
        res["file"] = str(file_path)
        res["artifact"] = validator_artifact_name(standard, artifact)
        res["syntax"] = syntax
        results.append(res)
        if res["result"] != "PASS":
            overall_failure = True

    # Output list of results or single result? 
    # Current requirement mostly shows single output format, but for directory scanning, list is appropriate.
    # If single file, return single object. If multiple, return list?
    # Or always return list/wrapper.
    # CLI tools often print JSON per line or a ref to a summary.
    # Requirement 4 System Config -> Report Formatter.
    # Requirement 5.1 Output (JSON). It shows a single object.
    
    # If input was a single file, output single object.
    if len(files_to_validate) == 1 and not p.is_dir():
        click.echo(json.dumps(results[0], indent=2))
    else:
         click.echo(json.dumps(results, indent=2))

    if overall_failure:
        sys.exit(1)

def validator_artifact_name(standard, version):
    return f"{standard}-{version}"

@main.command()
@click.option('--from', 'from_version', required=True, help='Base version')
@click.option('--to', 'to_version', required=True, help='Target version')
@click.option('--syntax', default='UBL', help='Syntax (UBL or CII)')
@click.argument('directory', required=False, type=click.Path(exists=True)) # Directory argument is optional for MVP diff
def diff(from_version, to_version, syntax, directory):
    """Compare validation artifacts."""
    manager = ArtifactManager()
    
    try:
        path_from = manager.get_artifact_path(from_version)
        path_to = manager.get_artifact_path(to_version)
    except Exception as e:
        click.echo(json.dumps({"error": f"Failed to download artifacts: {str(e)}"}), err=True)
        sys.exit(1)

    # Extract rules
    rules_from = extract_rules(path_from, syntax)
    rules_to = extract_rules(path_to, syntax)

    added = rules_to - rules_from
    removed = rules_from - rules_to
    modified = [] # Difficult to detect without deep parsing, omit for MVP or assume ID match = same rule

    impact_analysis = {
        "files_analyzed": 0,
        "regressions": []
    }
    
    if directory:
        p = Path(directory)
        files = list(p.glob('**/*.xml')) if p.is_dir() else [p]
        impact_analysis["files_analyzed"] = len(files)
        
        if files:
            validator_from = Validator(path_from)
            validator_to = Validator(path_to)
            
            for f in files:
                # Run validation
                res_from = validator_from.validate(f, syntax=syntax)
                res_to = validator_to.validate(f, syntax=syntax)
                
                # Extract rule IDs that failed
                fails_from = set(e['rule_id'] for e in res_from.get('errors', []))
                fails_to = set(e['rule_id'] for e in res_to.get('errors', []))
                
                # Regressions: Passed before (or didn't have this error) -> Failed now
                # i.e. New errors in 'to' that weren't in 'from'
                new_error_ids = fails_to - fails_from
                
                if new_error_ids:
                    # Retrieve full error details for the new errors
                    detailed_new_errors = [
                        err for err in res_to.get('errors', []) 
                        if err['rule_id'] in new_error_ids
                    ]
                    
                    impact_analysis["regressions"].append({
                        "file": str(f),
                        "new_errors": detailed_new_errors
                    })

    output = {
        "from": from_version,
        "to": to_version,
        "rule_changes": {
            "added": list(added),
            "removed": list(removed),
        },
        "impact_analysis": impact_analysis
    }
    
    click.echo(json.dumps(output, indent=2))

def extract_rules(artifact_path: Path, syntax: str) -> set:
    """
    Parse .sch files to extract rule IDs.
    """
    rules = set()
    # Find .sch files
    pattern = f"*{syntax}*.sch*"
    sch_files = list(artifact_path.rglob(pattern))
    
    # If no .sch found, maybe only XSLT is available? 
    # If only XSLT, extracting rule IDs is harder (inside xsl:template or SVRL generation logic).
    # Let's try to find SCH first.
    
    for sch_path in sch_files:
        try:
            doc = etree.parse(str(sch_path))
            ns = {'sch': 'http://purl.oclc.org/dsdl/schematron'}
            # Rule IDs are often on assert or report elements as 'id' or 'flag' or parent 'rule' context
            # EN16931 rules usually have 'id' on assert/report or match specific patterns.
            # Looking for asserts with IDs.
            asserts = doc.xpath('//sch:assert/@id', namespaces=ns)
            reports = doc.xpath('//sch:report/@id', namespaces=ns)
            rules.update(asserts)
            rules.update(reports)
        except Exception:
            continue
            
    return rules

if __name__ == '__main__':
    main()
