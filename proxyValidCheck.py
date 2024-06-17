import requests

# List of proxies
proxies_list = {
    "http": "http://frostonfire8:yVzPZiJKuK@45.198.30.203:59100",
    "https": "http://frostonfire8:yVzPZiJKuK@45.198.30.203:59100"
}

# Function to check if a proxy is valid
def is_proxy_valid(proxy):
    try:
        response = requests.get('http://google.com', proxies={"http": proxy, "https": proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Filter out invalid proxies
valid_proxies = {key: value for key, value in proxies_list.items() if is_proxy_valid(value)}

print("Valid proxies:", valid_proxies)