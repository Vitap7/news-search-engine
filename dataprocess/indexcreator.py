import jieba
import pymongo
import math as m

store1 = {}
store2 = {}
store3 = {}

# 总文件数
global N
N = 0

# wordsoftxt记录文件的词数，与文件中"|"数目相同，用于TF-IDF计算
global wordsoftxt
wordsoftxt = 0

def word_count(words):
    # counts用于记录每个文件的字典，即{'词语':次数}
    counts = {}
    for word in words:
        counts[word]=counts.get(word,0)+1
    return counts

# 实现倒排索引
# file表示文件号，counts[key]为词出现的次数
def inverted_index(file,counts):
    for key in counts:
        if key in store1:
            store1[key].append([file,counts[key]])
        else:
            store1[key]=[[file,counts[key]]]
    return store1


def tfidf_index(store1,store2):
    for key in store1:
        # dt 表示包含该词的文档数目
        dt = len(store1[key])
        #print('key',key,'dt=',dt)
        for j in range(1,dt+1,1):
            # store1[key][j-1][1] 代表该词在x号文件中出现的次数，数组下标与文件编号相差1

            No_x_txt = store1[key][j-1][0]
            # 计算TD-IDF
            tf = float(store1[key][j-1][1]/wordsoftxt)
            idf = m.log(float(N/(dt+1)))
            tfidf = tf*idf

            if key in store2:
                store2[key].append([No_x_txt,tfidf])
                #print('add!')
            else:
                store2[key]=[[No_x_txt,tfidf]]
                #print('init!')
    store1.clear()
    return store2

def indexcreate():

    mongo_client = pymongo.MongoClient('127.0.0.1',27017)
    db = mongo_client['myNewsDB']
    news = db['cut_news_coll'].find({})

    global N
    # pymongo 4.0删除了count()方法,下行代码不可用
    # N = db['cut_news_coll'].find().count()
    for item in news:
        N+=1
        #print(item)

        # 将词语加入到列表wordArr中
        wordArr = []
        wordArr = item['cut_text'].split("|")
        # 去掉wordArr的空字符串
        wordArr = list(filter(None,wordArr))
        global wordsoftxt
        wordsoftxt = len(wordArr)

        # wordandtimes用于表示文件的词语与数量的键值对
        wordandtimes = {}
        wordandtimes = word_count(wordArr)

        # 测试
        #print(wordandtimes)

        # len(wordArr) ≠ wordsoftxt = len(wordandtimes)，是因为调用word_count之后重复的词并作一键
        # 但TF-IDF计算时要用调用之前的词数，不然极端情况下可能会出现TF>1的情况，不利于词频计算
        # 所以在上面有wordsoftxt = len(wordArr)

        inverted_index(item['No'],wordandtimes)
    wordandtimes.clear()
    tfidf_index(store1,store2)

    #print('store1:',store1)

def tfidf_sorted(store2):
    for key in store2:
        store3_key = sorted(store2[key], key=lambda x: x[1],reverse = True)
        if key in store3:
            store3[key].append(key,store3_key)
        else:
            store3[key] = store3_key

    store2.clear()
    return store3

def tfidfsorted():

    print("tfidfsorted() start!")

    mongoClient = pymongo.MongoClient('127.0.0.1',27017)
    db = mongoClient['myNewsDB']
    coll = db['index_coll']
    coll.drop()

    for item in store3:
        #print(item)
        data = {'word':item,'tfidf':store3[item]}
        print(data)
        coll.insert_one(data)

    store3.clear()
    print("tfidfsorted() done!")


if __name__ == '__main__':
    indexcreate()

    tfidf_sorted(store2)

    tfidfsorted()