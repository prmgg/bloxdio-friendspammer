import aiohttp
import asyncio
import json

def read_cookies_and_api_type(file_path):
    cookies_list = []
    cookies = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    key, value = line.split('=', 1)
                    if key == "api_type":
                        cookies["api_type"] = value
                    else:
                        cookies[key] = value
                except ValueError:
                    continue

            if "api_type" in cookies and cookies:
                cookies_list.append(cookies)
                cookies = {}
    return cookies_list

def remove_account(file_path, cookies_to_remove):
    lines_to_keep = []
    skip = False

    with open(file_path, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("3PSIDMC") and line.split('=')[1] == cookies_to_remove.get("3PSIDMC"):
            skip = True
            i += 1
            while i < len(lines) and '=' in lines[i]:
                i += 1
        elif line.startswith("3PSIDMCPP") and line.split('=')[1] == cookies_to_remove.get("3PSIDMCPP"):
            skip = True
            i += 1
            while i < len(lines) and '=' in lines[i]:
                i += 1
        else:
            lines_to_keep.append(lines[i])
            i += 1

    with open(file_path, 'w') as f:
        f.writelines(lines_to_keep)

async def send_friend_request():
    cookies_list = read_cookies_and_api_type('cookie.txt')

    if not cookies_list:
        print("Error: No valid cookies found in cookie.txt")
        return

    for cookies in cookies_list:
        api_type = cookies.get("api_type")
        if not api_type or not cookies:
            print("Error: 'api_type' not found for an account")
            continue

        print(f"Cookies read from file: {cookies}")

        url = f"https://{api_type}.bloxd.io/social/send-friend-request"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "application/json",
            "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
            "Content-Type": "application/json",
            "Sec-GPC": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=0",
            "Referer": "https://bloxd.io/"
        }

        data = {
            "metricsCookies": {
                "3PAPISID": cookies.get("3PAPISID", "N/A"),
                "1PAPISID": cookies.get("1PAPISID", "N/A"),
                "3PSID": cookies.get("3PSID", "N/A"),
                "1PSID": cookies.get("1PSID", "N/A"),
                "3PSIDMC": cookies.get("3PSIDMC", "default_value"),
                "3PSIDMCPP": cookies.get("3PSIDMCPP", "default_value"),
                "3PSIDMCSP": "0j0f03K6J009m00000001j0010s07wILM91p0q000R00tsw00B000J01bW71"
            },
            "contents": {
                "requestToPlayerName": "interactive"
            }
        }

        print(f"Sending friend request for {api_type}...")
        print("Request data being sent:")
        print(json.dumps(data, indent=4))

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, cookies=cookies, json=data) as response:
                    if response.status == 401:
                        print(f"401 Unauthorized Error: Deleting account with 3PSIDMC or 3PSIDMCPP")
                        remove_account('cookie.txt', cookies)
                        print(f"Account with matching cookies has been removed from cookie.txt")
                        continue
                    response_text = await response.text()
                    print(f"Response Status Code: {response.status}")
                    print(f"Response Content: {response_text[:200]}")
        except aiohttp.ClientError as e:
            print(f"Request Error: {e}")

asyncio.run(send_friend_request())
