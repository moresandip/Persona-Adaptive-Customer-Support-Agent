import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_password_reset_pdf(filepath):
    """Generates a professional password reset guide PDF using reportlab."""
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#B91C1C'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.5,
        borderPadding=5,
        spaceAfter=8
    )
    
    # Content
    story.append(Paragraph("Security & Authentication Guide: Password Recovery", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("This document outlines the standard operational procedure for resetting lost or compromised user passwords on the Adsparkx platform.", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("1. Initiating the Password Reset Flow", h2_style))
    story.append(Paragraph("To reset your password, visit the login portal at <b>https://app.adsparkx.com/login</b> and click the 'Forgot Password?' link beneath the sign-in prompt. Alternatively, you can directly access the reset page at <b>https://app.adsparkx.com/password/reset</b>.", body_style))
    story.append(Paragraph("You will be required to enter the verified email address associated with your Adsparkx profile. Our system will validate the email address and dispatch a secure reset link. For security reasons, the system will display a generic confirmation message even if the email entered does not exist in our database.", body_style))
    
    story.append(Paragraph("2. Using the Secure Password Reset Link", h2_style))
    story.append(Paragraph("Once the request is submitted, a verification email containing a unique, time-sensitive cryptographic link is dispatched. This token link has a strict validity window of <b>60 minutes</b>. If you do not click the link within 60 minutes, it will expire and you must initiate a new recovery request.", body_style))
    story.append(Paragraph("Upon clicking the link, you will be redirected to the secure page to choose a new password. Your new password must meet the following complexity parameters:", body_style))
    story.append(Paragraph("- Minimum of 10 characters in length<br/>- At least one uppercase letter (A-Z)<br/>- At least one lowercase letter (a-z)<br/>- At least one numerical digit (0-9)<br/>- At least one special character (e.g., !, @, #, $, %)", body_style))
    
    story.append(Paragraph("3. Common Issues & Troubleshooting", h2_style))
    story.append(Paragraph("<b>Issue: 'Link Expired' Error</b><br/>This occurs if you wait more than 60 minutes before clicking the link or if you click an older recovery link after requesting multiple resets. Please ensure you only use the most recent email received, and perform the reset immediately.", body_style))
    story.append(Paragraph("<b>Issue: Email Not Arriving</b><br/>If you do not receive the email within 5 minutes, check your Spam/Junk folders. Ensure your mail server is not blocking notifications from <b>no-reply@adsparkx.com</b>. If you use custom corporate email filtering (such as Mimecast or Barracuda), check with your IT administrator to release the message.", body_style))
    story.append(Paragraph("<b>Issue: Account Locked</b><br/>If you enter the incorrect password 5 consecutive times, your account will be locked for security. To unlock it, wait 30 minutes for the automatic timeout release, or follow the automated recovery link flow described above, which bypasses the lock once completed.", body_style))
    
    # Build Document
    doc.build(story)

def create_kb_documents(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. PDF
    create_password_reset_pdf(os.path.join(data_dir, "password_reset_guide.pdf"))
    print("Generated data/password_reset_guide.pdf")
    
    # 2. api_troubleshooting.md
    api_trouble = """# API Troubleshooting & Error Codes Reference

This document covers common API integration issues, error messages, and their resolution pathways on the Adsparkx platform.

## 1. 401 Unauthorized Error
This error occurs when your API requests fail authentication checks.
* **Root Cause**: Invalid, expired, or missing Bearer token.
* **Troubleshooting Steps**:
  1. Verify your API secret key is configured properly in your request headers.
  2. Ensure the header uses the exact format: `Authorization: Bearer <YOUR_API_KEY>` (verify that the word `Bearer` is capitalized and followed by a space).
  3. Ensure your API token hasn't been revoked in your dashboard settings.
  
## 2. 429 Too Many Requests (Rate Limits)
Our servers restrict excessive API usage to maintain platform reliability.
* **Root Cause**: Your application has exceeded the allocated API rate limit for your subscription tier.
* **Troubleshooting Steps**:
  1. Inspect the response headers: `X-RateLimit-Limit` (total limit per window), `X-RateLimit-Remaining` (remaining requests), and `X-RateLimit-Reset` (time in seconds until the limit resets).
  2. Implement exponential backoff in your API call loops.
  3. If your business operational needs exceed current thresholds, contact our support team to request a rate limit increase (Enterprise tier required).

## 3. 500 Internal Server Error
* **Root Cause**: The platform encountered an unexpected error on our servers.
* **Troubleshooting Steps**:
  1. Verify the payload matches the target endpoint's exact JSON schema.
  2. Include the `X-Request-ID` header value in your support ticket so our engineers can trace the execution logs.
  3. Check our system status page at status.adsparkx.com to verify if there is an ongoing outage.
"""
    with open(os.path.join(data_dir, "api_troubleshooting.md"), "w", encoding="utf-8") as f:
        f.write(api_trouble)
    print("Generated data/api_troubleshooting.md")
    
    # 3. billing_policy.txt
    billing_policy = """Adsparkx Billing, Invoice, and Subscription Policies
Effective Date: January 1, 2026

1. Billing Cycle and Invoicing
All subscription plans (Growth, Enterprise) are billed on a recurring monthly cycle starting on the date of your initial subscription. Invoices are automatically generated and sent to the billing email on file. Payment is processed automatically using your saved credit card.

2. Failed Payments and Account Suspension
If a payment attempt fails, we will retry the charge 3 times over a 7-day grace period (on days 2, 4, and 7). During this grace period, your API and workspace access remain fully functional. If payment is still outstanding after the 7th day, the account status changes to 'Suspended'. Suspended accounts have APIs deactivated and workspace access restricted.

3. Refund Policy
We offer a 14-day refund window for initial subscription plan purchases. Annual subscriptions are eligible for partial refunds within the first 14 days, subject to a 10% administrative processing fee. We do not issue refunds for monthly renewals, usage-based overages, or mid-cycle cancellations. All billing disputes must be raised via email at billing@adsparkx.com within 30 days of the charge.

4. Sales Tax and Corporate VAT
Depending on your geographic location and local tax regulations, a sales tax or VAT charge may be applied to your monthly subscription invoice. Tax-exempt organizations must upload a valid tax exemption certificate in the Billing Portal to waive future tax collections.
"""
    with open(os.path.join(data_dir, "billing_policy.txt"), "w", encoding="utf-8") as f:
        f.write(billing_policy)
    print("Generated data/billing_policy.txt")
    
    # 4. refund_policy.md
    refund_policy = """# Refund & Cancellation Policy

This document details the conditions under which Adsparkx will issue refunds or process subscription cancellations.

## 1. 14-Day Money-Back Guarantee
New users who purchase a monthly or annual Growth subscription plan are eligible for a full refund within 14 calendar days of the initial transaction.
* **Process**: To request a refund, go to **Settings > Billing > Request Refund** or email billing@adsparkx.com.
* **Exclusions**: The 14-day refund policy does not apply to:
  * Enterprise contracts with custom Service Level Agreements (SLAs).
  * Recurring monthly renewal charges.
  * Accounts suspended due to violation of our Terms of Service.

## 2. Subscription Cancellations
You can cancel your subscription at any time. When you cancel:
* Your access remains active until the end of your current billing period.
* We do not issue pro-rated refunds for unused days during the billing cycle.
* Upon cycle completion, your account is downgraded to the Free Tier.

## 3. Disputing Duplicate Charges
If you notice duplicate charges on your statement, please email billing@adsparkx.com with:
1. Your account email address.
2. The dates and amounts of the duplicate charges.
3. The last 4 digits of the card charged.
We resolve duplicate charge issues within 3 business days and issue immediate credits for billing errors.
"""
    with open(os.path.join(data_dir, "refund_policy.md"), "w", encoding="utf-8") as f:
        f.write(refund_policy)
    print("Generated data/refund_policy.md")
    
    # 5. account_security.md
    security = """# Account Security and MFA Management

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
"""
    with open(os.path.join(data_dir, "account_security.md"), "w", encoding="utf-8") as f:
        f.write(security)
    print("Generated data/account_security.md")

    # 6. payment_methods.txt
    payment = """Accepted Payment Methods and Wire Transfers
Adsparkx supports multiple payment systems for customer convenience.

1. Credit and Debit Cards
We accept major credit and debit cards: Visa, Mastercard, American Express, Discover, and JCB. Credit cards are stored securely using Stripe's PCI-compliant vaults. Card details are processed over encrypted HTTPS channels.

2. Wire Transfers and ACH (Enterprise Only)
Enterprise subscriptions with annual billing agreements ($5,000+ per year) can choose to pay via bank wire transfer or ACH.
- Payment terms are net 30 days from the invoice date.
- Wire details are printed on your enterprise invoice.
- Send remittance advice emails to billing@adsparkx.com to speed up credit application.

3. PayPal and Digital Wallets
We support PayPal for subscriptions on the Growth plan. To link PayPal:
- Go to Settings > Billing > Payment Methods.
- Click 'Add PayPal' and authorize the link in the pop-up modal.
- Apple Pay and Google Pay are supported in mobile browsers.
"""
    with open(os.path.join(data_dir, "payment_methods.txt"), "w", encoding="utf-8") as f:
        f.write(payment)
    print("Generated data/payment_methods.txt")

    # 7. integration_guide.md
    integration = """# Integration Guide & Quickstart

Get started integrating the Adsparkx API into your codebase.

## 1. Quickstart API Key Generation
To use the Adsparkx API, you must generate an API Key.
1. Log in to the Adsparkx dashboard.
2. Navigate to **Developer Settings > API Keys**.
3. Click **Create API Key**. Enter a key name and select scope parameters.
4. Copy the secret key immediately. It is only displayed once.

## 2. Making Your First Request
The API base URL is `https://api.adsparkx.com/v1`. Use the Authorization header to authenticate requests.

```bash
curl -X GET "https://api.adsparkx.com/v1/metrics" \\
  -H "Authorization: Bearer your_api_key_here" \\
  -H "Content-Type: application/json"
```

## 3. SDK Libraries
We provide official SDKs for major programming environments:
* **Python SDK**: Install via `pip install adsparkx-sdk`
* **Node.js SDK**: Install via `npm install adsparkx-sdk`
* **Go SDK**: Fetch via `go get github.com/adsparkx/adsparkx-go`
"""
    with open(os.path.join(data_dir, "integration_guide.md"), "w", encoding="utf-8") as f:
        f.write(integration)
    print("Generated data/integration_guide.md")

    # 8. data_privacy_gdpr.txt
    privacy = """Data Privacy and GDPR Compliance Guidelines
Adsparkx is committed to user data privacy and complies with GDPR, CCPA, and COPPA mandates.

1. Data Collection and Retention
We collect operational metrics, user emails, and API configurations needed to run the platform. User log content is kept for 30 days to assist troubleshooting, after which it is automatically deleted.

2. Right to be Forgotten (Data Deletion Request)
Under GDPR, users can request the deletion of all personal and account data:
- Go to Settings > Security & Privacy.
- Click 'Request Account Deletion'.
- Confirm the deletion request via the email verification link.
- Deletions are processed and completed within 14 calendar days. This action is permanent and deletes all API configurations, reports, and team workspaces.

3. Data Portability
You can export all workspace configuration settings, metrics data, and billing history:
- Navigate to Settings > Export Data.
- Select export format (CSV or JSON).
- Click 'Generate Export' and download the generated zip file.
"""
    with open(os.path.join(data_dir, "data_privacy_gdpr.txt"), "w", encoding="utf-8") as f:
        f.write(privacy)
    print("Generated data/data_privacy_gdpr.txt")

    # 9. subscription_plans.md
    sub_plans = """# Subscription Plans & Pricing Model

Adsparkx provides three pricing tiers to suit different team sizes and operational requirements.

| Tier | Price / Month | API Rate Limit | Features Included |
| --- | --- | --- | --- |
| **Free** | $0 | 10 requests / min | Basic dashboard, 1 user, 3-day data retention |
| **Growth** | $49 | 60 requests / min | Custom integrations, 5 users, 30-day retention, Email support |
| **Enterprise** | $299 | 1000 requests / min | Custom SLAs, Unlimited users, 365-day retention, 24/7 dedicated support |

## Overages and Custom Limits
* **Overage Rate**: Growth tier accounts that exceed their API limit are temporarily blocked.
* **Enterprise Customization**: Enterprise users can request custom rate limits (up to 10,000 RPM) by contacting sales@adsparkx.com.
* **Auto-upgrade option**: Enable auto-upgrade in billing settings to transition to the Growth tier when Free limits are exceeded.
"""
    with open(os.path.join(data_dir, "subscription_plans.md"), "w", encoding="utf-8") as f:
        f.write(sub_plans)
    print("Generated data/subscription_plans.md")

    # 10. enterprise_support_sla.txt
    sla = """Enterprise Support & SLA Agreement
This document outlines response timelines and support procedures for Enterprise customers.

1. Support Hours
Dedicated Enterprise support engineers are active 24/7/365. Support tickets can be submitted via the Enterprise Dashboard or by emailing enterprise-support@adsparkx.com.

2. Incident Severity Levels & Response Times
We classify issues into three severity categories, each with a strict target response time SLA:
* Priority 1 (P1) - Critical Outage: Core services are down, blocking operational workflows. Target response time: 2 Hours.
* Priority 2 (P2) - Major Impact: Key features are unavailable, but workaround exists. Target response time: 8 Hours.
* Priority 3 (P3) - Minor Issue: General queries, minor UI bugs, feature requests. Target response time: 24 Hours.

3. SLA Violation Credits
If Adsparkx fails to meet target response times on P1 incidents more than twice in a calendar month, the enterprise workspace will receive a billing credit equal to 15% of the monthly subscription fee.
"""
    with open(os.path.join(data_dir, "enterprise_support_sla.txt"), "w", encoding="utf-8") as f:
        f.write(sla)
    print("Generated data/enterprise_support_sla.txt")

    # 11. webhook_setup.md
    webhook = """# Webhook Setup & Event Signatures

Webhooks allow Adsparkx to send real-time notifications to your application servers.

## 1. Configuring Your Webhook URL
To set up a webhook receiver:
1. Log in to the Adsparkx Dashboard and go to **Developer Settings > Webhooks**.
2. Click **Add Endpoint**.
3. Input your destination URL (e.g., `https://yourdomain.com/webhooks/adsparkx`).
4. Select the event types to listen for (e.g., `invoice.paid`, `api.limit_reached`).

## 2. Signature Verification
Every webhook payload includes a signature header to verify the origin and prevent tampering:
* Header: `X-Adsparkx-Signature`
* Signature generation uses HMAC-SHA256 with your endpoint's signing secret.

Example verification code in Python:
```python
import hmac
import hashlib

def verify_signature(payload_bytes, signature, secret_key):
    computed = hmac.new(
        secret_key.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, signature)
```

## 3. Retries
If your server returns anything other than a `200 OK` status code, we retry delivery up to 5 times using exponential backoff over a 24-hour window.
"""
    with open(os.path.join(data_dir, "webhook_setup.md"), "w", encoding="utf-8") as f:
        f.write(webhook)
    print("Generated data/webhook_setup.md")

    # 12. rate_limits.txt
    rate_limits = """API Rate Limits and Request Throttling Guide
To maintain system health and fairness, Adsparkx enforces API rate limits.

1. Standard Limits
Rate limits are calculated on a sliding 60-second window:
* Free Plan: 10 requests/minute (RPM).
* Growth Plan: 60 RPM.
* Enterprise Plan: 1,000 RPM.

2. Exceeding Limits (HTTP 429)
When your application exceeds its limit, the Adsparkx API returns an HTTP 429 status code. The body contains a JSON explanation:
{
  "error": "RateLimitExceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after_seconds": 15
}

3. Strategies to Avoid Throttling
- Cache frequent API queries locally.
- Implement token-bucket or leaky-bucket queuing algorithms in your code.
- Read response headers for rate limits and adjust execution speed dynamically.
"""
    with open(os.path.join(data_dir, "rate_limits.txt"), "w", encoding="utf-8") as f:
        f.write(rate_limits)
    print("Generated data/rate_limits.txt")

    # 13. browser_caching_troubleshoot.md
    caching = """# Browser Troubleshooting & Cache Clearance Guide

If the Adsparkx interface is failing to load properly, it may be due to outdated browser cache or cookies.

## 1. Clearing Google Chrome Cache
1. Open Google Chrome.
2. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac) to open Clear Browsing Data.
3. Set Time Range to **All time**.
4. Check **Cookies and other site data** and **Cached images and files**.
5. Click **Clear data**.
6. Restart Chrome and reload the dashboard.

## 2. Clearing Mozilla Firefox Cache
1. Click the menu button (three horizontal lines) and select **Settings**.
2. Go to **Privacy & Security**.
3. In the **Cookies and Site Data** section, click **Clear Data...**.
4. Check both options and click **Clear**.

## 3. Testing with Incognito/Private Mode
To bypass cache configuration issues quickly, open a Private window:
* Chrome: `Ctrl + Shift + N` / `Cmd + Shift + N`
* Firefox: `Ctrl + Shift + P` / `Cmd + Shift + P`
If the app loads in Private mode, a full cache clearance is necessary for standard browser operation.
"""
    with open(os.path.join(data_dir, "browser_caching_troubleshoot.md"), "w", encoding="utf-8") as f:
        f.write(caching)
    print("Generated data/browser_caching_troubleshoot.md")

if __name__ == "__main__":
    create_kb_documents("data")
