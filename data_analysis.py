import json
import pickle
word_lengths = [0 for _ in range(31)]
char_lengths = [0 for _ in range(52)]


def data_analysis(mode):
    print(mode)
    data = json.load(open(mode + '.json', 'r', encoding='utf-8'))
    for news in data:
        comment = news['tgt']
        cnt_words = len(comment.split())
        word_lengths[cnt_words] += 1
        cnt_chars = len(''.join(comment.split()))
        if cnt_chars > 51:
            cnt_chars = 51
        char_lengths[cnt_chars] += 1


data_analysis('train')
data_analysis('valid')
data_analysis('test')

print(word_lengths)
print(sum(word_lengths))
print(char_lengths)
print(sum(char_lengths))
