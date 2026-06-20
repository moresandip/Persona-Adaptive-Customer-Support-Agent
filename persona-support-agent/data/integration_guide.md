# Integration Guide & Quickstart

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
curl -X GET "https://api.adsparkx.com/v1/metrics" \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json"
```

## 3. SDK Libraries
We provide official SDKs for major programming environments:
* **Python SDK**: Install via `pip install adsparkx-sdk`
* **Node.js SDK**: Install via `npm install adsparkx-sdk`
* **Go SDK**: Fetch via `go get github.com/adsparkx/adsparkx-go`
