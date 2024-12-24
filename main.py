import httpx
import asyncio
import json

def read_cookies_and_api_type(file_path):
    cookies_list = []
    api_type = None
    cookies = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  
                try:
                    key, value = line.split('=', 1)
                    if key == "api_type":
                        api_type = value
                    else:
                        cookies[key] = value
                except ValueError:
                    continue  

            if api_type and cookies:
                cookies_list.append((cookies, api_type))
                cookies = {}
                api_type = None 
    return cookies_list

async def send_friend_request():
    cookies_list = read_cookies_and_api_type('cookie.txt')

    if not cookies_list:
        print("Error: No valid cookies found in cookie.txt")
        return

    for cookies, api_type in cookies_list:
        if not api_type:
            print("Error: 'api_type' not found for an account")
            continue

        print(f"Using API Type: {api_type}")
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
                "requestToPlayerName": "" #send req username
            }
        }

        print(f"Sending friend request for {api_type}...")
        print("Request data being sent:")
        print(json.dumps(data, indent=4))

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, cookies=cookies, json=data)
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Content: {response.text[:200]}")
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
        except httpx.ConnectError as e:
            print(f"Connection Error: {e}")

asyncio.run(send_friend_request())
