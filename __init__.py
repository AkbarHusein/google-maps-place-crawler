from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time
import json


class GoogleMapsCrawler:
    """
    A class to scrape cafe details (names, links, and addresses) from Google Maps
    """

    def __init__(self, output_dir_path: str = "output"):
        """
        Initializes the crawler with options and output directory for saving results.
        """
        self.ensure_directory_exists(output_dir_path)
        self.output_file = os.path.join(output_dir_path, "cafes.json")
        self.url = "https://www.google.com/maps/@5.1918507,97.0299829,12z?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"

        # Set up Chrome options for the webdriver
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")

        # Initialize Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

        # Initialize list to store scraped data
        self.data = []

    def ensure_directory_exists(self, directory: str):
        """
        Ensure the specified directory exists, create it if it doesn't.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_to_json(self):
        """
        Save the scraped data to a JSON file.
        """
        try:
            with open(self.output_file, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
            print(f"Data successfully saved to {self.output_file}")
        except Exception as e:
            print(f"Failed to save data: {e}")

    def wait_for_manual_scrolling(self, container, timeout=10, check_interval=1):
        """
        Wait until manual scrolling stops by monitoring the container's scroll height.
        """
        last_height = self.driver.execute_script("return arguments[0].scrollHeight;", container)
        start_time = time.time()

        while True:
            time.sleep(check_interval)
            new_height = self.driver.execute_script("return arguments[0].scrollHeight;", container)

            # If height doesn't change for the timeout duration, assume scrolling stopped
            if new_height == last_height:
                if time.time() - start_time >= timeout:
                    print("Scrolling has stopped.")
                    break
            else:
                last_height = new_height
                start_time = time.time()

    def search_cafes(self, keyword: str):
        """
        Search for cafes on Google Maps by a given keyword and extract links.
        """
        query = keyword.replace(" ", "+")
        search_url = f"https://www.google.com/maps/search/{query}/@5.1921819,97.0296394,12z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"

        try:
            self.driver.get(search_url)

            # Find the containers with the results
            containers = self.driver.find_elements(By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd")
            print(f"Found {len(containers)} result containers.")

            for idx, container in enumerate(containers):
                print(f"Waiting for manual scrolling in container {idx}...")
                self.wait_for_manual_scrolling(container, timeout=5)

                # Extract cafe links from the current container
                cafe_elements = container.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
                
                for element in cafe_elements:
                    name = element.get_attribute("aria-label")
                    link = element.get_attribute("href")
                    self.data.append({"name": name, "link": link})

        except Exception as e:
            print(f"Error occurred during search: {e}")
        finally:
            print('Search complete.')

    def extract_cafe_details(self):
        """
        For each cafe, extract additional details such as the address.
        """
        for cafe in self.data:
            self.driver.get(cafe["link"])
            print(f"Processing cafe: {cafe['name']} - {cafe['link']}")
            time.sleep(2)

            try:
                # Wait for the address element to become available
                address_elements = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".Io6YTe.fontBodyMedium.kR99db.fdkmkc"))
                )
                if address_elements:
                    cafe["address"] = address_elements[0].text
                    print(f"Address: {cafe['address']}")
                else:
                    cafe["address"] = None
            except Exception as e:
                cafe["address"] = None
                print(f"Failed to retrieve address: {e}")

        # Save all data after processing
        self.save_to_json()
        print("All data has been saved. Happy Hacking dudeee!")

if __name__ == "__main__":
    crawler = GoogleMapsCrawler()
    crawler.search_cafes("Cafe lhokseumawe") # Change this to your desired keyword dudee!
    crawler.extract_cafe_details()
