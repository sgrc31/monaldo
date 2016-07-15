#!/usr/bin/env python3

import os
import random
from flask import Flask, render_template
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

basedir_booksdb = os.path.abspath(os.path.dirname('metadata.db'))
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
class Authors(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    sort = db.Column(db.Text)
    
class Books(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    sort = db.Column(db.Text, nullable=False)
    author_sort = db.Column(db.Text)
    path = db.Column(db.Text)

class Data(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.Integer, nullable=False)
    format = db.Column(db.Text)
    name = db.Column(db.Text)

class Tags(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

class BooksTagsLink(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'books_tags_link'
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.Integer, nullable=False)
    tag = db.Column(db.Integer, nullable=False)

class AuthorsBooksLink(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'books_authors_link'
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.Integer, nullable=False)
    author = db.Column(db.Integer, nullable=False)

class Comments(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

class Languages(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    lang_code = db.Column(db.Text, nullable=False)

class BooksLanguagesLink(db.Model):
    __bind_key__ = 'booksdb'
    __tablename__ = 'books_languages_link'
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.Integer, nullable=False)
    lang_code = db.Column(db.Integer, nullable=False)
    

############
# Routes
############
@app.route('/')
def index():
    random_book = random.choice(Books.query.all())
    return render_template('index.html',
                           random_id = random_book.id,
                           random_title = Books.query.filter_by(id=random_book.id).first().title
                           )

@app.route('/authors')
def authors():
    books_inventory = {}
    ids_list = [x.id for x in Authors.query.all()]
    for id in ids_list:
        books_inventory[id] = len(AuthorsBooksLink.query.filter_by(author=id).all())
    return render_template('authors.html',
                           author_objs_list = Authors.query.all(),
                           books_inventory = books_inventory
                          )

@app.route('/authors/<author_id>/<author_name>')
def author_page(author_id, author_name):
    return render_template('author_page.html',
                           author_id = author_id,
                           author_name = author_name,
                           book_objects_list = Books.query.filter(Books.author_sort.contains(author_name)).all()
                           )

@app.route('/books')
def all_books():
    return render_template('all_books.html',
                           books_obj_list = Books.query.all()
                           )

@app.route('/book/<book_id>/<book_title>')
def book_page(book_id, book_title):
    books_tags_obj_list = BooksTagsLink.query.filter_by(book=book_id).all()
    tags_numbers_list = [x.tag for x in books_tags_obj_list]
    tags_obj_list = [Tags.query.filter_by(id=x).first() for x in tags_numbers_list]
    authors_book_link_objs_list = AuthorsBooksLink.query.filter_by(book=book_id).all()
    authors_id_list = [x.author for x in authors_book_link_objs_list]
    author_objs_list = [Authors.query.filter_by(id=x).first() for x in authors_id_list]
    if book_title == Books.query.filter_by(id=book_id).first().title:
        return render_template('book_page.html',
                               book_id = book_id,
                               book_title = book_title,
                               book_object = Books.query.filter_by(id=book_id).first(),
                               author_objs_list = author_objs_list,
                               scaricabili_object_list = Data.query.filter_by(book=book_id).all(),
                               tags_obj_list = tags_obj_list,
                               comment = Comments.query.filter_by(book=book_id).first()
                               )
    else:
        return 'nope' #TODO insert 404 error

@app.route('/tags')
def all_tags():
    books_inventory = {}
    ids_list = [x.id for x in Tags.query.all()]
    for id in ids_list:
        books_inventory[id] = len(BooksTagsLink.query.filter_by(tag=id).all())
    return render_template('tags.html',
                           tags_obj_list = Tags.query.all(),
                           books_inventory = books_inventory
                          )

@app.route('/tags/<tag_id>/<tag_name>')
def tag_page(tag_id, tag_name):
    tags_books_obj_list = BooksTagsLink.query.filter_by(tag=tag_id).all()
    book_ids_list = [x.book for x in tags_books_obj_list]
    books_obj_list = [Books.query.filter_by(id=x).first() for x in book_ids_list]
    if tag_name == Tags.query.filter_by(id=tag_id).first().name:
        return render_template('tag_page.html',
                               tag_id = tag_id,
                               tag_name = tag_name,
                               books_obj_list = books_obj_list
                               )
    else:
        return 'lolnope2'

@app.route('/languages')
def languages():
    books_inventory = {}
    ids_list = [x.id for x in Languages.query.all()]
    for id in ids_list:
        books_inventory[id] = len(BooksLanguagesLink.query.filter_by(lang_code=id).all())
    return render_template('languages.html',
                           languages = Languages.query.all(),
                           books_inventory = books_inventory
                           )

@app.route('/language/<language_id>/<language_name>')
def language_page(language_id, language_name):
    book_ids_list = [x.book for x in BooksLanguagesLink.query.filter_by(lang_code=language_id).all()]
    book_objs_list = [Books.query.filter_by(id=x).first() for x in book_ids_list]
    return render_template('language_page.html',
                           language_id = language_id,
                           language_name = language_name,
                           book_objs_list = book_objs_list
                           )


#############
# Start app
#############
if __name__ == '__main__':
    manager.run()
