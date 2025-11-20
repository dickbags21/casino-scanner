# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Contact the repository owner directly via GitHub
3. Provide details about the vulnerability and steps to reproduce
4. Allow reasonable time for a fix before public disclosure

## Security Best Practices for This Repository

### Repository Privacy

This repository contains security research tools and should be kept **private** to prevent:
- Exposure of security research methodologies
- Leakage of API keys and credentials
- Public disclosure of vulnerability data
- Misuse of scanning tools

### Making the Repository Private

See [MAKE_PRIVATE.md](../MAKE_PRIVATE.md) for detailed instructions on making this repository private.

Quick methods:
1. **GitHub Web Interface**: Settings → Danger Zone → Change visibility
2. **GitHub CLI**: `gh repo edit dickbags21/casino-scanner --visibility private`
3. **Helper Script**: `./make_repository_private.sh`

### Protecting Sensitive Data

#### API Keys and Secrets

**Never commit these to the repository:**
- Shodan API keys
- Database credentials
- OAuth tokens
- SSH keys
- TLS/SSL certificates
- Service account credentials

**Best practices:**
1. Use `.env` files for local development (already in `.gitignore`)
2. Use GitHub Secrets for CI/CD workflows
3. Rotate any keys that may have been accidentally committed
4. Use environment variables for sensitive configuration

#### Configuration Files

The following files may contain sensitive data:
- `config/config.yaml` - Shodan API keys
- `.env` - Environment variables
- Any `credentials.*` or `secrets.*` files

These patterns are included in `.gitignore` to prevent accidental commits.

#### Scan Results and Data

Scan results may contain:
- Target URLs and IP addresses
- Vulnerability details
- Authentication credentials found during scans
- Sensitive business information

**Protection measures:**
- Store results locally (already in `.gitignore` as `results/`)
- Never commit raw scan outputs
- Sanitize data before sharing or reporting
- Use encryption for sensitive result archives

### Git History Security

If secrets were previously committed:

1. **Check commit history for secrets:**
   ```bash
   git log -p | grep -i "api_key\|password\|secret\|token"
   ```

2. **Remove secrets from history (if found):**
   ```bash
   # Use git-filter-repo (recommended)
   pip install git-filter-repo
   git filter-repo --path config/config.yaml --invert-paths
   
   # Or use BFG Repo-Cleaner
   # https://rtyley.github.io/bfg-repo-cleaner/
   ```

3. **Rotate compromised credentials:**
   - Generate new Shodan API key
   - Update configuration files
   - Update any dependent systems

### GitHub Security Features

Enable these features in repository settings:

#### Dependabot
- ✅ Enable Dependabot alerts
- ✅ Enable Dependabot security updates
- ✅ Enable Dependabot version updates

#### Code Scanning
- ✅ Enable CodeQL analysis
- ✅ Set up automated security scanning
- ✅ Review and fix identified vulnerabilities

#### Secret Scanning
- ✅ Enable secret scanning (available for private repos with GitHub Advanced Security)
- ✅ Enable push protection
- ✅ Review and rotate any exposed secrets

#### Branch Protection
- Require pull request reviews
- Require status checks to pass
- Restrict who can push to main branch

### Dependencies Security

#### Python Dependencies

Regularly update dependencies:
```bash
# Check for vulnerable packages
pip-audit

# Update all packages
pip install --upgrade -r requirements.txt

# Review security advisories
pip install safety
safety check
```

#### Vulnerability Scanning

The project includes:
- Playwright for browser automation
- Shodan API client
- Various security research tools

**Recommendations:**
1. Keep all dependencies updated
2. Review CVEs for used libraries
3. Use virtual environments
4. Pin versions in `requirements.txt`

### Application Security

#### Web Dashboard Security

The dashboard (port 8000) has:
- ❌ No authentication (single-user design)
- ❌ No rate limiting
- ❌ No HTTPS by default

**Recommendations for production use:**
1. Add authentication/authorization
2. Use reverse proxy with HTTPS (nginx, Caddy)
3. Implement rate limiting
4. Restrict network access (localhost only or VPN)
5. Change default ports
6. Use strong session secrets

#### Node-RED Security

Node-RED (port 1880) requires:
- Change default admin password
- Enable HTTPS
- Restrict network access
- Review flow security

See Node-RED security documentation: https://nodered.org/docs/user-guide/runtime/securing-node-red

### Network Security

#### Recommended Network Configuration

```bash
# Run dashboard on localhost only
python3 start_dashboard.py --host 127.0.0.1

# Use SSH tunneling for remote access
ssh -L 8000:localhost:8000 user@remote-host
```

#### Firewall Rules

If running on a server:
```bash
# Allow only localhost access
sudo ufw deny 8000
sudo ufw deny 1880

# Or use specific IP whitelist
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

### Docker Security

If using Docker:

1. **Don't run as root:**
   ```dockerfile
   USER node  # or specific user
   ```

2. **Use specific image tags:**
   ```dockerfile
   FROM python:3.11-slim  # not 'latest'
   ```

3. **Scan images:**
   ```bash
   docker scan casino-scanner
   ```

4. **Limit container permissions:**
   ```bash
   docker run --cap-drop=ALL --security-opt=no-new-privileges casino-scanner
   ```

### Monitoring and Logging

#### Security Event Logging

Monitor for:
- Failed authentication attempts (if implemented)
- Unusual API usage patterns
- Large data exports
- Configuration changes
- New user/collaborator additions

#### Log Management

- Store logs securely
- Rotate logs regularly
- Never log secrets or credentials
- Review logs for security events

### Incident Response

If a security incident occurs:

1. **Immediate Actions:**
   - Make repository private (if public)
   - Rotate all credentials
   - Review access logs
   - Identify scope of compromise

2. **Investigation:**
   - Check commit history
   - Review collaborator access
   - Examine network logs
   - Document findings

3. **Remediation:**
   - Remove exposed secrets
   - Patch vulnerabilities
   - Update documentation
   - Notify affected parties (if required)

4. **Prevention:**
   - Implement additional security controls
   - Update security practices
   - Train team members
   - Document lessons learned

### Compliance and Legal

#### Responsible Security Research

- Obtain proper authorization before scanning
- Follow coordinated disclosure practices
- Respect terms of service
- Comply with local laws (CFAA, GDPR, etc.)
- Document authorization and scope

#### Data Protection

- Handle personal data per GDPR/privacy laws
- Implement data retention policies
- Secure data at rest and in transit
- Provide data deletion capabilities

### Security Checklist

Before using this tool:

- [ ] Repository is private
- [ ] All secrets are in `.gitignore`
- [ ] Shodan API key is configured securely
- [ ] Git history checked for exposed secrets
- [ ] Dependencies are up to date
- [ ] Dependabot alerts enabled
- [ ] Secret scanning enabled
- [ ] Dashboard restricted to localhost
- [ ] Node-RED secured with authentication
- [ ] Proper authorization obtained for scanning
- [ ] Incident response plan documented
- [ ] Regular security reviews scheduled

### Resources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Shodan Responsible Use](https://help.shodan.io/the-basics/credit-types-explained)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

### Contact

For security concerns, contact the repository maintainer through GitHub.

---

**Last Updated**: 2025-01-16  
**Version**: 1.0
