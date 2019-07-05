import os, requests, operator, re, nltk
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS',"config.DevelopmentConfig"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

q = Queue(connection=conn)

from models import *

print("*"*50)
print(os.environ.get('APP_SETTINGS',"config.DevelopmentConfig"))
print("*"*50)

def count_and_save_words(url):
    errors = []
    try:
        r = requests.get(url)
    except:
        errors.append("Unable to get URL. Please make sure its valid and try agaon.")
        return {"error":errors}

    # text Processing
    raw = BeautifulSoup(r.text).get_text()
    nltk.data.path.append('./nltk_data/')  # Set the path
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)
    # remove punctuations, count raw words
    nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if nonPunct.match(w)]
    raw_words_count = Counter(raw_words)
    # stop words
    no_stop_words = [w for w in raw_words if w.lower() not in stops]
    no_stop_words_count = Counter(no_stop_words)

    #Save the results
    try:
        result = Result(url=url, result_all=raw_words_count, result_no_stop_words=no_stop_words_count)
        db.session.add(result)
        db.session.commit()
        return result.id
    except:
        errors.append("Unable to add items to Database")
        return {"error": errors}


@app.route('/',methods=['POST','GET'])
def index():
    print("H"*50)
    results = {}
    if request.method == "POST" or request.method == "GET":
        print(request.method)
        print("N" * 50)
        # get url that the user has entered
        url = request.form['url']
        print("url: ",url)
        print("L"*50)
        if 'http://' not in url[:7]:
            url = 'http://'+ url
        job = q.enqueue_call(func=count_and_save_words,args=(url,), result_ttl=5000)
        print("*" * 50)
        print(job.get_id())
        print("*" * 50)
        return render_template('index.html', results=results)

@app.route("/results/<job_key>",methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key,connection=conn)
    if job.is_finished:
        return str(job.result),200
    else:
        return "Nay!", 202

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == "__main__":
    app.run()