import asyncio
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
import httpx

options = Options()
options.add_argument("--headless")
options.set_preference("intl.accept_languages", "ja,en-US;q=0.7,en;q=0.3")

def create_driver():
    service = Service("") #enter pass
    return webdriver.Firefox(service=service, options=options)

async def send_request(secure_3psidmc):
    metric_url = "https://bloxd.io/index/metrics/cookies"
    social_base_url = "https://social{social_id}.bloxd.io/social/get-social-information"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "application/json",
        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/json",
        "Sec-GPC": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "Cookie": f"___Secure-3PSIDMC={secure_3psidmc}"
    }

    metric_body = {
        "metricsCookies": {
            "1PAPISID": "N/A",
            "1PSID": "N/A",
            "3PAPISID": "N/A",
            "3PSID": "N/A",
            "1PSID": "N/A",
            "3PSIDMC": secure_3psidmc,
            "3PSIDMCPP": "N/A",
            "3PSIDMCSP": "0j0f03K6J009m00010001j0010s07wILM91p0q000R00tsw00B000J01bW71"
        }
    }

    retries = 3
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                metric_response = await client.post(metric_url, headers=headers, json=metric_body)
                if metric_response.status_code == 200:
                    metric_data = metric_response.json()
                    metric_3psidmcpp = metric_data.get("3PSIDMCPP", "N/A")
                    for social_id in range(1, 15):
                        social_url = social_base_url.format(social_id=social_id)
                        social_body = {
                            "metricsCookies": {
                                "1PAPISID": "N/A",
                                "1PSID": "N/A",
                                "3PAPISID": "N/A",
                                "3PSID": "N/A",
                                "3PSIDMC": secure_3psidmc,
                                "3PSIDMCPP": metric_3psidmcpp,
                                "3PSIDMCSP": "0j0f03K6J009m00010001j0010s07wILM91p0q000R00tsw00B000J01bW71"
                            }
                        }
                        async with httpx.AsyncClient(timeout=30) as client:
                            social_response = await client.post(social_url, headers=headers, json=social_body)
                            if social_response.status_code == 200:
                                with open("cookie.txt", "a") as file:
                                    file.write(f"3PSIDMC={secure_3psidmc}\n")
                                    file.write(f"3PSIDMCPP={metric_3psidmcpp}\n")
                                    file.write(f"api_type=social{social_id}\n\n")
                                print(f"Valid social API found: social{social_id}")
                                return
                            else:
                                print(f"Invalid social{social_id}: Status Code: {social_response.status_code}")
                else:
                    print(f"Metric API failed: Status Code: {metric_response.status_code}")
        except (httpx.ConnectTimeout, httpx.RequestError) as e:
            if attempt < retries - 1:
                print(f"Request failed, retrying in 30 seconds... ({attempt + 1}/{retries})")
                await asyncio.sleep(30)
            else:
                print("All retries failed.")
                break

async def process_account(semaphore):
    async with semaphore:  
        driver = create_driver()
        try:
            driver.get("https://bloxd.io/")
            time.sleep(5)

            cookies = driver.get_cookies()
            secure_3psidmc = next((cookie["value"] for cookie in cookies if cookie["name"] == "___Secure-3PSIDMC"), None)

            if secure_3psidmc:
                await send_request(secure_3psidmc)
            else:
                print("___Secure-3PSIDMC cookie not found.")
        except TimeoutException:
            print("Timeout error occurred, reopening session...")
            driver.quit()  
            driver = create_driver()  
            await process_account(semaphore)  
        finally:
            driver.quit()

async def main():
    semaphore = asyncio.Semaphore(2)  
    tasks = [process_account(semaphore) for _ in range(100)]  
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
