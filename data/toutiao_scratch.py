import selenium
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import os
import time
import json
import argparse
import traceback

parser = argparse.ArgumentParser()
parser.add_argument('-rounds', type=int, required=True, help='one round equals one refresh')
parser.add_argument('-sleep_time', type=int, default=600, help='time to sleep when the website cannot refresh')
parser.add_argument('-expire_time', type=int, default=120, help='time limit to stop scrolling the page (sec)')
opt = parser.parse_args()

# 配置
options = webdriver.ChromeOptions()
options.add_argument('lang=zh_CN.UTF-8')

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)
js_bottom = "var q=document.documentElement.scrollTop=100000"
js_top = "var q=document.documentElement.scrollTop=0"

# 读取保存的数据
if os.path.exists('toutiao_news.json'):
    scratch_result = json.load(open('toutiao_news.json', 'r', encoding='utf-8'))
    print('[INFO] Loaded {} pieces of data from json file.'.format(len(scratch_result)))
else:
    scratch_result = {}

# 打开浏览器
empty_rounds = 0
for i in range(opt.rounds):
    print('-'*10 + 'Round {}'.format(i+1) + '-'*10)
    driver.get(r'https://www.toutiao.com/ch/news_image/')
    driver.refresh() # 刷新界面
    time.sleep(3)

    # 滚动滚轮，尽可能加载页面
    start = time.clock()
    while True:
        end = time.clock()
        if end - start > opt.expire_time:
            break
        driver.execute_script(js_bottom)

    # 找到当前页面所有新闻
    images = driver.find_elements_by_class_name('img-item')
    print('[INFO] {} pieces of news found in this round'.format(len(images)))
    
    if len(images) < 10:
        empty_rounds += 1
        print('Accumulated empty rounds: ', empty_rounds)
        if empty_rounds > 10:
            print('The website cannot refresh, let me sleep for {} seconds'.format(opt.sleep_time))
            time.sleep(opt.sleep_time)
    else:
        empty_rounds = 0
        
    links = []
    for img_item in images:
        url = img_item.find_element_by_tag_name('a').get_attribute('href')
        links.append(url)
    time.sleep(3)

    for url in links:
        news_id = re.search('(\d+)', url).group(1)
        if str(news_id) in scratch_result:
            print('[INFO] Already crawled news #{}, skipping...'.format(news_id))
            continue

        # 找到标题、图片、描述
        driver.get(url)
        page_source = driver.page_source
        try:
            title = re.search('<title>(.*?)</title>', page_source).group(1)
            gallery_info = re.search('gallery: JSON\.parse\((.*?)\)', page_source).group(1)
            gallery_dict = json.loads(json.loads(gallery_info, encoding='utf-8'))
        except:
            print('[WARNING] News #{} is not a toutiao page, skipping...'.format(news_id))
            continue

        try:
            images = []
            for image_info in gallery_dict['sub_images']:
                images.append(image_info['url'])
            texts = gallery_dict['sub_abstracts']
        except:
            print('[WARNING] There are no images in news #{}, skipping...'.format(news_id))
            continue

        # 找到评论（可能有）
        comments = []
        comment_items = driver.find_elements_by_class_name('c-content')
        if not comment_items:
            print('[WARNING] There are no comments in news #{}, skipping...'.format(news_id))
            continue
        for item in comment_items:
            comment = item.find_element_by_tag_name('p').text
            comments.append(comment)

        # 保存数据
        news = {'title': title, 'id': news_id, 'images': images, 'texts': texts, 'comments': comments}
        scratch_result[str(news_id)] = news
        print('[INFO] 新闻#{}爬取成功。'.format(news_id))

        data_cnt = len(scratch_result)
        if data_cnt % 10 == 0:
            print('-'*50+'\n'+'[INFO] {} pieces of data finished.'.format(data_cnt)+'\n'+'-'*50)
            json.dump(scratch_result, open('toutiao_news.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
            print('Let me rest for a while...otherwise they may block me QAQ')
            time.sleep(5)


driver.close()
print('[INFO] Congratulations! All data finished.')

