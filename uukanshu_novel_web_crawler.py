import random
from datetime import datetime
import requests
from fake_useragent import UserAgent  # Generate random user agent
from bs4 import BeautifulSoup  # Parse HTML
from opencc import OpenCC  # Simplified Chinese to Traditional Chinese conversion
import asyncio
import edge_tts  # Text-to-speech
import os
import re

# User agent object
ua = UserAgent()

# Current time
now = datetime.now()

# Random seed
seed = now.timestamp()
random.seed(seed)

# Simplified to Traditional Chinese conversion object
converter = OpenCC('s2t')

# HTTP request headers
headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": ua.random,
    "Connection": "keep-alive",
    "Host": "www.uukanshu.com",
    "Referer": "https://www.uukanshu.com/",
}

# Get page source code


def get_page(url):
    response = requests.get(url, headers=headers)
    return response.text

# Parse page data


def page_data(soup):
    page = get_page(url)
    soup = BeautifulSoup(page, 'html.parser')

    timu = converter.convert(soup.find(id="timu").text)
    content = converter.convert(soup.find('div', id='contentbox').text)

    next_link = 'https://www.uukanshu.com' + soup.find('a', id='next')['href']

    # Remove special characters
    content = re.sub(r'\[a-z\]', '', content)

    replace_list = [' ', ',', '\n', '\r', '\u3000', '“', '”',
                    '未完待續', '*', '未完待續', '.', '.', '�', 'uanu', 'UU看書']

    for i in replace_list:
        content = content.replace(i, '\r')

    data_list = content.split('\r')
    data_list = [x for x in data_list if x != '']

    return timu, next_link, data_list

# Text-to-speech and save


async def main(output, text):
    voice = "zh-CN-YunyangNeural"
    tts = edge_tts.Communicate(text, voice)
    await tts.save(output)

if __name__ == '__main__':

    text_folder = './text_file'  # Text file output folder

    url = input('Path your start uu novel url:')

    if url != '':

        copy_page = int(input('How many pages do you want to copy:'))

        if isinstance(copy_page, int):

            # Create folder if not exist
            if not os.path.exists(text_folder):
                os.makedirs(text_folder)

            # Start copying
            print(f'start copy : {now.strftime("%H:%M:%S")}')
            for i in range(copy_page):

                title, url, text = page_data(url)
                text = ''.join(text)

                if not os.path.exists(f'./audio_file/{title}.wav'):
                    asyncio.run(main(f'./audio_file/{title}.wav', text))

                print(
                    f'copy {title} done, pass : {str(datetime.now() - now).split(".")[0]}')
