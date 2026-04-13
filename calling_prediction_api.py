import requests
import json

# ── Fill these from your AI Core Service Key ──────────────────
CLIENT_ID       = "sb-524de71c-6fdc-42f9-9ca3-1aa049f9521f!b37640|xsuaa_std!b15301"
CLIENT_SECRET   = "56e3a705-fe31-4cd8-adab-b9b49790abbe$VkGaPU4HAATczI9yH00PmPRSFS4QU-dJCJw9XzuED8o="
AUTH_URL        = "https://fin-analytical-svc-rnd.authentication.ap11.hana.ondemand.com"
DEPLOYMENT_URL  = "https://api.ai.prod-ap11.ap-southeast-1.aws.ml.hana.ondemand.com/v2/inference/deployments/<YOUR_PREDICTION_DEPLOYMENT_ID>"
RESOURCE_GROUP  = "default"
# ─────────────────────────────────────────────────────────────


def get_token():
    response = requests.post(
        url=f"{AUTH_URL}/oauth/token",
        data={
            "grant_type"   : "client_credentials",
            "client_id"    : CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_headers(token):
    return {
        "Authorization"    : f"Bearer {token}",
        "AI-Resource-Group": RESOURCE_GROUP,
        "Content-Type"     : "application/json"
    }


# Step 1: Health check
def call_health(token):
    response = requests.get(
        url=f"{DEPLOYMENT_URL}/v1/health",
        headers=get_headers(token)
    )
    print(f"Health Status Code : {response.status_code}")
    print(f"Health Response    : {response.text}")
    return response.json()


# Step 2: Reload models from S3
def call_reload_models(token):
    response = requests.post(
        url=f"{DEPLOYMENT_URL}/v1/reload-models",
        headers=get_headers(token)
    )
    print(f"Reload Status Code : {response.status_code}")
    print(f"Reload Response    : {response.text}")
    return response.json()


# Step 3: Run prediction pipeline
def call_process(token):
    body = {
        "market": "Hong Kong"
    }
    response = requests.post(
        url=f"{DEPLOYMENT_URL}/v1/process",
        headers=get_headers(token),
        json=body,
        timeout=300          # pipeline can take time
    )
    print(f"Process Status Code : {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Status             : {result.get('status')}")
        print(f"Rows Processed     : {result.get('rows_processed')}")
        print(f"Execution Time     : {result.get('execution_time_seconds')}s")
        print(f"Message            : {result.get('message')}")
    else:
        print(f"Process Response   : {response.text}")
    return response.json()


# Step 4: Get config (optional check)
def call_get_config(token, market="Hong Kong"):
    response = requests.get(
        url=f"{DEPLOYMENT_URL}/v1/getConfig",
        headers=get_headers(token),
        params={"market": market}
    )
    print(f"Config Status Code : {response.status_code}")
    result = response.json()
    data = result.get("data", [])
    print(f"Config rows returned: {len(data)}")
    for row in data:
        print(f"  {row}")
    return result


# Main
if __name__ == "__main__":
    print("Getting token...")
    token = get_token()
    print("Token retrieved ✅\n")

    print("1. Calling Health API...")
    call_health(token)

    print("\n2. Reloading Models from S3...")
    call_reload_models(token)

    print("\n3. Calling Process (Prediction) API...")
    call_process(token)

    print("\n4. Calling Get Config API...")
    call_get_config(token, market="Hong Kong")
