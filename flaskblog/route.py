from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, login_manager
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.model import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image



@app.route("/")
@app.route("/home")
def home():
    page = request.args.get(key = 'page', default = 1, type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page = 5, page = page)
    return render_template('home.html', posts = posts)


@app.route("/about")
def about():
    return render_template('about.html', title = 'About')

@app.route('/demo')
def demo():
    return render_template('demo.html', title = 'Demo')
# Note: The additional title could given via render_template function

@app.route('/register', methods = ['GET', 'POST'])
# methods: for activate the utility of the page
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in now.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsucessful. Please check email and password.', 'success')
    return render_template('login.html', title = 'Login', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture): 
    # hash picture name by random hex -< prevent the collision of pilename
    # keep the original extension
    # scale uploaded picture
    # save the image

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn


@app.route('/account', methods = ['GET', 'POST'])
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

    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account',
                            image_file = image_file, form = form)


@app.route('/post/new', methods = ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content  = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('The post has been created!', 'success')
        return redirect(url_for('home'))
    
    return render_template('create_post.html',
                           title = 'New Post',
                           form = form,
                           legend = 'New Post')     

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    # if not exist return 404 <-> the page dosen't exist
    return render_template('post.html', title = post.title, post = post)


@app.route('/post/<int:post_id>/update', methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) # http respons for forbidden route
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # since this post has been added in the database when it was created.
        # db.session.add() is no needed
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        # Set original data to the default value of the form
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',
                        title = 'Update Post',
                        form = form,
                        legend = 'Update Post')  


@app.route('/post/<int:post_id>/delete', methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) # http respons for forbidden route
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get(key = 'page', default = 1, type = int)
    user = User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(author = user)\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page = 5, page = page)
    return render_template('user_post.html', posts = posts, user = user)