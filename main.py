from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap(app)


# We can use the SQlAlchemy to also create the data base instead of using the sqlite3 as we have above
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') #"sqlite:///movie-collection.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    # # The code below is used to print out the title with the data stored in the class
    # def __repr__(self):
    #     return f'<Movies {self.title}>'


# This creates the database and prepare it for coming data
db.create_all()

all_movies = []


# Using the flask-wtf to create form
class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class addMovie(FlaskForm):
    add = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField('Add Movie')


@app.route("/")
def home():
    # This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/edit', methods=['GET', 'POST'])
def rate_movie():
    form = RateMovieForm()
    # Singling out the current movie based on the id of the movie
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", movie=movie, form=form)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = addMovie()
    if form.validate_on_submit():
        url = f"https://api.themoviedb.org/3/search/movie"
        parameters = {
            'api_key': 'cb3667269fb6fbf10bc31d163e2cc571',
            'query': form.add.data,
        }
        response = requests.get(url=url, params=parameters)
        data = response.json()['results']

        return render_template('select.html', movie_data=data)
    return render_template('add.html', form=form)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/findMovie')
def find_movie():
    movie_id = request.args.get('id')
    if movie_id:
        image_url = "https://image.tmdb.org/t/p/w500"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        parameters = {
            'api_key': 'cb3667269fb6fbf10bc31d163e2cc571',
            "language": "en-US"
        }
        response = requests.get(url=url, params=parameters)
        data = response.json()

        new_movie = Movie(title=data['title'],
                          year=data['release_date'].split('-')[0],
                          description=data['overview'],
                          img_url=f'{image_url}{data["poster_path"]}')

        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('rate_movie', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
