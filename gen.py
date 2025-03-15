import asyncio
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import httpx
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

options = Options()
options.add_argument("--headless")
options.set_preference("intl.accept_languages", "ja,en-US;q=0.7,en;q=0.3")

async def init_driver():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: webdriver.Firefox(service=Service("C:\\geckodriver\\geckodriver.exe"), options=options))

async def fetch_retry(client, url, headers, data, retries=3):
    for attempt in range(retries):
        try:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
        except httpx.RequestError as e:
            logging.warning(f"Request error: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(5)
            else:
                raise
    return None

async def send_request(cookie_val, client):
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
        "Cookie": f"___Secure-3PSIDMC={cookie_val}"
    }

    metric_body = {
        "metricsCookies": {
            "1PAPISID": "N/A",
            "1PSID": "N/A",
            "3PAPISID": "N/A",
            "3PSID": "N/A",
            "3PSIDMC": cookie_val,
            "3PSIDMCPP": "N/A",
            "3PSIDMCSP": "0j0f03K6J009m11000001j0010s07wILM91p0q000R00tsw00B000J00bW71"
        }
    }

    metric_data = await fetch_retry(client, metric_url, headers, metric_body)
    if metric_data:
        metric_3psidmcpp = metric_data.get("3PSIDMCPP", "N/A")
        for social_id in range(1, 15):
            social_url = social_base_url.format(social_id=social_id)
            social_body = {
                "metricsCookies": {
                    "1PAPISID": "N/A",
                    "1PSID": "N/A",
                    "3PAPISID": "N/A",
                    "3PSID": "N/A",
                    "3PSIDMC": cookie_val,
                    "3PSIDMCPP": metric_3psidmcpp,
                    "3PSIDMCSP": "0j0f03K6J009m11000001j0010s07wILM91p0q000R00tsw00B000J00bW71"
                }
            }
            social_response = await fetch_retry(client, social_url, headers, social_body)
            if social_response:
                with open("cookie.txt", "a") as file:
                    file.write(f"3PSIDMC={cookie_val}\n")
                    file.write(f"3PSIDMCPP={metric_3psidmcpp}\n")
                    file.write(f"api_type=social{social_id}\n\n")
                logging.info(f"Valid social API: social{social_id}")
                return
            else:
                logging.info(f"Invalid social{social_id}: No response.")

async def process(semaphore, client, driver_pool):
    async with semaphore:
        driver = await driver_pool.acquire()
        try:
            driver.get("https://bloxd.io/")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            cookies = driver.get_cookies()
            secure_3psidmc = next((cookie["value"] for cookie in cookies if cookie["name"] == "___Secure-3PSIDMC"), None)

            if secure_3psidmc:
                await send_request(secure_3psidmc, client)
            else:
                logging.warning("Cookie not found.")
        except TimeoutException:
            logging.error("Timeout. Skipping...")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
            driver_pool.release(driver)

class DriverPool:
    def __init__(self, size):
        self.pool = asyncio.Queue(maxsize=size)
        self.size = size

    async def init_drivers(self):
        for _ in range(self.size):
            driver = await init_driver()
            await self.pool.put(driver)

    async def acquire(self):
        return await self.pool.get()

    def release(self, driver):
        self.pool.put_nowait(driver)

async def main():
    semaphore = asyncio.Semaphore(10)
    driver_pool = DriverPool(size=3)
    await driver_pool.init_drivers()
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [process(semaphore, client, driver_pool) for _ in range(100)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())