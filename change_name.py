import aiohttp
import asyncio
import random
import string

def read_cookies(file_path):
    cookies_list = []
    current_cookie = {}

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):  
                continue
            if '=' in line:  
                key, value = line.split('=', 1)
                current_cookie[key] = value

            if "3PSIDMC" in current_cookie and "3PSIDMCPP" in current_cookie:
                cookies_list.append(current_cookie)
                current_cookie = {}  

    return cookies_list

def generate_random_string():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=2))

async def send_request(cookie_3psidmc, cookie_3psidmcpp):
    url = "https://bloxd.io/name/update"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "application/json",
        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/json",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0"
    }
    body = {
        "metricsCookies": {
            "1PAPISID": "N/A",
            "1PSID": "N/A",
            "3PAPISID": "N/A",
            "3PSID": "N/A",
            "3PSIDMC": cookie_3psidmc,
            "3PSIDMCPP": cookie_3psidmcpp,
            "3PSIDMCSP": "0j0f03K6J009m00000001j0010s07wILM91p0q000R00tsw00B000J01bW71"
        },
        "contents": {
            "name": f"{generate_random_string()}_Discord_x4nVvXed2c"
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body, headers=headers) as response:
            if response.status == 200:
                print(f"Request successful for 3PSIDMC={cookie_3psidmc[:10]}...")
            else:
                print(f"Request failed with status {response.status} for 3PSIDMC={cookie_3psidmc[:10]}...")

async def main():
    cookies_list = read_cookies('cookie.txt')

    if cookies_list:
        tasks = []
        for cookies in cookies_list:
            if "3PSIDMC" in cookies and "3PSIDMCPP" in cookies:
                tasks.append(send_request(cookies["3PSIDMC"], cookies["3PSIDMCPP"]))
            else:
                print("Required cookies not found in cookie.txt")
        if tasks:
            await asyncio.gather(*tasks) 
    else:
        print("No cookies found in cookie.txt")

asyncio.run(main())
