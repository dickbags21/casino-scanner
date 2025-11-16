# Making This Repository Private

This guide provides instructions on how to make the `casino-scanner` repository private on GitHub.

## ⚠️ Important Note

**Repository visibility (public/private) is a GitHub platform setting that cannot be changed through code commits or configuration files.** You must have admin access to the repository to change its visibility.

## Methods to Make Repository Private

### Method 1: GitHub Web Interface (Recommended)

This is the easiest method:

1. Navigate to your repository: `https://github.com/dickbags21/casino-scanner`
2. Click on **Settings** (top right, next to About)
3. Scroll down to the **Danger Zone** section (at the bottom)
4. Click **Change repository visibility**
5. Select **Make private**
6. Confirm by typing the repository name when prompted
7. Click **I understand, change repository visibility**

### Method 2: GitHub CLI

If you have the GitHub CLI (`gh`) installed and authenticated:

```bash
# Install GitHub CLI if not already installed
# On Ubuntu/Debian:
# sudo apt install gh

# On macOS:
# brew install gh

# Authenticate with GitHub (if not already done)
gh auth login

# Make the repository private
gh repo edit dickbags21/casino-scanner --visibility private
```

### Method 3: GitHub API

Using `curl` with a GitHub Personal Access Token:

```bash
# You'll need a Personal Access Token with 'repo' scope
# Create one at: https://github.com/settings/tokens

# Set your token as an environment variable
export GITHUB_TOKEN="your_token_here"

# Make the repository private
curl -X PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/dickbags21/casino-scanner \
  -d '{"private":true}'
```

### Method 4: Using the Helper Script

Run the included helper script (requires GitHub CLI):

```bash
./make_repository_private.sh
```

## After Making the Repository Private

Once the repository is private:

### ✅ Benefits
- Only you and invited collaborators can see the code
- The repository won't appear in search results
- Sensitive data (API keys, configurations) are protected
- Better security for vulnerability research tools

### 📋 Things to Consider
- Collaborators will need to be explicitly invited
- GitHub Actions minutes may be limited (check your plan)
- Forks will be deleted when you make a public repository private
- Any public GitHub Pages will be unpublished

### 🔐 Additional Security Recommendations

After making the repository private, consider:

1. **Review commit history** for any accidentally committed secrets
   ```bash
   # Search for potential secrets in commit history
   git log -p | grep -i "api_key\|password\|secret\|token"
   ```

2. **Use `.gitignore`** to prevent committing sensitive files
   - Already included: `config/config.yaml` (contains API keys)
   - Consider adding: `.env`, `*.key`, `credentials.*`

3. **Rotate any exposed API keys**
   - Shodan API key (if previously committed)
   - Any other service credentials

4. **Use GitHub Secrets** for CI/CD workflows
   - Store API keys in Settings → Secrets and variables → Actions

5. **Enable security features**:
   - Dependabot alerts
   - Code scanning
   - Secret scanning (available for private repos with GitHub Advanced Security)

## Verification

After changing visibility, verify:

1. Try accessing the repository in an incognito/private browser window
2. Check that `https://github.com/dickbags21/casino-scanner` requires authentication
3. Visit your repository settings to confirm it shows "Private" badge

## Troubleshooting

### "You don't have permission to change visibility"
- You must be the repository owner or have admin access
- Organization repositories may require organization owner permissions

### GitHub CLI authentication issues
```bash
# Re-authenticate
gh auth logout
gh auth login
```

### API rate limits
- Unauthenticated requests: 60 per hour
- Authenticated requests: 5,000 per hour
- Use authentication for API requests

## Need Help?

If you encounter issues:
1. Check [GitHub Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
2. Verify you have the necessary permissions
3. Contact GitHub Support if needed

---

**Security Note:** This repository contains security research tools. Making it private is recommended to prevent misuse and protect any sensitive configurations.
