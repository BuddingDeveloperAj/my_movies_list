from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
api_key = "YOUR API KEY"


##SQL DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my-movies-list.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String(750), unique=True, nullable=False)
    rating = db.Column(db.Float, default=None)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)
    img_url = db.Column(db.String(250), unique=True, nullable=False)


db.create_all()


##FORM

class EditingForm(FlaskForm):
    rating = StringField('Your rating out of 10')
    review = StringField('Your review')
    submit = SubmitField('Submit')


class AddMovie(FlaskForm):
        new_movie = StringField('Movie Title')
        submit = SubmitField('Add movie')


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    all_movies = Movie.query.order_by(Movie.ranking).all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    editing_form = EditingForm()
    if editing_form.validate_on_submit():
        movie.rating = float(editing_form.rating.data)
        movie.review = editing_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=editing_form, movie=movie)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["POST", "GET"])
def add_movie():
    add_form = AddMovie()
    if add_form.validate_on_submit():
        response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={api_key}"
                               f"&language=en-US&query={add_form.new_movie.data}&page=1&include_adult=false").json()
        all_details = response["results"]

        return render_template('select.html', results=all_details)
    return render_template('add.html', form=add_form)


@app.route("/movie")
def get_movie():
    movie_id = request.args.get("id")
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?"
                            f"api_key={api_key}&language=en-US").json()
    new_movie = Movie(title=response["title"],
        year=response["release_date"][:4],
        description=response["overview"],
        img_url=f"https://image.tmdb.org/t/p/w300_and_h450_bestv2{response['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit", id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)

