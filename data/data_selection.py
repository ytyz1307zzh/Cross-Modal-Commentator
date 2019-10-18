import json
import argparse
import traceback
import os
import re

# for every comment in comment_list, decide whether this is a valid comment
def valid_comment_length(comment_list):
    valid_comment_list = []
    for comment in comment_list:
        sentence = comment.strip().split()
        length = len(sentence)
        if 5 <= length <= 30:
            valid_comment_list.append(comment)

    return valid_comment_list

# if valid, return body itself, otherwise return None
def valid_body_length(body):
    # body in netease is a string, while others' are lists
    if type(body) == list:
        valid_body_list = []
        total_length = 0

        for string in body:
            # remove repetitive sentences
            if string in valid_body_list:
                continue
            sentence = string.strip().split()

            if total_length + len(sentence) > 100:
                break
            total_length += len(sentence)
            valid_body_list.append(string)

        # if the whole text is less than 20 words, or the first sentence is more than 50 words, return None
        if 10 <= total_length <= 100:
            return ' '.join(valid_body_list)
        else:
            return None

    elif type(body) == str:
        sentence = body.strip().split()
        length = len(sentence)
        if 10 <= length <= 100:
            return body
        else:
            return None
    else:
        raise TypeError('Invalid type for "body", expected str or list')

# return whether there is enough comments in this news
def valid_comment_number(comment_list):
    if len(comment_list) < 10:
        return False
    else:
        return True

'''
# if there is appropriate number of images in this news, return a list of file names. Otherwise return None
def valid_image_number(image_list, opt): # image_list: listed images in data (might not all crawled successfully)
    image_dir = opt.source + '_image'
    crawled_list = os.listdir(image_dir) # All crawled images

    # some image data in yidian are just id instead of url
    if opt.source == 'yidian':
        image_list = [image if re.search('i1\.go2yd\.com', image) else
                      'i1.go2yd.com/image.php?url='+image for image in image_list]

    # convert url to saved path
    for i in range(len(image_list)):
        image_list[i] = re.sub('http://', '', image_list[i])
        image_list[i] = re.sub('/', '--', image_list[i])
        image_list[i] = re.sub('\?', '~', image_list[i])
        image_list[i] = image_list[i] + '.jpg'

    valid_image_list = [image for image in image_list if image in crawled_list]
    if 4 <= len(valid_image_list) <= 10:
        return valid_image_list
    else:
        return None
'''
def valid_image_number(image_list, opt):
    if 3 <= len(image_list) <= 15:
        return image_list
    else:
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-source', required=True, choices=['netease', 'sina', 'yidian', 'toutiao'])
    opt = parser.parse_args()

    data_path = opt.source + '_news_clean.json'
    all_data = json.load(open(data_path, 'r', encoding='utf-8'))
    print('[INFO] All data loaded, containing {} pieces of news.'.format(len(all_data)))

    if os.path.exists(opt.source + '_selected_data.json'):
        select_result = json.load(open(opt.source + '_selected_data.json', 'r', encoding='utf-8'))
        print('[INFO] Previous selected data loaded, containing {} pieces of news.'.format(len(select_result)))
    else:
        select_result = {}

    cnt1 = 0
    cnt2 = 0
    cnt3 = 0
    cnt4 = 0
    for id, news_data in all_data.items():

        if id in select_result:
            continue

        comments = news_data['comments']
        images = news_data['image']
        body = news_data['body']
        title = news_data['title']

        # criterion 1: comment length
        comments = valid_comment_length(comments)
        if not comments:
            cnt1 += 1
            continue

        # criterion 2: body length
        body = valid_body_length(body)
        if not body:
            cnt2 += 1
            continue

        # criterion 3: number of comments
        if not valid_comment_number(comments):
            cnt3 += 1
            continue

        # criterion 4: number of images
        # TODO: Change this simple version of valid_image_number to full version in final decision
        images = valid_image_number(images, opt)
        if not images:
            cnt4 += 1
            continue

        # Congratulations! You are qualified to be selected into the dataset!
        result = {'title': title, 'body': body, 'comments': comments, 'image': images}
        select_result[id] = result

        cnt = len(select_result)
        if cnt % 100 == 0:
            json.dump(select_result, open(opt.source + '_selected_data.json', 'w', encoding='utf-8'),
                      indent=4, ensure_ascii=False)
            print('[INFO] {} pieces of data selected.'.format(cnt))

    print('[INFO] Final check: {} pieces of data selected.'.format(len(select_result)))
    json.dump(select_result, open(opt.source + '_selected_data.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
    print('[INFO] Original data: ', len(all_data))
    print('News ommitted because of comment length: ', cnt1)
    print('News ommitted because of body length: ', cnt2)
    print('News ommitted because of comment number: ', cnt3)
    print('News ommitted because of image number: ', cnt4)

