import os
import csv
import requests
import json
import logging
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import concurrent.futures
from dataclasses import dataclass, field, fields, asdict

API_KEY = ""

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    API_KEY = config["api_key"]


## Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def scrape_search_results(keyword, location, locality, page_number, retries=3):
    formatted_keyword = keyword.replace(" ", "+")
    formatted_locality = locality.replace(" ", "+")
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={formatted_keyword}&location={formatted_locality}&original_referer=&start={page_number*10}"
    tries = 0
    success = False
    
    while tries <= retries and not success:
        try:
            response = requests.get(url)
            logger.info(f"Recieved [{response.status_code}] from: {url}")
            if response.status_code != 200:
                raise Exception(f"Failed request, Status Code {response.status_code}")
                
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            div_cards = soup.find_all("div", class_="base-search-card__info")
            for div_card in div_cards:
                company_name = div_card.find("h4", class_="base-search-card__subtitle").text
                job_title = div_card.find("h3", class_="base-search-card__title").text
                link = div_card.parent.find("a")
                job_link = link.get("href")
                location = div_card.find("span", class_="job-search-card__location").text
                
                search_data = {
                    "name": company_name,
                    "job_title": job_title,
                    "url": job_link,
                    "location": location
                }                

                print(search_data)
            logger.info(f"Successfully parsed data from: {url}")
            success = True
        
                    
        except Exception as e:
            logger.error(f"An error occurred while processing page {url}: {e}")
            logger.info(f"Retrying request for page: {url}, retries left {retries-tries}")
            tries+=1
    if not success:
        raise Exception(f"Max Retries exceeded: {retries}")




def start_scrape(keyword, pages, location, locality, retries=3):
    for page in range(pages):
        scrape_search_results(keyword, location, locality, page_number, retries=retries)


if __name__ == "__main__":

    MAX_RETRIES = 3
    MAX_THREADS = 5
    PAGES = 3
    LOCATION = "us"
    LOCALITY = "United States"

    logger.info(f"Crawl starting...")

    ## INPUT ---> List of keywords to scrape
    keyword_list = ["software engineer"]
    aggregate_files = []

    ## Job Processes
    for keyword in keyword_list:
        start_scrape(keyword, PAGES, LOCATION, LOCALITY, retries=MAX_RETRIES)
    logger.info(f"Crawl complete.")