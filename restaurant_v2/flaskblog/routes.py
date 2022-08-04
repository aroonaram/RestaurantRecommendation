from crypt import methods
import os
import secrets
import uuid
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, RestaurantForm, ReviewForm, SearchForm
from flaskblog.models import User, Restaurant, Review, ResturantByUser
from flask_login import login_user, current_user, logout_user, login_required



@app.route("/")
@app.route("/home")
def home():
    #restaurants = Restaurant.query.all()
    #return render_template('home.html', restaurants=restaurants)
    page = request.args.get('page',1,type=int)
    restaurants = Restaurant.query.paginate(page=page,per_page= 5)
    similarbyUser = ResturantByUser.query.filter_by(username_id = '6_SpY41LIHZuIaiDs5FMKA')
    if current_user.is_authenticated:
        user = User.query.filter_by(username = current_user.username)
        #print('Hello',current_user.username_id)
        similarbyUser = ResturantByUser.query.filter_by(username_id = current_user.username_id)
    #similarbyUser = ResturantByUser.query.filter_by(username_id = user.username_id)
    #similarbyUser = ResturantByUser.query.filter_by(username_id = '6_SpY41LIHZuIaiDs5FMKA')
    businessList = []
    i = 0
    for x in similarbyUser:
        lst = []
        val = Restaurant.query.filter_by(business_id = x.business_id).one()
        #print(val.name, type(val.name))
        lst.append(val.name)
        lst.append(val.id)
        lst.append(val.categories)
        businessList.append(lst)

    return render_template('home.html', restaurants=restaurants,similarbyUser=businessList)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #username_id = form.username.data.encode("utf-16")
        username_id = uuid.uuid4().hex
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,username_id= username_id)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/restaurant/new", methods=['GET', 'POST'])
@login_required
def new_restaurant():
    form = RestaurantForm()
    if form.validate_on_submit():
        restaurant = Restaurant(name=form.name.data, 
        cuisine=form.cuisine.data,
        postalCode= form.postalCode.data,
        lat = form.lat.data,
        lon = form.lon.data,
        hours = form.hours.data,
        categories = form.categories.data)
        db.session.add(restaurant)
        db.session.commit()
        flash('New restaurant added!', 'success')
        return redirect(url_for('home'))
    return render_template('create_restaurant.html', title='New Restaurant',
                           form=form, legend='New Post')

@app.route("/restaurant/<int:restaurant_id>")
def restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    reviews = Review.query.filter_by(rest_id=restaurant.id)
    return render_template('restaurant.html', title=restaurant.name, restaurant=restaurant, reviews=reviews)

@app.route("/restaurant/<int:restaurant_id>/write_review", methods=['GET', 'POST'])
@login_required

def write_review(restaurant_id):
    restid = restaurant_id
    form = ReviewForm()
    user = User.query.filter_by(username = current_user.username)
    rest = Restaurant.query.filter_by(id=restid)
    for r in rest:
        Review.business_id = r.business_id
    for u in user:
        Review.username_id = u.username_id
        Review.user_id = u.id    
    if form.validate_on_submit():
        review = Review(
        rating=form.rating.data, 
        content=form.content.data,
        author= current_user,
        rest_id= restid,
        review_id = uuid.uuid4().hex
        #business_id = business_id
        #username_id = username_id
        #user_id = user_id
        )

        db.session.add(review)
        db.session.commit()
        flash('New review added!', 'success')
        return redirect(url_for('restaurant', restaurant_id=restaurant_id))
    return render_template('write_review.html',title='New review',form=form, legend='New review',user = user,rest=rest)

@app.route("/restaurant/<int:restaurant_id>/similar_restaurants", methods=['GET', 'POST'])
def similar_restaurants(restaurant_id):
    #current_restaurant = Restaurant.query.get_or_404(restaurant_id)
    similar_restaurants = Restaurant.query.all()
    return render_template('similar_restaurants.html', restaurants=similar_restaurants)

# pass stuff to nav bar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Search function
@app.route("/search",methods = ["POST"])
def search():
    form = SearchForm()
    
    if form.validate_on_submit():
        restaurant.searched = form.searched.data
        restaurant.searched = Restaurant.query.filter_by(postalCode = restaurant.searched)
        return render_template("search.html",form=form,searched=form.searched.data, restaurants = restaurant.searched )