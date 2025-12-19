from invoice_lint.artifact_manager import ArtifactManager
from pathlib import Path
import re

manager = ArtifactManager()
# We know it downloaded 1.3.15
path = manager.get_artifact_path("1.3.15")

# Find XSLT
xml_files = list(path.rglob("*UBL*.xsl*"))
print(f"Found {len(xml_files)} XSLT files")

regex_checks = {
    "upper-case": r"upper-case\(",
    "lower-case": r"lower-case\(",
    "matches": r"matches\(",
    "replace": r"replace\(",
    "tokenize": r"tokenize\(",
    "ends-with": r"ends-with\("
}

for f in xml_files:
    if "schematron" in f.name.lower() or "validation" in f.name.lower():
        print(f"Checking {f.name}...")
        content = f.read_text()
        for func, regex in regex_checks.items():
            matches = re.findall(regex, content)
            if matches:
                 print(f"  Found {len(matches)} usages of {func}")
