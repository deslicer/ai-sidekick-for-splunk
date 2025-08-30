# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions of AI Sidekick for Splunk:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of AI Sidekick for Splunk seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**🚨 DO NOT create public GitHub issues for security vulnerabilities.**

Instead, please report security issues privately to:

**Email**: security@deslicer.com

### What to Include

When reporting a security vulnerability, please include:

1. **Description**: A clear description of the vulnerability
2. **Impact**: Potential impact and attack scenarios
3. **Reproduction**: Step-by-step instructions to reproduce the issue
4. **Environment**:
   - Version of AI Sidekick for Splunk
   - Python version
   - Operating system
   - Deployment method (Docker, local, etc.)
5. **Evidence**: Screenshots, logs, or proof-of-concept code (if applicable)
6. **Suggested Fix**: If you have ideas for remediation

### Response Timeline

We are committed to responding to security reports promptly:

- **Initial Response**: Within 48 hours of receiving your report
- **Status Update**: Within 7 days with our assessment and planned actions
- **Resolution**: Security fixes will be prioritized and released as soon as possible

### Responsible Disclosure

We follow responsible disclosure practices:

1. **Investigation**: We will investigate and validate the reported vulnerability
2. **Fix Development**: We will develop and test a fix
3. **Coordinated Release**: We will coordinate the release of the fix with you
4. **Public Disclosure**: After the fix is released, we may publicly acknowledge the vulnerability and your contribution (with your permission)

### Security Best Practices

When using AI Sidekick for Splunk, please follow these security best practices:

#### API Keys and Credentials
- **Never commit API keys** to version control
- **Use environment variables** for sensitive configuration
- **Rotate API keys regularly**
- **Use least-privilege access** for service accounts

#### Deployment Security
- **Keep dependencies updated** to patch known vulnerabilities
- **Use HTTPS/TLS** for all communications
- **Implement proper authentication** for production deployments
- **Run with minimal privileges** (avoid root/administrator accounts)
- **Enable audit logging** for security monitoring

#### Network Security
- **Restrict network access** to necessary ports and services
- **Use firewalls** to limit exposure
- **Implement rate limiting** to prevent abuse
- **Monitor for suspicious activity**

#### Data Protection
- **Encrypt sensitive data** at rest and in transit
- **Implement proper access controls** for Splunk data
- **Follow data retention policies**
- **Sanitize logs** to prevent information disclosure

### Security Features

AI Sidekick for Splunk includes several built-in security features:

- **Input validation** for all user inputs
- **Secure session management** with Redis
- **Rate limiting** for API endpoints
- **Audit logging** for security events
- **Configurable authentication** methods
- **TLS/SSL support** for encrypted communications

### Security Updates

Security updates will be:

- **Released promptly** for supported versions
- **Documented** in release notes with CVE numbers when applicable
- **Announced** through our security advisory channels
- **Backward compatible** when possible

### Bug Bounty Program

We currently do not have a formal bug bounty program, but we greatly appreciate security researchers who help us improve the security of our project. We will:

- **Acknowledge your contribution** in our security advisories (with your permission)
- **Provide recognition** in our project documentation
- **Consider your feedback** for future security improvements

### Security Contact

For security-related questions or concerns:

- **Email**: security@deslicer.com
- **Response Time**: Within 48 hours during business days
- **Encryption**: PGP key available upon request

### Legal

We will not pursue legal action against security researchers who:

- **Report vulnerabilities responsibly** through proper channels
- **Do not access or modify data** beyond what is necessary to demonstrate the vulnerability
- **Do not disrupt our services** or harm our users
- **Follow coordinated disclosure** practices

Thank you for helping keep AI Sidekick for Splunk and our community safe!

---

*This security policy is based on industry best practices and is regularly reviewed and updated.*
