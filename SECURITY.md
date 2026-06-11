# Security Policy

## Supported Versions

We actively maintain and release security updates for the following version(s):

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

Only the latest version on the `main` branch is currently supported with security updates. We recommend always using the most recent release for the latest security patches and improvements.

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Option 1: GitHub Private Vulnerability Reporting**

1. Navigate to the Security tab of this repository
2. Click "Report a vulnerability"
3. Fill out the vulnerability report form with as much detail as possible

**Option 2: Email Report**

If you prefer not to use GitHub's private vulnerability reporting, send an email to the project maintainer with the subject line "Security Vulnerability Report" containing:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes (if applicable)

### What to Include in Your Report

To help us understand and address the issue quickly, please include:

- Type of vulnerability (e.g., SQL injection, XSS, path traversal, etc.)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct path)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact assessment of the vulnerability

### Response Timeline

We aim to acknowledge vulnerability reports within **48 hours**. We will provide a more detailed response within **7 days** with:

- Confirmation of the vulnerability
- Initial assessment and severity rating
- Timeline for remediation

## Security Update Policy

Our security update process:

1. **Acknowledgment**: We confirm receipt of the vulnerability report within 48 hours
2. **Assessment**: We evaluate the severity and impact of the vulnerability
3. **Remediation**: We develop and test a fix for the vulnerability
4. **Release**: We release a security patch or update
5. **Disclosure**: We publicly disclose the vulnerability after a patch is available

## Disclosure Policy

We follow a **coordinated disclosure** process:

- We work with reporters to understand and verify the vulnerability
- We develop a fix before public disclosure
- We notify major downstream distributors when appropriate
- We publish a security advisory on GitHub when the fix is available
- We credit reporters (with permission) in the security advisory

We believe coordinated disclosure is the best approach for protecting users. We ask that reporters:

- Allow time for a fix to be developed and deployed before public disclosure
- Do not exploit the vulnerability for any purpose beyond proof-of-concept
- Handle vulnerability information responsibly

## Contact

For security-related matters not suitable for public channels, please use the private vulnerability reporting feature in GitHub Security tab or open an issue with clear indication that it contains sensitive security information.

For general questions about the project security, please open a discussion at https://github.com/VamshiKrishnaMacha/Intelligent-Road-Infrastructure-Assessment-Using-YOLO/discussions.

## Security-Related Dependencies

This project uses third-party dependencies. We monitor for vulnerabilities in these dependencies and update them as needed. If you report a vulnerability in a dependency, we will work to patch or update the affected dependency as quickly as possible.