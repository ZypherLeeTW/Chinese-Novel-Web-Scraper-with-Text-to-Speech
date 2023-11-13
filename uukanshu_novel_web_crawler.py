import random
from datetime import datetime
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from opencc import OpenCC
import asyncio
import edge_tts
import os
import re

# pip install requests
# pip install fake-useragent
# pip install beautifulsoup4
# pip install opencc-python-reimplemented

ua = UserAgent()
now = datetime.now()
seed = now.timestamp()
random.seed(seed)
converter = OpenCC('s2t')  # 簡體轉繁體

headers = headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": ua.random,  # 使用者代理
    "Connection": "keep-alive",
    "Host": "www.uukanshu.com",
    "Referer": "https://www.uukanshu.com/",
}


def get_page(url):
    response = requests.get(url, headers=headers)
    return response.text


def page_data(soup):
    page = get_page(url)
    soup = BeautifulSoup(page, 'html.parser')
    timu = converter.convert(soup.find(id="timu").text)
    content = converter.convert(soup.find('div', id='contentbox').text)
    next_link = 'https://www.uukanshu.com' + soup.find('a', id='next')['href']
    # 去除符號
    content = re.sub(r'[a-z]', '', content)
    replace_list = [' ', ',', '\n', '\r', '\u3000', '“', '”',
                    '未完待續', '*', '未完待續', '．', '.', '�', 'ｕａｎｕ', 'ＵU看書']
    for i in replace_list:
        content = content.replace(i, '\r')
        data_list = content.split('\r')
        data_list = [x for x in data_list if x != '']  # 去除空字串

    return timu, next_link, data_list


async def main(output, text):
    voice = "zh-CN-YunyangNeural"
    tts = edge_tts.Communicate(text, voice)
    await tts.save(output)


if '__main__' == __name__:
    text_folder = './text_file'  # txt output folder
    url = input('Path your start uu novel url:')

    if not url == '':
        copy_page = int(input('How many pages do you want to copy:'))

        if type(copy_page) is int:
            # create folder if not exist
            if not os.path.exists(text_folder):
                os.makedirs(text_folder)
            # start copy
            for i in range(copy_page):
                title, url, text = page_data(url)
                text = ''.join(text)
                print(f'start copy {title} : {now.strftime("%H:%M:%S")}')
                if not os.path.exists(f'./audio_file/{title}.wav'):
                    asyncio.run(main(f'./audio_file/{title}.wav', text))
                print(
                    f'copy {title} done,time cost : {str(datetime.now() - now).split(".")[0]}')
pass
