# date : 2020-12-10
import jieba
import pymongo

# stopfilepath : 停用词txt文件路径
stopfilepath = '../jiebacut/stopwords.txt'

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

def txtcut():

    print('text cut Start!')

    mongo_client = pymongo.MongoClient('127.0.0.1',27017)
    db = mongo_client['myNewsDB']
    collection = db['news_coll']

    news = collection.find({})

    cut_collection = db['cut_news_coll']
    cut_collection.drop()

    for item in news:
        # 输出测试
        print(item['No'])

        # 分词后写入集合 db['cut_news_coll']
        cut_collection.insert_one({'No':item['No'],'cut_text':seg_sentence(item['titleNtext'])})
    print('text cut Done!')

if __name__ == '__main__':
    txtcut()