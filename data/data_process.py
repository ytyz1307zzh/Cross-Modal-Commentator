import json
import pickle
import codecs
import random

def save(data_list, mode):
    print(mode)
    text_list = []
    image_list = []
    for data in data_list:
        text_list.append({'src': data['src'], 'tgt': data['tgt']})
        image_list.append(data['image'])
    json.dump(text_list, open(mode+'.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
    pickle.dump(image_list, open(mode+'.img', 'wb'))

def data_split(data):
    data_list = []
    cnt_news = 0

    for id, content in data.items():
        images = content['image']
        title = content['title']
        comments = content['comments']
        body = content['body']
        body_length = len(body.strip().split())
        if body_length < 10 or body_length > 70:
            continue

        for i in range(len(images)):
            for j in range(len(images[i])):
                if 0 <= images[i][j] < 0.00001:
                    images[i][j] = 0.00001
                elif -0.00001 < images[i][j] < 0:
                    images[i][j] = -0.00001

        for cmt in comments:
            data_list.append({'src': title + ' ' + body, 'tgt': cmt, 'image': images})

        cnt_news += 1
        if cnt_news % 1000 == 0:
            print(cnt_news)

    print('data_list: ', len(data_list))
    random.shuffle(data_list)
    test_data = data_list[:2000]
    valid_data = data_list[2000:7000]
    train_data = data_list[7000:]
    print('test data: ', len(test_data))
    print('valid data: ', len(valid_data))
    print('train data: ', len(train_data))

    save(test_data, 'test')
    save(valid_data, 'valid')
    save(train_data, 'train')


netease_data = json.load(open('./netease_data.json', 'r', encoding='utf-8'))
yidian_data = json.load(open('./yidian_data.json', 'r', encoding='utf-8'))
sina_data = json.load(open('./sina_data.json', 'r', encoding='utf-8'))
print('netease: ', len(netease_data))
print('yidian: ', len(yidian_data))
print('sina: ', len(sina_data))

all_data = netease_data
all_data.update(yidian_data)
all_data.update(sina_data)

print('total: ', len(all_data))

data_split(all_data)
print('finished.')