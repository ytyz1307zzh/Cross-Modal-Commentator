import requests
from bs4 import BeautifulSoup
import re
import traceback
import argparse
import time
import json
import os
import goto
from goto import with_goto

true = True
false = False
null = ''
requests.adapters.DEFAULT_RETRIES = 5
sess = requests.session()

channel_headers = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cookie': 'JSESSIONID=ae209fc7214d602cbced493ca4b0e45de4fbf156573351521b7f1b8a72ea49d6; wuid=51550058039081; wuid_createAt=2018-12-22 22:57:37; UM_distinctid=167d66bf6624a-04df86a20fd067-47e1039-144000-167d66bf663991; weather_auth=2; Hm_lvt_15fafbae2b9b11d280c79eff3b840e45=1546443904,1546492344,1546505849,1546522961; CNZZDATA1255169715=1186738594-1545486941-null%7C1546519500; captcha=s%3A3d8f1f220676a8113c64627d3ebb4d68.KKsdLdC8KERynrW%2F%2FPi0dEDbkFLoCB4RJAZsrJ1yqu4; Hm_lpvt_15fafbae2b9b11d280c79eff3b840e45=1546523513; cn_1255169715_dplus=%7B%22distinct_id%22%3A%20%22167d66bf6624a-04df86a20fd067-47e1039-144000-167d66bf663991%22%2C%22sp%22%3A%20%7B%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201546523511%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201546523511%7D%7D',
                    'Host': 'www.yidianzixun.com',
                    'Referer': 'http://www.yidianzixun.com/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'}
# 动态加载评论的header
headers = { 'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cookie': 'JSESSIONID=ae209fc7214d602cbced493ca4b0e45de4fbf156573351521b7f1b8a72ea49d6; wuid=51550058039081; wuid_createAt=2018-12-22 22:57:37; UM_distinctid=167d66bf6624a-04df86a20fd067-47e1039-144000-167d66bf663991; weather_auth=2; Hm_lvt_15fafbae2b9b11d280c79eff3b840e45=1546182993,1546183077,1546183084,1546232681; CNZZDATA1255169715=1186738594-1545486941-null%7C1546232328; Hm_lpvt_15fafbae2b9b11d280c79eff3b840e45=1546234187; cn_1255169715_dplus=%7B%22distinct_id%22%3A%20%22167d66bf6624a-04df86a20fd067-47e1039-144000-167d66bf663991%22%2C%22sp%22%3A%20%7B%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201546234562%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201546234562%7D%7D; captcha=s%3A26df437640ebe6baf4b8ec6bfb606ceb.9HF5hG12WgXUIUP9HMpkO8gW%2F5%2BHOe1siljRbjhhUfA',
                'Host': 'www.yidianzixun.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'}

# function to automatically generate the parameter "_spt"
def get_spt(cstart, cend):

    prefix = 'yz~eaodhoy~'
    convert_dict = {'0': ':',
                    '1': ';',
                    '2': '8',
                    '3': '9',
                    '4': '>',
                    '5': '?',
                    '6': '<',
                    '7': '=',
                    '8': '2',
                    '9': '3'}

    spt = ''
    for i in str(cstart):
        spt = spt + convert_dict[i]
    for j in str(cend):
        spt = spt + convert_dict[j]
    return prefix + spt

@with_goto
def main(opt):
    global true
    global false
    global null

    if os.path.exists('yidian_news.json'):
        scratch_result = json.load(open('yidian_news.json', 'r', encoding='utf-8'))
        length = len(scratch_result)
        print('[INFO] Loaded {} news from yidian_news.json'.format(length))
    else:
        scratch_result = {}

    channel_url = r'http://www.yidianzixun.com/home/q/news_list_for_channel'
    while True:
        try:
            success_cnt = 0
            for cstart in range(0, 100, 10):
                cend = cstart + 10
                print('cstart: ', cstart)

                channel_params = {'channel_id': 'best',
                            'cstart': cstart,
                            'cend': cend,
                            'infinite': 'true',
                            'refresh': 1,
                            '__from__': 'pc',
                            'multi': 5,
                            '_spt': get_spt(cstart, cend),
                            'appid': 'web_yidian',
                            '_': round(time.time()*1000)}

                response = sess.get(channel_url, params=channel_params, headers=channel_headers)
                with open('debug.txt', 'w', encoding='utf-8') as f:
                    print(response, file=f)
                    
                try:
                    next_list = eval(response.text)['result'] # 返回的动态加载的新闻list
                except:
                    print('[ERROR] Cannot get more news, early stopping...')
                    break

                comment_url = 'http://www.yidianzixun.com/home/q/getcomments' # 评论url
                news_prefix = 'http://www.yidianzixun.com/article/'
                for news_dict in next_list:
                    doc_id = news_dict['docid'] # 新闻id

                    if doc_id in scratch_result:
                        continue

                    news_url = news_prefix + doc_id
                    news_response = sess.get(news_url, headers=headers)

                    soup = BeautifulSoup(news_response.text, 'lxml')
                    left_wrapper = soup.find(class_='left-wrapper')
                    if not left_wrapper:
                        print('[ERROR] News #{} is not a Yidianzixun news'.format(doc_id))
                        continue
                    title = left_wrapper.find('h2').text
                    img_items = soup.find_all(class_='a-image')
                    img_id = []
                    for item in img_items:
                        image = item.find('img')['src']
                        img_id.append(image)
                    summary = re.search('<meta name=\"description\" content=\"(.*?)\">', news_response.text).group(1)
                    content_bd = soup.find(class_='content-bd')
                    if not content_bd:
                        print('[ERROR] News #{} is not a Yidianzixun news'.format(doc_id))
                        continue
                    desc_items = content_bd.find_all('p')
                    desc = []
                    for item in desc_items:
                        if item.text:
                            desc.append(item.text)


                    # 爬取评论
                    comment_params = {  '_': round(time.time()*1000),
                                        'docid': doc_id,
                                        's': '',
                                        'count': 30,
                                        'last_comment_id': '',
                                        'appid': 'web_yidian'}
                    comment_response = sess.get(comment_url, params=comment_params, headers=headers)

                    comments = []
                    comment_dict = eval(comment_response.text)['comments']
                    for comment_piece in comment_dict:
                        comments.append(comment_piece['comment'])
                    if not comments:
                        print('[WARNING] There are no comments in news #{}, skipping this one...'.format(doc_id))
                        continue

                    # 保存爬取的数据
                    news = {'title': title, 'summary': summary, 'description': desc, 'images': img_id, 'comments': comments}
                    scratch_result[doc_id] = news
                    print(title) # 打印title以表示成功爬取
                    success_cnt += 1

                    news_cnt = len(scratch_result)
                    if news_cnt % 10 == 0:
                        json.dump(scratch_result, open('yidian_news.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
                        print('-'*50)
                        print('[INFO] {} pieces of news saving into json file...'.format(news_cnt))
                        print('-'*50)
                
            if success_cnt == 0:
                print('The website cannot refresh now. Let me sleep for {} seconds before retrying'.format(opt.sleep_time))
                time.sleep(opt.sleep_time)

        except KeyboardInterrupt:
            quit()
        except:
            traceback.print_exc()
            pass
            # 这次获得的list内的新闻爬完了


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n_news', type=int, required=True, help='how many news you want to acquire')
    parser.add_argument('-sleep_time', type=int, default=600, help='how many seconds do you want to sleep between rounds')
    opt = parser.parse_args()
    main(opt)
