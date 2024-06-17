import requests

# List of proxies
proxies_list = {
    "http": "socks5://frostonfire8:yVzPZiJKuK@193.5.64.184:59101"
}

# Function to check if a proxy is valid
def is_proxy_valid(proxy):
    try:
        response = requests.get('http://example.com', proxies={"http": proxy, "https": proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Filter out invalid proxies
valid_proxies = {key: value for key, value in proxies_list.items() if is_proxy_valid(value)}

print("Valid proxies:", valid_proxies)