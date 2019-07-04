import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS',"config.DevelopmentConfig"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result

print("*"*50)
print(os.environ.get('APP_SETTINGS',"config.DevelopmentConfig"))
print("*"*50)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == "__main__":
    app.run()