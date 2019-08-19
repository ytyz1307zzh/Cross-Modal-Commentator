import re
import json
import requests
import argparse
import os

# 加载图片的header
image_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

parser = argparse.ArgumentParser()
parser.add_argument('-save_dir', default='./yidian_image', help='directory to save your images')
opt = parser.parse_args()
requests.adapters.DEFAULT_RETRIES = 5
sess = requests.session()

news = json.load(open('yidian_news.json', 'r', encoding='utf-8'))
print('[INFO] News file loaded, containing {} pieces of news.'.format(len(news)))
if os.path.exists('yidian_exist_id.json'):
    exist_ids = json.load(open('yidian_exist_id.json', 'r', encoding='utf-8'))
    print('[INFO] Loaded exist_ids list, {} images crawled.'.format(len(exist_ids)))
else:
    exist_ids = []

for news_id, news_content in news.items():
    if news_id in exist_ids:
        print('[INFO] Already crawled news #{}, skipping...'.format(news_id))
        continue
    img_urls = news_content['images']

    for url in img_urls:
        if not re.search('i1\.go2yd\.com', url): # 爬下来的不是完整的url，是一个id
            image_url = 'http://i1.go2yd.com/image.php?url=' + url
        else:
            image_url = 'http:' + url

        image_response = sess.get(image_url, headers=image_headers)

        if image_response.status_code != 200:
            print('[ERROR] Cannot access image {}, skipping...'.format(image_url))
            with open('yidian_err.txt', 'a', encoding='utf-8') as f:
                print(image_url, file=f)
                f.flush()
            continue

        filename = image_url
        # process the url as filename
        filename = re.sub('http://', '', filename)
        filename = re.sub('/', '--', filename)
        filename = re.sub('\?', '~', filename)
        filename = filename + '.jpg'

        with open(opt.save_dir+'/'+filename, 'wb') as f:
            f.write(image_response.content)

    print('[INFO] News {} completed.'.format(news_id)) # if all related images are stored, print the id to signal the success
    exist_ids.append(news_id)
    news_cnt = len(exist_ids)
    if news_cnt % 50 == 0:
        json.dump(exist_ids, open('yidian_exist_id.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
        print('-'*50)
        print('[INFO] {} pieces of news finished.'.format(news_cnt))
        print('-'*50)

print('[INFO] All data finished.')
