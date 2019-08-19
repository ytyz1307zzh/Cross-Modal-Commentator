import requests
from bs4 import BeautifulSoup
import re
import json
import os
from time import sleep
import traceback
import argparse
from random import randint

def main():

    ip_list = ['183.47.40.35:8088',
               '113.54.218.133:1080',
               '222.221.11.119:3128',
               '221.7.255.167:8080',
               '175.102.3.98:8089',
               '202.204.121.126:80']
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

    parser = argparse.ArgumentParser()
    parser.add_argument('-news_id', type=int)
    opt = parser.parse_args()
    if os.path.exists('news.json'):
        scratch_result = json.load(open('news.json', 'r', encoding='utf-8'))
        with open('log.txt', 'r', encoding='utf-8') as log_file:
            news_id = int(log_file.readline().strip()) - 1
        print('[INFO] Load json file from news.json')
        print('[INFO] Starting crawling from news #', news_id)
    else:
        scratch_result = {}
        news_id = opt.news_id

    news_cnt = len(scratch_result)

    while True:

        if str(news_id) in scratch_result:
            news_id -= 1
            continue

        # The news can be in one of the three directories: 'N', 'O' or 'P'
        url = 'http://news.163.com/photoview/00AP0001/{}.html'.format(news_id)
        try:
            #sess.proxies = {'http': ip_list[randint(0,5)]}
            response = sess.get(url, allow_redirects=False)
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            sleep(5)
            print("That was a nice sleep, now let me continue...")
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            data = eval(soup.find(class_='gallery').find('textarea').text)
        except: # cannot found in 'P'
            url = 'http://news.163.com/photoview/00AO0001/{}.html'.format(news_id)
            try:
                #sess.proxies = {'http': ip_list[randint(0,5)]}
                response = sess.get(url, allow_redirects=False)
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                sleep(5)
                print("That was a nice sleep, now let me continue...")
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            try:
                data = eval(soup.find(class_='gallery').find('textarea').text)
            except: # cannot found in 'O'
                url = 'http://news.163.com/photoview/00AN0001/{}.html'.format(news_id)
                try:
                    #sess.proxies = {'http': ip_list[randint(0,5)]}
                    response = sess.get(url, allow_redirects=False)
                except:
                    print("Connection refused by the server..")
                    print("Let me sleep for 5 seconds")
                    sleep(5)
                    print("That was a nice sleep, now let me continue...")
                    continue
                soup = BeautifulSoup(response.text, 'lxml')
                try:
                    data = eval(soup.find(class_='gallery').find('textarea').text)
                except: # cannot found in 'N'
                    print('[ERROR] Cannot find news #{}, skipping this one...'.format(news_id))
                    news_id -= 1 # skip to next piece of news
                    continue

        # found the news
        title = data['info']['setname']
        text = data['info']['prevue']
        imgs = []
        for img_data in data['list']:
            imgs.append(img_data['img'])

        try:
            bbs_link = soup.find(class_='comment js-tielink').attrs['href']
        except:
            print('[ERROR] Cannot find comments in news #{}, skipping this one...'.format(news_id))
            news_id -= 1
            continue

        post_id = re.search('comment\.news\.163\.com/(.*?)/(.*?)\.html', bbs_link)
        post_id = post_id.group(2)
        newlist_url ='http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/' \
                       '{}/comments/newList?ibc=newspc&limit=30&showLevelThreshold=72&headLimit=1&tailLimit=2&offset=0'\
                        .format(post_id) # link to "最新评论"
        hotlist_url ='http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/' \
                       '{}/comments/hotList?ibc=newspc&limit=5&showLevelThreshold=72&headLimit=1&tailLimit=2&offset=0'\
                        .format(post_id) # link to "热门评论"

        def get_comments(url):
            comment_response = sess.get(url, allow_redirects=False)
            comment_response = comment_response.text
            pattern = re.compile('\"content\":\"(.*?)\"')
            comments = pattern.findall(comment_response)
            return comments

        comments = get_comments(hotlist_url) + get_comments(newlist_url)
        news = {'title': title, 'imgs': imgs, 'text': text, 'comments': comments}
        scratch_result[str(news_id)] = news
        news_cnt += 1
        print(title)

        if news_cnt % 100 == 0:
            json.dump(scratch_result, open('news.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
            with open('log.txt', 'w', encoding='utf-8') as log_file:
                log_file.write(str(news_id))
                log_file.flush()
            print('-'*20)
            print('[INFO]{} pieces of news finished.'.format(news_cnt))
            print('-'*20)

        news_id -= 1 # move to next page

if __name__ == '__main__':
    main()
