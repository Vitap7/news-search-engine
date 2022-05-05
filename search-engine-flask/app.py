# coding:utf-8
import pymongo

from search import search_fun
from page_utils import Pagination
from flask import Flask, request, render_template, redirect, url_for
from collections import deque

app = Flask(__name__, static_url_path='')

@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'POST' and  request.form.get('query'):
        query = request.form['query']
        searchtype = request.form['r_sel']
        return redirect(url_for('search', query=query, searchtype=searchtype))
    return render_template('index.html')

@app.route("/search/<searchtype>/<query>", methods=['POST', 'GET'])

def search(query,searchtype):
    searcharr = [0,0,0]
    searcharr[int(searchtype)] = 1
    docs,terms = search_fun(query,searchtype)

    result = highlight(docs, terms)

    pager_obj = Pagination(request.args.get("page", 1), len(result), request.path, request.args, per_page_count=10)

    index_list = result[pager_obj.start:pager_obj.end]

    html = pager_obj.page_html()

    return render_template('search.html', docs=index_list, value=query, length=len(docs), html=html, searchArr=searcharr)

def highlight(docs, terms):
    # 使用deque，优化性能
    result = deque()
    mongoClient = pymongo.MongoClient('127.0.0.1',27017)
    db = mongoClient['myNewsDB']

    for doc in docs:
        data = db['news_coll'].find_one({'No':doc[0]})
        title = data['title']
        for term in terms:
            title = title.replace(term, '<font color="red">{}</font>'.format(term))
        result.append((data['url'],data['time'],data['text'][0:66],title))

    result = list(result)
    return result

if __name__ == "__main__":
    app.run(host='localhost', port=7777, debug=False, threaded=True)