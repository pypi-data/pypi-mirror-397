# invoice-lint: EN16931 CI Validation Tool

A command-line tool to validate e-invoices (UBL/CII) against EN16931 standards with pixel-perfect accuracy using official Schematron artifacts. Designed for CI/CD pipelines.

## Quick Start
```bash
# Install
pip install invoice-lint

# Validate an invoice
invoice-lint validate --artifact 1.3.15 invoice.xml
```

## Why this tool?
*   **Official Compliance**: Uses the official `Connecting Europe Facility (CEF)` validation artifacts (XSLT/Schematron) directly. No approximation.
*   **Diff Engine**: Detect strictness changes between versions before you upgrade. "What worked yesterday might fail today."
*   **CI/CD Ready**: Zero-config exit codes (0=Pass, 1=Fail), JSON output, and pip-installable.

## CI Integration (GitHub Actions)
Add this to your `.github/workflows/validate.yml`:

```yaml
steps:
  - uses: actions/checkout@v3
  - name: Validate Invoices
    uses: your-org/invoice-lint@v1
    with:
      artifact: '1.3.15'
      path: './invoices'
```

## Security Notice
> [!IMPORTANT]
> **No external data transmission.**
> This tool runs 100% locally. Validation logic (XSLT) is downloaded from GitHub to your local cache (`~/.cache/invoice-lint`) ONLY. Your invoice data never leaves your environment.

## Pricing (Advanced Features)
The basic validation is open and free.
Advanced features like **Diff Impact Analysis** (Checking regressions on your historical data) require a commercial license.

Contact `sales@example.com` for license keys and access to advanced modules.
