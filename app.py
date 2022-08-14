from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())

# the methods that the request can accept


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/botones', methods=['POST', 'GET'])
def botones():
    return render_template('Botones.html')


@app.route('/POST', methods=['POST', 'GET'])
def post():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',user=name)

if __name__ == "__main__":
    app.run(debug=True)
