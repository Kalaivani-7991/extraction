import re
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

output_file = './reviews.csv'
url = 'https://www.amazon.com/Garden-Life-Vegetarian-Multivitamin-Supplement/product-reviews/B0032EZOAM/ref=cm_cr_getr_d_paging_btm_prev_1?pageNumber=1&sortBy=recent&reviewerType=avp_only_reviews'

class AmazonScraper:
    def __init__(
        self,
        headless=True,
        load_images=False,
        chromedriver_path="./chromedriver.exe",
        window_size=(700, 900)
    ):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--disable-gpu")
        
        if not load_images:
            prefs = {"profile.default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-site-usage")
        
        service = Service(chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_size(*window_size)

    def perform_reload(self, url):
        self.driver.get(url)
        try:
            reload_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@onclick='window.location.reload()']"))
            )
            reload_element.click()
        except:
            print("Reload element not found or clickable.")
        time.sleep(5)  # Add a delay after reload

    def scrape_reviews(self, url):
        reviews_data = []

        self.perform_reload(url)
        current_page = 1

        while True:
            reviews_parent = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "cm_cr-review_list"))
            )

            for review in reviews_parent.find_elements(By.XPATH, ".//div[@data-hook='review']"):
                try:
                    reviewer_name = review.find_element(By.XPATH, ".//span[@class='a-profile-name']").text
                except:
                    reviewer_name = "N/A"
                try:
                    review_title = review.find_element(By.XPATH, ".//a[@data-hook='review-title']").text
                except:
                    review_title = "N/A"
                try:
                    rating = review.find_element(By.XPATH, ".//i[@data-hook='review-star-rating']").text
                except:
                    rating = "N/A"
                try:
                    date = review.find_element(By.XPATH, ".//span[@data-hook='review-date']").text
                except:
                    date = "N/A"
                try:
                    review_text = review.find_element(By.XPATH, ".//span[@data-hook='review-body']").text
                except:
                    review_text = "N/A"
                try:
                    helpful_count = review.find_element(By.XPATH, ".//span[@data-hook='helpful-vote-statement']").text
                except:
                    helpful_count = "N/A"

                review_info = {
                    "Reviewer Name": reviewer_name,
                    "Review Title": review_title,
                    "Rating": rating,
                    "Date": date,
                    "Review": review_text,
                    "Helpful": helpful_count
                }
                reviews_data.append(review_info)

            print(f"Page {current_page} Reviews data scraped.")

            # Check if the Next page button is clickable
            try:
                next_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@class='a-last']/a[contains(text(), 'Next page') or contains(text(), '>>')]"))
                )
            except Exception as e:
                print(f"No more pages available. {e}")
                break

            # Scroll down to trigger loading of more reviews
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)  # Add a short delay to ensure the page loads
            current_page += 1

            # Click the Next page button
            next_button.click()

            # Sleep for 10 seconds before scraping the next page
            time.sleep(10)

        # Save data to CSV file
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Reviewer Name", "Review Title", "Rating", "Date", "Review", "Helpful"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for review in reviews_data:
                writer.writerow(review)

        print("Reviews data saved to", output_file)
        return reviews_data

scraper = AmazonScraper()
reviews = scraper.scrape_reviews(url)
