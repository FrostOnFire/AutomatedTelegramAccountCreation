import requests

# List of proxies
proxies_list = [
    "212.83.149.33:9300"
]

# Function to check if a proxy is valid
def is_proxy_valid(proxy):
    try:
        response = requests.get('http://example.com', proxies={"http": proxy, "https": proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Filter out invalid proxies
valid_proxies = [proxy for proxy in proxies_list if is_proxy_valid(proxy)]

print("Valid proxies:", valid_proxies)