import requests
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
import os
import json
import time
import random

# Retry function to handle connection issues with exponential backoff
def download_with_retries(url, num, retries=3, delay=5, max_delay=30):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Check if the response is successful
        with open(f'{num}.pdf', ' b') as f:
            f.write(response.content)
        print(f"Downloaded {num}.pdf")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {num}.pdf: {e}")
        if retries > 0:
            # Exponential backoff: Randomize delay to avoid hammering the server
            delay = min(delay * 2, max_delay)  # Double the delay up to max_delay
            print(f"Retrying {num} in {delay} seconds...")
            time.sleep(delay + random.uniform(0, 3))  # Add some random variation
            return download_with_retries(url, num, retries - 1, delay, max_delay)
        else:
            print(f"Failed to download {num}.pdf after {3 - retries} retries.")
            return False

def get_documents():
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Host': 'ttab-reading-room.uspto.gov',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        'Content-Type': 'application/json',
        'Content-Length': '154',
        'Origin': 'https://ttab-reading-room.uspto.gov',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://ttab-reading-room.uspto.gov/efoia/efoia-ui/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    action_postURL = "https://ttab-reading-room.uspto.gov/ttab-efoia-api/decision/search"
    res = requests.get(action_postURL, stream=True)
    search_cookies = res.cookies
    post_data = {
        "dateRangeData": {},
        "facetData": {},
        "parameterData": {},
        "recordTotalQuantity": 25,
        "searchText": "",
        "sortDataBag": [{"issueDate": "desc"}],
        "recordStartNumber": 0
    }
    res_post = requests.post(action_postURL, data=json.dumps(post_data), cookies=search_cookies, headers=headers)
    json_response = res_post.json()['results']
    document_links = ["https://ttab-reading-room.uspto.gov/cms/rest" + i.get('documentId') for i in json_response]
    proceeding_num = [i.get('proceedingNumber') for i in json_response]
    
    return {
        'documentLinks': document_links,
        'proceedingNumber': proceeding_num
    }

def download_documents():
    document_dict = get_documents()
    document_links = document_dict['documentLinks']
    proceeding_num = document_dict['proceedingNumber']
    path = os.path.join(os.getcwd(), 'TTAB Cases')
    try:
        os.makedirs(path, exist_ok=True)  # Use os.makedirs to avoid error if directory already exists
        print(f"Successfully created the directory {path}")
    except OSError as e:
        print(f"Creation of the directory {path} failed: {e}")

    print("Downloading All Documents")

    with FuturesSession() as session:
        futures = {
            session.get(url, stream=True, timeout=30): num for url, num in zip(document_links, proceeding_num)
        }
        for future in as_completed(futures):
            response = future.result()
            num = futures[future]  # Get the proceeding number from the futures dictionary   
            # Check if the download was successful and save the file
            if response.status_code == 200:
                with open(os.path.join(path, f'{num}.pdf'), 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {num}.pdf")
            else:
                # Retry if the status code is not 200 (e.g., 500 Internal Server Error, etc.)
                print(f"Download failed for {num}.pdf, retrying...")
                download_with_retries(future.request.url, num)

# Call download_documents function to start the process
download_documents()
