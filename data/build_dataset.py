import json
import pickle
import argparse
import numpy as np
import re
import os

def convert_filename(url, opt):
    if opt.source == 'yidian':
        if not re.search('i1\.go2yd\.com', url): # 爬下来的不是完整的url，是一个id
            filename = 'http://i1.go2yd.com/image.php?url=' + url
        else:
            filename = 'http:' + url
    else:
        filename = url
    filename = re.sub('http://', '', filename)
    filename = re.sub('/', '--', filename)
    filename = re.sub('\?', '~', filename)
    filename = filename + '.jpg'

    return filename

parser = argparse.ArgumentParser()
parser.add_argument('-source', choices=['sina', 'yidian', 'netease'], required=True)
opt = parser.parse_args()

news_data_path = '{}_selected_data.json'.format(opt.source)
image_data_path = '{}_features.pkl'.format(opt.source)

news_data = json.load(open(news_data_path, 'r', encoding='utf-8'))
image_data = pickle.load(open(image_data_path, 'rb'))

dataset = {}
for id, content in news_data.items():
    image_list = content['image']
    title = content['title']
    comments = content['comments']
    body = content['body']
    image_features = []

    for url in image_list:
        filename = convert_filename(url, opt)
        if filename in image_data:  # find the image name in image_data
            image_features.append(image_data[filename])

    result = {'title': title, 'body': body, 'comments': comments, 'image': image_features}
    dataset[id] = result

    cnt = len(dataset)
    if cnt % 100 == 0:
        print('{} pieces of data finished.'.format(cnt))

json.dump(dataset, open('{}_data.json'.format(opt.source), 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
print('Final check, all {} pieces of data finished.'.format(len(dataset)))

