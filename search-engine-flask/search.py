# coding:utf-8
import jieba
import pymongo

from math import log10
from datetime import datetime, timedelta

# stopfilepath : 停用词txt文件路径
stopfilepath = '../jiebacut/stopwords.txt'

st = {}

mongoClient = pymongo.MongoClient('127.0.0.1',27017)
db = mongoClient['myNewsDB']
data = db['index_coll'].find({},{"_id":0})

for i in data:
    item = {i['word']:i['tfidf']}
    st.update(item)

searchlist = []

# 停用词转化为数组
def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords

# 分词 + 去停
def seg_sentence(sentence):
    # 先分词
    sentence_seged = jieba.cut_for_search(sentence.strip())
    # 这里加载停用词的路径
    stopwords = stopwordslist(stopfilepath)
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            # 去掉空格
            if word != ' ' and word != '　':
                outstr += word
                outstr += "|"
    return outstr

# 对输入内容进行分词
def cutsearch(txt):
    searchlist = list(filter(None, seg_sentence(txt).split("|")))
    return searchlist

def search_fun(str_key_word,searchtype):
    key_word = []
    # 对输入内容进行分词
    key_word = cutsearch(str_key_word)

    if int(searchtype)==0:
        return find_key(key_word),key_word

    if int(searchtype)==1:
        return find_time(key_word),key_word

    if int(searchtype)==2:
        return find_hot(key_word),key_word


def find_key(key_word):
    totaltfidf = {}
    for term in key_word:
        if term in st:
            maxlen = min(5000,len(st[term]))
            # 如果搜索词在倒排索引键中，对该词出现的文档-tfidf键值对进行遍历
            for i in range(maxlen):
                if st[term][i][0] not in totaltfidf:
                    totaltfidf[st[term][i][0]] = st[term][i][1]
                else:
                    totaltfidf[st[term][i][0]] += st[term][i][1]
    totaltfidf = sorted(totaltfidf.items(), key=lambda x: x[1], reverse = True)
    return totaltfidf

def find_time(key_word):
    time_scores = {}
    for term in key_word:
        if term in st:
            maxlen = min(5000,len(st[term]))
            # 对搜索词出现的文档-时间进行先后排序
            for i in range(maxlen):

                filedata = db['news_coll'].find_one({'No':st[term][i][0]},{"_id":0})

                news_datetime = datetime.strptime(filedata['time']+':00', "%Y-%m-%d %H:%M:%S")
                now_datetime = datetime.now()
                td = now_datetime - news_datetime

                docid = int(st[term][i][0])
                td = (timedelta.total_seconds(td) / 86400) # day
                td = ("%.4f"%td)
                if st[term][i][0] not in time_scores:
                    time_scores[docid] = td
                else:
                    time_scores[docid] += td
    time_scores = sorted(time_scores.items(), key=lambda x: x[1])
    if len(time_scores) == 0:
        return []
    else:
        return time_scores

def find_hot(key_word):
    hot_scores = {}
    for term in key_word:
        if term in st:
            maxlen = min(5000,len(st[term]))
            # 对计算后的热度进行先后排序
            for i in range(maxlen):
                filedata = db['news_coll'].find_one({'No':st[term][i][0]},{"_id":0})

                news_datetime = datetime.strptime(filedata['time']+':00', "%Y-%m-%d %H:%M:%S")
                now_datetime = datetime.now()
                td = now_datetime - news_datetime

                docid = int(st[term][i][0])
                td = (timedelta.total_seconds(td) / 60) # min
                hot = 10000*(log10(1.5*float(st[term][i][1]))+float(filedata['comment'])*0.02)/td
                hot = ("%.4f"%hot)
                if st[term][i][0] not in hot_scores:
                    hot_scores[docid] = hot
                else:
                    hot_scores[docid] += hot
    hot_scores = sorted(hot_scores.items(), key=lambda x: x[1], reverse=True)
    if len(hot_scores) == 0:
        return []
    else:
        return hot_scores