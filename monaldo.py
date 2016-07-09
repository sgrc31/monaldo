#!/usr/bin/env python3

import os
from flask import Flask, render_template
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

basedir_booksdb = os.path.abspath(os.path.dirname('ebooks/metadata.db'))
basedir_usersdb = os.path.abspath(os.path.dirname('.'))

app = Flask(__name__)
app.config['SQLALCHEMY_BINDS'] = {'booksdb': 'sqlite:///{}'.format(os.path.join(basedir_booksdb, 'metadata.db')),
                                  'usersdb': 'sqlite:///{}'.format(os.path.join(basedir_usersdb, 'users.sqlite'))}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)
manager = Manager(app)


#######################
# Classi database
#######################
class Books(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    author_sort = db.Column(db.Text)


############
# Routes
############
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/authors')
def authors():
    return render_template('authors.html', names = Books.query.all())

@app.route('/authors/<author_name>')
def author_page(author_name):
    return render_template('author_page.html',
                           author_name = author_name,
                           book_objects_list = Books.query.filter_by(author_sort=author_name).all()
                           )

@app.route('/book/<book_id>/<book_title>')
def book_page(book_id, book_title):
    if book_title == Books.query.filter_by(id=book_id).first().title:
        return render_template('book_page.html',
                               book_id = book_id,
                               book_title = book_title,
                               book_object = Books.query.filter_by(id=book_id).first()
                               )
    else:
        return 'nope' #TODO insert 404 error

@app.route('/user/<nome>')
def user(nome):
    return render_template('user.html', name=nome)

if __name__ == '__main__':
    manager.run()
