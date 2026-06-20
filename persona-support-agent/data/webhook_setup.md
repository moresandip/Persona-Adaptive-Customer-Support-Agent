# Webhook Setup & Event Signatures

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
