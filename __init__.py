import datetime
import logging
import re
import json
import requests
from typing import List
import os
import azure.functions as func

folders = []
pages = []

def folder_page(item):
    if item['download_url'] is None:
        folders.append(item['url'])
    else:
        pages.append(item['download_url'])

def up_check(url):
    state = requests.get(url)
    if state.status_code != 200:
        return f"{url} : {state.status_code}"

def main(mytimer: func.TimerRequest, eventout: func.Out[str]) -> None:
    logging.info('start')
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    files = []
    url_list = []
    pattern = re.compile("<(http[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\-\.\_\~\:\/\?\#\[\]%@!$&'()*+,;=]*)>")
    
    folder = requests.get(os.environ["docFolder"])
    folder_data = json.loads(folder.text)
    logging.info(folder)
    for item in folder_data:
        if "message" in folder_data:
            raise LookupError(folder_data['message'])
        folder_page(item)
        
    while len(folders) > 0:
        for folder in folders:
            folder_dir = requests.get(folder)
            folder_dir_data = json.loads(folder_dir.text)
            for item in folder_dir_data:
                if "message" in item:
                    raise LookupError(item['message'])
                folder_page(item)
            folders.remove(folder)
            
    for page in pages:
        if "message" in page:
            raise LookupError(page['message'])
        data = requests.get(page)
        files.append(data.text)
    
    for file in files:
        urls = pattern.findall(file)
        url_list += urls
    
    url_list = list(dict.fromkeys(url_list))

    failed_urls = []
    for url in url_list:
        result = up_check(url)
        if not result is None:
            failed_urls.append(result)

    out = json.dumps(failed_urls)

    if len(failed_urls) > 0:
        eventout.set(out)
    else:
        eventout.set("All links OK")