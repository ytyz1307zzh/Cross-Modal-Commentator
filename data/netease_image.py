import requests
from bs4 import BeautifulSoup
import re
import argparse
from time import sleep
import json
import os
import goto
from goto import with_goto

@with_goto
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-save_dir', default='./imgs', help='path to save crawled images')
    opt = parser.parse_args()

    news = json.load(open('news.json', 'r', encoding='utf-8'))
    print('[INFO] JSON file loaded, containing {} pieces of news.'.format(len(news)))
    if os.path.exists('log.json'): # if some news are previously crawled, then load their ids
        exist_ids = json.load(open('log.json', 'r', encoding='utf-8'))
        print('[INFO] Previous crawled ids loaded, containing {} news'.format(len(exist_ids)))
    else:
        exist_ids = []

    requests.adapters.DEFAULT_RETRIES = 5
    sess = requests.session()
    sess.headers = {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "zh-CN,zh;q=0.8"
        }

    for news_id, news_content in news.items():

        if news_id in exist_ids: # this news has been crawled before
            continue

        img_urls = news_content['imgs'] # acquire a list of image url
        for url in img_urls: # crawl one image at one time
            label .retry
            try:
                response = sess.get(url)

                if response.status_code != 200: # if the image cannot be found
                    print('[ERROR] Cannot access image with url: ', url)
                    with open('err.txt', 'a', encoding='utf-8') as err_file: # store the error information
                        err_file.write(url+'\n')
                    continue

            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                sleep(5)
                print("That was a nice sleep, now let me continue...")
                goto .retry

            filename = url
            # process the url as filename
            filename = re.sub('http://', '', filename)
            filename = re.sub('/', '--', filename)
            filename = re.sub('\?', '~', filename)
            filename = filename + '.jpg'

            with open(opt.save_dir+'/'+filename, 'wb') as f:
                f.write(response.content)

        print(news_id) # if all related images are stored, print the id to signal the success
        exist_ids.append(news_id)
        news_cnt = len(exist_ids)
        if news_cnt % 50 == 0:
            print('-'*50)
            print('[INFO] {} pieces of news finished.'.format(news_cnt))
            print('-'*50)
            json.dump(exist_ids, open('log.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

    print('[INFO] All data finished.')

if __name__ == '__main__':
    main()

