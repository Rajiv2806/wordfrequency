import os, requests, operator, re, nltk
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS',"config.DevelopmentConfig"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result

print("*"*50)
print(os.environ.get('APP_SETTINGS',"config.DevelopmentConfig"))
print("*"*50)

@app.route('/',methods=['POST','GET'])
def index():
    errors = []
    results = {}
    print(">"*50)
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['url']
            r = requests.get(url)
        except:
            errors.append("Unable to get URL. Please make sure its Valid.")
            return render_template('index.html', errors=errors)
        if r:
            # text Processing
            raw = BeautifulSoup(r.text,'html.parser').get_text()
            nltk.data.path.append('./nltk_data/') # Set the path
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)
            # remove punctuations, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_words_count = Counter(raw_words)
            #stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)
            # Save the results
            results = sorted(no_stop_words_count.items(),
                             key=operator.itemgetter(1),
                             reverse=True
                             )[:10]
            print("*" * 50)
            print(results)
            print("*" * 50)
            try:
                print("1")
                result = Result(url=url,result_all=raw_words_count,result_no_stop_words=no_stop_words_count)
                db.session.add(result)
                db.session.commit()
                print("11")
                return render_template('index.html',errors=errors, results=results)
            except:
                print("2")
                errors.append("Unable to add item to database")
        return render_template('index.html',errors=errors, results=results)

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == "__main__":
    app.run()