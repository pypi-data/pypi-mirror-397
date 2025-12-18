# Enable 2FA for npm Publishing

## Issue

You got this error when trying to publish:
```
npm error 403 Two-factor authentication or granular access token with bypass 2fa enabled is required to publish packages.
```

npm now **requires** two-factor authentication (2FA) for publishing packages.

---

## Solution: Enable 2FA

### Step 1: Go to npm Website

Visit: https://www.npmjs.com/settings/mariodefe/profile

Or:
1. Go to https://www.npmjs.com/
2. Click your profile (top right)
3. Select "Account" or "Profile Settings"

### Step 2: Enable Two-Factor Authentication

1. Look for **"Two-Factor Authentication"** section
2. Click **"Enable 2FA"**
3. Choose authentication method:
   - **Authenticator App** (Recommended): Google Authenticator, Authy, Microsoft Authenticator
   - **SMS**: Text messages to your phone

### Step 3: Configure 2FA

**For Authenticator App:**
1. Install an authenticator app on your phone:
   - Google Authenticator (iOS/Android)
   - Microsoft Authenticator (iOS/Android)
   - Authy (iOS/Android)
2. Scan the QR code shown on npm website
3. Enter the 6-digit code from your app
4. Save your recovery codes (important!)

**For SMS:**
1. Enter your phone number
2. Receive verification code via SMS
3. Enter the code
4. Save your recovery codes

### Step 4: Choose 2FA Level

npm offers two levels:
- **Authorization only**: 2FA required for login and profile changes
- **Authorization and writes** (Recommended for publishing): 2FA required for login + publishing

Select **"Authorization and writes"** to enable publishing.

---

## Alternative: Use Access Token

If you don't want to enable 2FA for your main account, you can create a granular access token:

### Create Granular Access Token

1. Go to https://www.npmjs.com/settings/mariodefe/tokens
2. Click **"Generate New Token"** → **"Granular Access Token"**
3. Configure token:
   - **Name**: "SAP Datasphere MCP Publishing"
   - **Expiration**: 90 days (or custom)
   - **Packages and scopes**:
     - Select: **"Read and write"**
     - Package: `@mariodefe/sap-datasphere-mcp`
4. **Important**: Check **"Bypass 2FA for publish"** (if available)
5. Click **"Generate Token"**
6. **Copy the token immediately** (you won't see it again!)

### Use Access Token

```bash
# Method 1: Set in environment
set NPM_TOKEN=npm_yourGeneratedTokenHere
npm publish --access public

# Method 2: Login with token
npm login
# When prompted, paste your token as password
```

---

## After Enabling 2FA

Once 2FA is enabled:

### Publishing with 2FA

```bash
npm publish --access public
```

You'll be prompted for:
1. Your npm password
2. Your 2FA code (from authenticator app or SMS)

Example:
```
npm notice Publishing to https://registry.npmjs.org/
This operation requires a one-time password from your authenticator.
Enter OTP: 123456
```

---

## Quick Publish Steps (After 2FA Setup)

```bash
# 1. Make sure you're in the project directory
cd c:\Users\mariodefe\mcpdatasphere

# 2. Verify you're logged in
npm whoami
# Should show: mariodefe

# 3. Publish with 2FA
npm publish --access public
# Enter your 2FA code when prompted

# 4. Verify publication
# Visit: https://www.npmjs.com/package/@mariodefe/sap-datasphere-mcp
```

---

## Troubleshooting

### "Invalid OTP"

- Make sure your phone's time is synced correctly
- OTP codes are time-sensitive
- Try regenerating a new code

### "Token expired"

- Granular access tokens expire after 90 days by default
- Create a new token and update your configuration

### "Still can't publish"

1. Log out and log back in:
   ```bash
   npm logout
   npm login
   ```

2. Clear npm cache:
   ```bash
   npm cache clean --force
   ```

3. Try publishing again:
   ```bash
   npm publish --access public
   ```

---

## Security Best Practices

1. **Save recovery codes**: Store them securely (password manager, encrypted file)
2. **Use authenticator app**: More secure than SMS
3. **Don't share tokens**: Keep access tokens private
4. **Regular token rotation**: Create new tokens every 90 days
5. **Revoke old tokens**: Remove tokens you no longer use

---

## Summary

npm requires 2FA for publishing to improve security. You have two options:

1. **Enable 2FA on your account** (Recommended)
   - More secure
   - Required for all publishing
   - Easy with authenticator app

2. **Use granular access token**
   - Per-package permissions
   - Can bypass 2FA for specific packages
   - Good for CI/CD pipelines

Choose the method that works best for you and complete the setup to publish your package!

---

## Links

- npm 2FA Setup: https://docs.npmjs.com/configuring-two-factor-authentication
- Access Tokens: https://docs.npmjs.com/creating-and-viewing-access-tokens
- Your npm Profile: https://www.npmjs.com/settings/mariodefe/profile
- Your npm Tokens: https://www.npmjs.com/settings/mariodefe/tokens
