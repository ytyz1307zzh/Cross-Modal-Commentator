import json

def data_selection(path):
    data = json.load(open(path, 'r', encoding='utf-8'))
    cnt_news = 0
    cnt_comments = 0
    
    for id, news in data.items():
        title = news['title'].strip().split()
        body = news['body'].strip().split()
        body_length = len(body)
        if body_length >= 10 and body_length <= 70:
            cnt_news += 1
            comments = news['comments']
            cnt_comments += len(comments)
            
    print('news: ', cnt_news)
    print('comments: ', cnt_comments)

print('netease')
data_selection('./netease_data.json')
print('sina')
data_selection('./sina_data.json')
print('yidian')
data_selection('./yidian_data.json')