import requests

# List of proxies
proxies_list = [
    "http://103.147.73.130:3131",
    "http://103.140.34.59:8080",
    "http://103.132.54.41:8182",
    "http://202.153.233.228:8080",
    "http://202.152.24.50:8080",
    "http://118.97.164.19:8080",
    "http://103.169.130.20:8080",
    "http://147.139.140.74:443",
    "http://103.108.156.38:8080",
    "http://103.110.34.43:8081",
    "http://103.172.35.13:8080",
    "http://202.154.18.10:8080",
    "http://103.130.82.46:8080",
    "http://203.128.73.122:8910",
    "http://117.54.114.102:80",
    "http://116.254.118.162:8080",
    "http://150.107.136.205:39843",
    "http://101.255.140.1:8090",
    "http://101.255.17.6:8033",
    "http://103.242.104.182:8080",
    "http://103.153.134.22:8080",
    "http://103.177.177.249:8080",
    "http://103.162.54.117:8080",
    "http://103.131.18.194:8080",
    "http://58.147.189.222:3128",
    "http://202.180.20.1:55443",
    "http://114.141.51.51:8080",
    "http://103.153.246.142:8181",
    "http://36.88.22.211:8080",
    "http://192.145.228.209:8081",
    "http://103.83.178.46:8181",
    "http://117.54.114.35:80",
    "http://61.8.70.114:2023",
    "http://103.154.118.154:17378",
    "http://103.101.193.78:1111"
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