# Code Quality Check

## Overview
Run all quality checks including linting, formatting, code review, security scanning, and security audit to ensure codebase quality and security.

## Steps
1. **Code Formatting & Linting**
   - Run Ruff formatting (auto-fixed)
   - Run Ruff linting with safe auto-fixes only
   - Check for code style issues

2. **Code Quality Analysis**
   - Run MyPy type checking
   - Check code complexity and maintainability
   - Validate import organization

3. **Security Scanning**
   - Run security vulnerability scanning
   - Check for hardcoded secrets
   - Validate input sanitization
   - Run dependency security audit

4. **Code Review Checklist**
   - Functionality verification
   - Code quality assessment
   - Security review
   - Performance considerations

5. **Security Audit**
   - Comprehensive security review
   - Dependency vulnerability assessment
   - Infrastructure security audit
   - Authentication/authorization review

## Quality Gates
- [ ] All Ruff checks pass (formatting & linting)
- [ ] MyPy type checking passes
- [ ] No security vulnerabilities found
- [ ] No hardcoded secrets detected
- [ ] All dependencies compatible and secure
- [ ] Code review criteria met
- [ ] Security audit completed successfully
