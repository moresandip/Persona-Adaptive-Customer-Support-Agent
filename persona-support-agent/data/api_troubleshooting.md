# API Troubleshooting & Error Codes Reference

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
