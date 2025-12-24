# Security Policy

## Supported Versions

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| 2.13.7+ | :white_check_mark: | Full security |
| < 2.13.7 | :x: | **VULNERABLE - DO NOT USE** |

## Critical Vulnerabilities in Versions < 2.13.7

### CVE-PENDING-001: Chain Integrity Bypass (HIGH)

**Affected versions:** < 2.13.7

**Description:** The `_load_chain()` function did not validate record hashes during chain reload. An attacker with filesystem access could modify decision records without detection.

**Impact:** Complete audit trail tampering. An attacker could rewrite history.

**Fix:** Upgrade to v2.13.7 or later.

### CVE-PENDING-002: Confidence Value Injection (MEDIUM)

**Affected versions:** < 2.13.7

**Description:** The `decide()` function accepted invalid confidence values including NaN, Infinity, negative numbers, and values > 1.0.

**Impact:** Data corruption, analytics failures, potential DoS through NaN propagation.

**Fix:** Upgrade to v2.13.7 or later.

### CVE-PENDING-003: Identity Save Path Confusion (LOW)

**Affected versions:** < 2.13.6

**Description:** The `identity.save()` function created a directory instead of a file when path ended in `.json` or `.key`.

**Impact:** Functionality failure, not a direct security vulnerability.

**Fix:** Upgrade to v2.13.6 or later.

## Reporting a Vulnerability

Report security vulnerabilities to: security@stellanium.io

We will respond within 48 hours and provide a fix within 7 days for critical issues.

## Security Best Practices

1. **Always use the latest version** - `pip install --upgrade honest-chain`
2. **Use Bitcoin anchoring** - External proof that cannot be tampered
3. **Verify chains regularly** - Call `hc.verify()` on load
4. **Protect storage directory** - Restrict filesystem access to decision logs
