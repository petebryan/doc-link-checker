"""__init__ for Function App to call."""
import datetime
import logging
import re
import json
import requests
import os
import azure.functions as func

folders = []
pages = []


def folder_page(item):
    """Identify if path is a file or folder."""
    if item["download_url"] is None:
        folders.append(item["url"])
    else:
        pages.append(item["download_url"])


def up_check(url: str):
    """Check the response for each URL."""
    state = requests.get(url)
    if state.status_code != 200:
        return f"{url} : {state.status_code}"
    return None


def main(mytimer: func.TimerRequest, eventout: func.Out[str]) -> None:
    """ Based on a timer, check a GitHub path for URLs. If response for a URL is not 200, return the URL and the reponse code. """
    # Set up logging
    logging.info("start")
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    # Check timer
    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)

    files = []
    url_list = []
    # Compile URL regex
    pattern = re.compile(
        "<(http[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\-\.\_\~\:\/\?\#\[\]%@!$&'()*+,;=]*)>"
    )

    # Get top level documentation folder
    doc_folder = os.environ["docFolder"]
    logging.info(f'My doc_folder value:{doc_folder}')
    folder = requests.get(doc_folder)
    folder_data = json.loads(folder.text)
    logging.info(folder)

    # For each item in path identify folders and files
    for item in folder_data:
        # Catch GitHub API limits
        if "message" in folder_data:
            raise LookupError(folder_data["message"])
        folder_page(item)

    # Iterate through each folder and extract files
    while len(folders) > 0:
        for folder in folders:
            folder_dir = requests.get(folder)
            folder_dir_data = json.loads(folder_dir.text)
            for item in folder_dir_data:
                if "message" in item:
                    raise LookupError(item["message"])
                folder_page(item)
            folders.remove(folder)

    # Iterate through each file and get contents
    for page in pages:
        if "message" in page:
            raise LookupError(page["message"])
        data = requests.get(page)
        files.append(data.text)

    # Extract URLS in files
    for file in files:
        urls = pattern.findall(file)
        url_list += urls

        url_list = list(dict.fromkeys(url_list))

    # Get response code for each URL
    failed_urls = []
    for url in url_list:
        result = up_check(url)
        if result is not None:
            failed_urls.append(result)

    out = json.dumps(failed_urls)

    # If broken URLs found return them
    if len(failed_urls) > 0:
        eventout.set(out)
    else:
        eventout.set("All links OK")
