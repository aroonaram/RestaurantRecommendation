from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username_id = db.Column(db.String(120), nullable=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    cluster = db.Column(db.Integer, nullable=True)
    backup1 = db.Column(db.String(60), nullable=True)
    reviews = db.relationship('Review', backref='author', lazy=True)
    resturantbyuser = db.relationship('ResturantByUser', backref='byuser', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"



class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    postalCode = db.Column(db.Integer, nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    stars = db.Column(db.Float, nullable=True)
    categories = db.Column(db.String(100), nullable=True)
    #date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='restname', lazy=True)
    hours = db.Column(db.String(100), nullable=True)
    attribute = db.Column(db.String(100), nullable=True)
    cluster = db.Column(db.Integer, nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    backup1 = db.Column(db.String(60), nullable=True)
    def __repr__(self):
        return f"Restaurant('{self.name}', '{self.id}','{self.categories}')"

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    business_id = db.Column(db.String(100), nullable=True)
    username_id = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rest_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    backup1 = db.Column(db.String(60), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    def __repr__(self):
        return f"Review('{self.content}', '{self.date_posted}')"

class ResturantByUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.String(100), nullable=True)
    username_id = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rest_id = db.Column(db.Integer, nullable=True)
    backup1 = db.Column(db.String(60), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    def __repr__(self):
        return f"ResturantByUser('{self.rest_id}', '{self.business_id}')"

class ResturantByRestaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Parentbusiness_id = db.Column(db.String(100), nullable=True)
    business_id = db.Column(db.String(120), nullable=True)
    name = db.Column(db.String(120), nullable=True)
    category = db.Column(db.String(120), nullable=True)
    Parentrest_id = db.Column(db.Integer, nullable=True)
    rest_id = db.Column(db.Integer, nullable=True)
    backup1 = db.Column(db.String(60), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    def __repr__(self):
        return f"ResturantByUser('{self.rest_id}', '{self.business_id}')"
