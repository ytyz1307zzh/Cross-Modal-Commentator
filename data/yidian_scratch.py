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
# 动态加载新闻页时的header
channel_headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cookie': 'JSESSIONID=ae209fc7214d602cbced493ca4b0e45de4fbf156573351521b7f1b8a72ea49d6; wuid=51550058039081; wuid_createAt=2018-12-22 22:57:37; UM_distinctid=167d66bf6624a-04df86a20fd067-47e1039-144000-167d66bf663991; weather_auth=2; Hm_lvt_15fafbae2b9b11d280c79eff3b840e45=1546602903,1547032936,1547131703,1547198428; CNZZDATA1255169715=1186738594-1545486941-null%7C1547194443; captcha=s%3Ae1c037bd76c2e9e2fefbbbe942c1c5df.a%2Bco24ItNPllzyb3m0Vd2ifT9G%2Fm%2Fp1VVLZ1TC9M7C8; Hm_lpvt_15fafbae2b9b11d280c79eff3b840e45=1547198432; cn_1255169715_dplus=%7B%22distinct_id%22%3A%20%22167d66bf6624a-04df86a20fd067-47e1039-144000-167d66bf663991%22%2C%22sp%22%3A%20%7B%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201547198430%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201547198430%7D%7D',                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'}
# 动态加载评论的header
comment_headers = { 'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cookie': 'CNZZDATA1255169715=714140876-1547030693-null%7C1547030693; weather_auth=2; captcha=s%3A3698c8dd74a6309b22c4b17a84bde20d.uemvhP7r1RLqXriU0F2XrnhIywWn%2FEjFhOLdAMGS%2B8A; JSESSIONID=a7808b3ad1aba5e095cd18791626b68c4311c394b24c0c43b965cb3e67438e70; wuid_createAt=2019-01-09 19:28:12; UM_distinctid=168325ec2b1441-0e038d78fa1414-784a5037-144000-168325ec2b34f1; Hm_lvt_15fafbae2b9b11d280c79eff3b840e45=1547033293; wuid=523545640592177; Hm_lpvt_15fafbae2b9b11d280c79eff3b840e45=1547033375; cn_1255169715_dplus=%7B%22distinct_id%22%3A%20%22168325ec2b1441-0e038d78fa1414-784a5037-144000-168325ec2b34f1%22%2C%22sp%22%3A%20%7B%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201547033391%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201547033391%7D%7D',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
                    'X-Requested-With': 'XMLHttpRequest'}

# function to automatically generate the parameter "_spt"
def get_spt(cstart, cend):

    prefix = 'yz~eaod8:2898=9:38'
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
    length = len(scratch_result)
    while True:
        try:
            for cstart in range(0, 50, 10):
                cend = cstart + 10

                channel_params = {'channel_id': 20823273092,
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
                next_list = eval(response.text)['result'] # 返回的动态加载的新闻list

                comment_url = 'http://www.yidianzixun.com/home/q/getcomments' # 评论url
                for news_dict in next_list:
                    doc_id = news_dict['docid'] # 新闻id

                    if doc_id in scratch_result:
                        continue

                    title = news_dict['title'] # 标题
                    summary = news_dict['summary']
                    gallery_items = news_dict['gallery_items']
                    desc = [] # 新闻中文字
                    img_id = [] # 新闻中图片的id
                    for item in gallery_items:
                        desc.append(item['desc'])
                        img_id.append(item['img'])

                    # 爬取评论
                    comment_params = {  '_': round(time.time()*1000),
                                        'docid': doc_id,
                                        's': '',
                                        'count': 30,
                                        'last_comment_id': '',
                                        'appid': 'web_yidian'}
                    comment_response = sess.get(comment_url, params=comment_params, headers=comment_headers)

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

                    news_cnt = len(scratch_result)
                    if news_cnt % 10 == 0:
                        json.dump(scratch_result, open('yidian_news.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
                        print('-'*50)
                        print('[INFO] {} pieces of news saving into json file...'.format(news_cnt))
                        print('-'*50)
                    if news_cnt >= opt.n_news:
                        print('[INFO] All finished.')

        except KeyboardInterrupt:
            quit()
        except:
            traceback.print_exc()
            pass


            # 这次获得的list内的新闻爬完了

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-save_dir', default='./yidian_image', help='directory to save the images')
    parser.add_argument('-n_news', type=int, required=True, help='how many news you want to acquire')
    opt = parser.parse_args()
    main(opt)
