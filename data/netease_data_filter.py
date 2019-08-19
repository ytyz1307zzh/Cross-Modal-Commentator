import json
import argparse
import os
import re
import jieba

# delete strings with illegal characters
def valid_text(str):
    if re.search('http', str):
        return False
    if re.search('&|#|@|\^|\$|\*', str):
        return False

    return True

def valid_comment(str):
    marks = ['，', '.', '。', '？', '！', '”', '“', '：', ' ', '；', '…', '、', '%', '（', '）', '《', '》']
    for char in str:
        if u'\u4e00'<= char <= u'\u9fff' or char.isalpha() or char.isdigit(): # legal chinese characters, digits or letters
            continue
        if char not in marks:
            str = str.replace(char, '')

    return str

# check for censor words in the sentence
def censor_words_check(sentence, opt):
    censor_words = []
    file_path = open(opt.censor_words, 'r', encoding='utf-8')
    for line in file_path:
        censor_words.append(line.strip())

    for word in sentence.strip().split():
        if word in censor_words:
            return False

    return True

data = json.load(open('netease_news.json', 'r', encoding='utf-8'))
parser = argparse.ArgumentParser()
parser.add_argument('-censor_words', required=True, help='list of censor words to remove from data')
opt = parser.parse_args()

if os.path.exists('netease_news_clean.json'):
    clean_data = json.load(open('netease_news_clean.json', 'r', encoding='utf-8'))
else:
    clean_data = {}

sentence_omit = 0

for id, content in data.items():

    if id in clean_data:
        continue

    comments = content['comments']
    text = content['text']
    title = content['title']
    images = content['imgs']

    # cut the sentences into words using jieba
    title_cut = ' '.join(jieba.cut(title))
    text_cut = ' '.join(jieba.cut(text))
    comments_cut = [' '.join(jieba.cut(sent)) for sent in comments]

    # filter illegal sentences
    if valid_text(text_cut):
        text_valid = text_cut
    else:
        print('[ERROR] Illegal text in news #{}, deleting this one...'.format(id))
        sentence_omit += 1
        continue
    comments_valid = [valid_comment(sent) for sent in comments_cut if censor_words_check(sent, opt)]
    sentence_omit += len(comments_cut) - len(comments_valid)

    result = {'title': title_cut, 'body': text_valid, 'comments': comments_valid, 'image': images}
    clean_data[id] = result
    cnt = len(clean_data)
    if cnt % 50 == 0:
        json.dump(clean_data, open('netease_news_clean.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
        print('-'*50)
        print('{} data finished.'.format(cnt))
        print('-'*50)

print('Final check, all {} data finished.'.format(len(clean_data)))
json.dump(clean_data, open('netease_news_clean.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
print('Sentences ommitted: ', sentence_omit)


