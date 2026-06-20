# Account Security and MFA Management

Adsparkx implements enterprise-grade security protocols to protect workspace data.

## 1. Enabling Multi-Factor Authentication (MFA)
We strongly recommend enabling MFA to prevent unauthorized access.
* **Steps to enable**:
  1. Navigate to **Profile Settings > Security**.
  2. Toggle **Multi-Factor Authentication** to ON.
  3. Scan the displayed QR code with your authenticator app (e.g., Google Authenticator, Duo, or Authy).
  4. Enter the 6-digit confirmation code displayed in your app.
  5. Download and save the emergency recovery codes.

## 2. Managing Active Sessions
If you suspect unauthorized access or have left your account logged in on a public computer, you can terminate sessions:
* Go to **Profile Settings > Security > Active Sessions**.
* Review the active sessions list (displaying device, IP address, and location).
* Click **Log Out of All Other Sessions** to terminate all logins except your current session.

## 3. Response to Compromised Account
If you believe your credentials have been stolen:
1. Immediately request a password reset using the forgot password page.
2. Terminate all active sessions under security settings.
3. Revoke all existing API keys and generate new ones.
4. Contact security@adsparkx.com if you detect data loss or unauthorized configurations.
