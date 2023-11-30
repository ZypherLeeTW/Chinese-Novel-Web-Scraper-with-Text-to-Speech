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


def get_page(url, headers):
    response = requests.get(url, headers=headers)
    return response.text


def parse_page_data(url, converter):
    page = get_page(url, headers)
    soup = BeautifulSoup(page, 'html.parser')

    timu = converter.convert(soup.find(id="timu").text)
    content = converter.convert(soup.find('div', id='contentbox').text)

    next_link = 'https://www.uukanshu.com' + soup.find('a', id='next')['href']

    content = re.sub(r'\[a-z\]', '', content)

    replace_list = [' ', ',', '\n', '\r', '\u3000', '“', '”',
                    '未完待續', '*', '未完待續', '.', '.', '�', 'uanu', 'UU看書']

    for i in replace_list:
        content = content.replace(i, '\r')

    data_list = content.split('\r')
    data_list = [x for x in data_list if x != '']

    return timu, next_link, data_list


def generate_audio_name(title):
    if '章' in title:
        title = int(title.split('第')[1].split('章')[0])
    elif '節' in title:
        title = int(title.split('第')[1].split('節')[0])
    return title


async def text_to_speech(output, text):
    voice = "zh-CN-YunyangNeural"
    tts = edge_tts.Communicate(text, voice)
    await tts.save(output)


if __name__ == '__main__':
    ua = UserAgent()
    now = datetime.now()
    seed = now.timestamp()
    random.seed(seed)
    converter = OpenCC('s2t')

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

    def copy_pages(zip_page, copy_page):
        first_title = ''
        last_title = ''
        first_url = ''
        last_url = ''
        for i in range(copy_page//zip_page):
            total_text = ''
            for k in range(zip_page):
                try:
                    title, url, text = parse_page_data(url, converter)
                    text = ''.join(text)
                    total_text += text
                    if k == 0:
                        first_url = url
                        first_title = title
                    last_url = url
                    last_title = title
                except TypeError:
                    print('網址錯誤')
                    break

            now = datetime.now()
            try:
                first_title = generate_audio_name(first_title)
                last_title = generate_audio_name(last_title)
                with open('./audio_file/url.txt', 'w', encoding='utf-8') as file:
                    file.write(
                        f'first page:{first_url}\n last page:{last_url}')

                if not os.path.exists(f'./audio_file/第{first_title}節_第{last_title}節.wav'):
                    asyncio.run(text_to_speech(
                        f'./audio_file/第{first_title}節_第{last_title}節.wav', total_text))

                print(
                    f'copy 第{first_title}節_第{last_title}節 done, pass : {str(datetime.now() - now).split(".")[0]}')
            except IndexError:
                print('標題格式錯誤')

    def copy_single_page(copy_page):
        for i in range(copy_page):
            title, url, text = parse_page_data(url, converter)
            text = ''.join(text)
            now = datetime.now()

            if not os.path.exists(f'./audio_file/{title}.wav'):
                asyncio.run(text_to_speech(f'./audio_file/{title}.wav', text))

            print(
                f'copy {title} done, pass : {str(datetime.now() - now).split(".")[0]}')
            with open('./audio_file/Last_url.txt', 'w', encoding='utf-8') as file:
                file.write(url)

    def copy_text_files(copy_page):
        text_folder = './text_file'
        if not os.path.exists(text_folder):
            os.makedirs(text_folder)

        print(f'start copy : {now.strftime("%H:%M:%S")}')

        if zip_file == 'y':
            zip_page = int(input('How many pages do you want to zip:'))
            if isinstance(copy_page, int):
                copy_pages(zip_page, copy_page)
        else:
            if isinstance(copy_page, int):
                copy_single_page(copy_page)

    url = input('Path your start uu novel url:')
    if url != '':
        copy_page = int(input('How many pages do you want to copy:'))
        zip_file = input('Do you want to zip the text file? (y/n):')

        copy_text_files(copy_page)
