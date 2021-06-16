from flask import Flask, url_for,redirect,jsonify, Response,request,render_template
from flask_pymongo import PyMongo
import pymongo
import json
from bson.objectid import ObjectId 
from wtforms import Form,StringField,validators

app = Flask(__name__)

try:
    mongo = pymongo.MongoClient(
        host = "localhost",
        port = 27017,
        serverSelectionTimeoutMS=1000)
    db = mongo.biblioteca
    mongo.server_info()
    print("connect to mongo...")
except:
    print("Error- can not connect to db")

@app.route("/")
def get_collections():
    collection = db.collection_names(include_system_collections=False)
    for collect in collection:
        print(collect)
    return render_template('home.html',collection = collection)

@app.route('/wishlist')
def get_wishlist():
  result = []
  try:
      results = list(db.wishlist.find())

      for book in results:
          result.append(list(db.books.find({"_id": ObjectId(book.get('id'))})))
      result = list(filter(lambda x: x!= [],result))
      for b in result:
          if b:
            b[0]["_id"] = str(b[0]["_id"])
      return render_template('wishlist.html',results = result)
  except:
      return render_template('wishlist.html',msg = 'Error-not found')

@app.route('/add_wishlist/<id>', methods=['GET', 'POST'])
def add_wishlist(id):
    try:
        result = list(db.wishlist.find({"id": id}))
        print(result)
        if result==[]:
            book = {
                'id':id
            }
            dbResponse = db.wishlist.insert_one(book)
            print('book was added...')
            return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))
    except:
        return Response(
            response=json.dumps({"message": "Error- cannot add book"}),
            status=500,
            mimetype="application/json")
    return redirect(url_for('dashboard'))

@app.route('/delete_wishlist/<id>',methods=['POST'])
def delete_wishlist(id):
    try:
        result = list(db.wishlist.find({"id": id}))
        print(result)
        dbResponse = db.wishlist.delete_one({"_id":ObjectId(result[0].get('_id'))})
        print('mergeeeee')
        return redirect(url_for('get_wishlist'))
    except:
        return Response(
            response= json.dumps({"message": "Error- cannot delete books"}),
            status=500,
            mimetype="application/json")

@app.route('/add_preferate/<id>', methods=['GET', 'POST'])
def add_preferate(id):
    try:
        result = list(db.preferate.find({"id": id}))
        print(result )
        if result == []:
            book = {
                'id':id
            }
            dbResponse = db.preferate.insert_one(book)
            print('book was added...')
            return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))
    except:
        return Response(
            response=json.dumps({"message": "Error- cannot add book"}),
            status=500,
            mimetype="application/json")
    return redirect(url_for('dashboard'))

@app.route('/preferate')
def get_preferate():
  result = []
  try:
      results = list(db.preferate.find())

      for book in results:
          result.append(list(db.books.find({"_id": ObjectId(book.get('id'))})))
      result = list(filter(lambda x: x != [], result))
      for b in result:
          b[0]["_id"] = str(b[0]["_id"])
      print(result)
      return render_template('preferate.html',results = result)
  except:
      return render_template('preferate.html',msg = 'Error-not found')

@app.route('/delete_preferate/<id>',methods=['POST'])
def delete_preferate(id):
    try:
        result = list(db.preferate.find({"id": id}))
        print(result)
        dbResponse = db.preferate.delete_one({"_id":ObjectId(result[0].get('_id'))})
        return redirect(url_for('get_preferate'))
    except:
        return Response(
            response= json.dumps({"message": "Error- cannot delete books"}),
            status=500,
            mimetype="application/json")



@app.route("/add",methods=['GET','POST'])
def create_user():
    
    try:
        form = CheForm(request.form)
        if request.method == 'POST' and form.validate():

            book = {
                "title":form.title.data,
                "author":form.author.data,
                "gen":form.gen.data,
                "an":form.an.data,
                "nume_editor":form.title.data,
                "rezumat":form.rezumat.data,

            }

            dbResponse = db.books.insert_one(book)
            print(dbResponse.inserted_id)
            return redirect(url_for('dashboard'))
        return render_template('add.html', form=form)
    except:
        print("error-Nu au fost introduse datele...")
        return Response(
            response= json.dumps({"message": "Error"}),
            status=500,
            mimetype="application/json")

@app.route('/books')
def get_all():

  try:
      results = list(db.books.find())
      for book in results:
          book["_id"] = str(book["_id"])
  
      return render_template('persons.html',results = results)    
  except:
      return render_template('persons.html',msg = 'Error-not found')


@app.route("/carte/<id>")
def carte(id):
    try:
        result = list(db.books.find({"_id":ObjectId(id)}))
        print(result)
        return render_template('person.html',result = result)
    except:
        return render_template('person.html',msg = 'Error-not found')

@app.route('/dashboard')
def dashboard():
  try:
      results = list(db.books.find())
      for book in results:
          book["_id"] = str(book["_id"])
      print(results)
      return render_template('dashboard.html',results = results)
  except:
      return Response(
            response= json.dumps({"message": "Error- cannot read books"}),
            status=500,
            mimetype="application/json")

class CheForm(Form):
    author = StringField('Author',[validators.Length(min =1,max=200)])
    title = StringField('Title',[validators.Length(min =1,max=200)])
    gen = StringField('Gen',[validators.Length(min =1,max=200)])
    an = StringField('An', [validators.Length(min=1, max=200)])
    nume_editor = StringField('Nume editor', [validators.Length(min=1, max=200)])
    rezumat = StringField('Rezumat', [validators.Length(min=1, max=1000)])



@app.route("/edit/<string:id>", methods = ['GET', 'POST'])
def update_book(id):
    try:
        result = list(db.books.find({"_id":ObjectId(id)}))
        print(result[0])
        print(result[0].get('title'))

        form = CheForm(request.form)
        form.author.data = result[0].get('author')
        form.title.data  = result[0].get('title')
        form.gen.data = result[0].get('gen')
        form.an.data = result[0].get('title')
        form.nume_editor.data = result[0].get('nume_editor')
        print("before")
        if request.method == 'POST':
            print('after')
            title       = request.form['title']
            author      = request.form['author']
            gen         = request.form['gen']
            an          = request.form['an']
            nume_editor = request.form['nume_editor']

            dbResponse = db.books.update_one(
                {"_id":ObjectId(id)},
                {"$set":{"title":title,"author": author,"gen": gen,"an": an,"nume_editor": nume_editor}}
            )
            return redirect(url_for('dashboard'))
        return render_template('edit.html', form=form)
    except:
        return Response(
            response= json.dumps({"message": "Error- cannot update books"}),
            status=500,
            mimetype="application/json")

@app.route('/delete/<id>',methods=['POST'])
def delete(id):
    try:
        dbResponse = db.books.delete_one({"_id":ObjectId(id)})
        return redirect(url_for('dashboard'))
    except:
        return Response(
            response= json.dumps({"message": "Error- cannot delete books"}),
            status=500,
            mimetype="application/json")

if __name__=='__main__':
    app.run(debug=True)

