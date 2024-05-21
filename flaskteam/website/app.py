from flask import Flask, render_template, flash, request, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.sql import func
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
import requests
from bs4 import BeautifulSoup

from werkzeug.utils import secure_filename
import uuid as uuid
import os

#create a flask instance
app =Flask(__name__)
#add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:wktong6877@localhost:3307/our_users_database'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#secret key
app.config['SECRET_KEY'] = "abcd"

#저장할 폴더이름
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] =UPLOAD_FOLDER

#initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.init_app(app)
#혹은 콘솔에 flask db init치기

#flask login stuff
login_manager = LoginManager()
login_manager.init_app(app)
# 사용자가 로그인되지 않은 상태에서 접근을 시도할 때 리디렉션될 로그인 화면의 URL을 지정 -> /login
login_manager.login_view ="login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#create model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)#nullable=False -> 공백없음
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added= db.Column(db.DateTime,  default=func.now())
    # date_added= db.Column(db.DateTime, default=datetime.utcnow)
    #do some password stuff
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref = 'poster')
    categories = db.relationship('Categories', backref = 'categorier')

    #post에서는 poster라는 이름을 사용해서 user객체에 접근할수있다 poster.id -> user.id와 동일

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    #password 일치하는지 확인

    #password 입력한거 가져와서 hash함수적용해서 비밀번호를 해시로 변환
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    #password 확인
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    #create a string
    def __repr__(self):
        return '<Name %r>' %self.name


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=func.now())
    category = db.Column(db.String(255)) #category
    url =  db.Column(db.String(255))
    post_pic = db.Column(db.String(255), nullable=True)
    #create foreign key to link users -> users의 id -> 한명의 유저가 여러가지 post 가지기 가능 
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
class Categories(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=func.now())
    category=db.Column(db.String(255))
    url =  db.Column(db.String(255))
    category_pic = db.Column(db.String(255), nullable=True)
    categorier_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#title content date_posted_ category url current user id

#create form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("UserName", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash= PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("submit")


class CrawlPostForm(FlaskForm):
    title = StringField("Enter your Title", validators=[DataRequired()])
    submit = SubmitField("submit")

class PostForm(FlaskForm):
            #title content date_posted category url

    title = StringField("What is your Title", validators=[DataRequired()])
    content = StringField("What is your Content", validators=[DataRequired()], widget = TextArea())
    category = StringField("What is your Category", validators=[DataRequired()])
    submit = SubmitField("submit")

class LoginForm(FlaskForm):
    username=StringField("Username", validators=[DataRequired()])
    password=PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("submit")
 
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("submit")




#navbar에 있는 csrf토큰이 form 인자로 전달되지않아서 base.html에 인자로 전달해줌
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

#create search function
@app.route('/search', methods=['POST', 'GET'])
def search():
    
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        #submit form으로 부터 데이터 받아옴
        post.searched = form.searched.data
        #query the database
        #content 내용 filter함
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched = post.searched , posts = posts)
    else:
        return redirect(url_for('index'))




#add post page -> 크롤링한 데이터를 바탕으로
@app.route('/add_crawlpost', methods=['POST', 'GET'])
@login_required
def add_crawlpost():
    #categories 데이터 베이스로 부터 정보가져옴
    #title 만 가져와서 title 해당하는 게 있으면 포스터 만든다
    form = CrawlPostForm()
    #add post에 지금 categories 데이터베이스에 들어있는 title 다 for문으로 돌려서 출력
    #form에는 title 정도만 입력하게 한다
    
    if form.validate_on_submit():
        OldCategory = Categories.query.filter_by(title=form.title.data).first()
        #입력한 title이 있는건지 확인
        if OldCategory is None:
            flash("input title is not exist")
            return redirect(url_for('add_crawlpost'))

        else:
            #poster은 user의 id
            poster = current_user.id
            #title content category url
            #title content date_posted category url

            post = Posts(title = OldCategory.title, content = OldCategory.content, category = OldCategory.category, url = OldCategory.url,post_pic =OldCategory.category_pic, poster_id = poster)
            #양식 초기화
            form.title.data = ''
            
            db.session.add(post)
            db.session.commit()
            flash('Blog Post Submitted Successfully')
    #addcrawl post에 categoriest 다전달해야함
    categories = Categories.query.order_by(Categories.date_posted.desc())
    return render_template('add_crawlpost.html',categories = categories,form = form, current_user = current_user)

@app.route('/delete_categories/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_categories(id):
    user_to_delete = Users.query.get_or_404(id)
        
    # 사용자와 관련된 카테고리 삭제
    for category in user_to_delete.categories:
        # 카테고리와 관련된 이미지 파일이 포스트에 없을 때만 삭제
        post_exist = Posts.query.filter_by(post_pic=category.category_pic).first()
        if category.category_pic and post_exist is None:
            file_path = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'], category.category_pic)
            if os.path.exists(file_path):
                os.remove(file_path)
              
     
        db.session.delete(category)
    db.session.commit()
    flash("All categories have been removed!")

    return redirect(url_for('add_crawlpost'))


@app.route('/delete_category/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_category(id):
    category_to_delete = Categories.query.get_or_404(id)
    post_exist = Posts.query.filter_by(post_pic=category_to_delete.category_pic).first()
    
    id = current_user.id

    # category id -> user의 id와 일치하는 id만 delete할수있다
    if id == category_to_delete.categorier_id:

        try:
            #post에 pic없는거만 사진 삭제
            if category_to_delete.category_pic and post_exist is None:
              
                file_path = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'], category_to_delete.category_pic)
                if os.path.exists(file_path):
                    os.remove(file_path)
  
            db.session.delete(category_to_delete)
            db.session.commit()
            flash("Category deleted successfully")
            return redirect(url_for('add_crawlpost'))
        

        except:
            flash("Category deleted failed, try again ")
            return redirect(url_for('add_crawlpost'))
    else:
        flash("Your are not authorized to delete that category")
        return redirect(url_for('add_crawlpost'))


 #show post
@app.route('/posts')
def posts():
    #데이터베이스로부터 모든 포스트 grab -> 날짜순 정렬된거 기준으로
    posts = Posts.query.order_by(Posts.date_posted.desc())

    return render_template("posts.html", posts=posts)

#개인의 post id로 블로그 봄
@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)

    
    return render_template("post.html", post=post)


#post편집
@app.route("/posts/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = form.category.data
        post.content = form.content.data
        #update data base
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        #redirect(url_for 안에는 함수이름이 들어간다
        #`url_for`함수는 엔드포인트 함수명을 인자로 받는다. 따라서 이동하고자 하는 라우트의 함수 이름을 url_for() 내에 적어줘야한다. 
        return redirect(url_for('post', id=post.id))
        # return redirect(url_for('malu', id=post.id))
    if current_user.id == post.poster_id:
        form.title.data = post.title
        form.category.data = post.category
        form.content.data = post.content
        return render_template('edit_post.html',form=form)
    else:
        flash("Your are not authorized to edit this post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


#post삭제
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
   
    id = current_user.id
    # poster id -> user의 id와 일치하는 id만 delete할수있다
    if id == post_to_delete.poster_id:

        try:
            if post_to_delete.post_pic:
                file_path = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'], post_to_delete.post_pic)
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post deleted successfully")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            flash("Post deleted failed, try again ")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("Your are not authorized to delete that post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)





@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        #데이터 베이스에 똑같은 이메일이 있는지 확인한다 이메일은 고유해야한다
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            #고유하다면 데이터배이스에 추가
            user = Users(name=form.name.data,username = form.username.data, email = form.email.data, password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
         
        name = form.name.data
        #초기화
        form.name.data = ''
        form.username.data=''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User added Successfully")
    
    return render_template('add_user.html', form=form, name = name)    

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User updated successfully")
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            flash("User updated failed")
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id = id)



@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        #기존 user가 가지고 있던 category랑 posts 싹 다 없애고 난 뒤 user delete해줘야 함
        # 사용자와 관련된 포스트 삭제
        for post in user_to_delete.posts:
            db.session.delete(post)

        # 사용자와 관련된 카테고리 삭제
        for category in user_to_delete.categories:
            # 카테고리와 관련된 이미지 파일 삭제
            if category.category_pic:
                file_path = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'], category.category_pic)
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.session.delete(category)

        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully")
        our_users = Users.query.order_by(Users.date_added).all()
        return render_template('add_user.html', form=form, name = name, our_users = our_users)

    except:
        flash("User deleted failed")
        return render_template('add_user.html', form=form, name = name, our_users = our_users)



#url_for에 함수이름 전달
@app.route('/')
def index():
    
    return render_template('index.html')
def start_crawling(category_url, category_name):
    response = requests.get(category_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    announcements = []

    news_articles = soup.select('ul.list_news._infinite_list > li.bx')


       

    for article in news_articles:
        title = article.select_one('a.news_tit').text
        url = article.select_one('a.news_tit')['href']
        content = article.select_one('a.api_txt_lines.dsc_txt_wrap').text
        pic = article.select_one('a.dsc_thumb img')
    
        # 이미지 URL을 가져오는 부분을 조건문으로 감싸서 'NoneType' 객체가 아닌 경우에만 이미지 URL을 가져오도록 함
        if pic is not None and pic.get('data-lazysrc') is not None:
            img_url = pic['data-lazysrc']
        else:
            img_url = ""

        announcements.append({'title': title, 'url': url, 'content': content, 'img_url': img_url})






    #유효성 검사 title, url, content category 중 none없어야함
    for  ann in announcements:
        if ann['title']=='' or ann['url'] =='' or ann['content']=='' or ann['img_url']==''or category_name is None:
            flash('ann empty error') 
        else:
            #title이 데이터 베이스에 동일한게 존재하는지 확인하고 없다면 넣는다
            categorier = current_user.id
            oldcategory = Categories.query.filter_by(title=ann['title'], categorier_id = categorier).first()

            if oldcategory is None:
            #고유하다면 데이터배이스에 추가 category title content url
           
                #title content date_posted_ category url current user id

                response_img = requests.get(ann['img_url'])
                response_img.raise_for_status()

                upload_folder = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
                #Grab image name
                pic_filename = secure_filename(category_name)+ '.png'
                #set uuid
                pic_name = str(uuid.uuid1()) + '_'+pic_filename
                #save the image
                
                pic_path = os.path.join(upload_folder, pic_name)
                with open(pic_path, 'wb') as f:
                    f.write(response_img.content)
             

                category = Categories( title = ann['title'], content = ann['content'] , category = category_name, url = ann['url'] ,category_pic = pic_name , categorier_id = categorier)
                db.session.add(category)
                db.session.commit()







  
@app.route('/crawling' , methods=['GET', 'POST'])
def crawling():
    
    if request.method == 'POST':
        category_name = request.form.get('category')
        if category_name == "Choose...":
            flash("Choose anything except this category")
        else:
            flash(f'Your Category is {category_name}!') 
            #여기에서 카테고리에 따른 search할꺼임 -> 정보 뽑고 카테코리 데이터베이스에 저장할꺼임
            url = {
                'Stock': 'https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query=%EC%A3%BC%EC%8B%9D',
                'Sport': 'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&ssc=tab.news.all&query=%EC%8A%A4%ED%8F%AC%EC%B8%A0&oquery=%EC%95%BC%EA%B5%AC&tqi=iBGz%2BdpzL8VssFnYRF0ssssstts-197829',
                'Music':  'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&ssc=tab.news.all&query=%EC%9D%8C%EC%95%85&oquery=%EC%A3%BC%EC%8B%9D&tqi=iBd0bwqpsECsstqwpshssssssLl-167263',
            }
            category_url = url[category_name]
            start_crawling(category_url, category_name)
    return render_template('crawling.html')



#create login page
@app.route('/login',methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #username = form.username.data , first()-> 방금전에 submit버튼에다가 username적은거 가져옴
        user = Users.query.filter_by(username = form.username.data).first()
        #username은 unique해서 하나만 존재
        if user:
            #check the hash
            if check_password_hash(user.password_hash, form.password.data):
                #비밀번호와 데이터베이스에 있는 해쉬된 비밀번호가 일치
                #로그인한고 세션을 생성해준다
                login_user(user)
                flash("Login successful")
                #dashboard함수로 redirect
                return redirect(url_for('dashboard'))
            else:
                #form에 입력한 password와 database에 있는 비밀번호가 틀렸습니다
                flash("Wrong password- try again")
        else:
            #user가 없을경우
            flash("That User does not exist")

    return render_template('login.html',form =form)

#create logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    #login함수로 redierect
    return redirect(url_for('login'))
#create dashboard page
@app.route('/dashboard',methods=['GET', 'POST'])
@login_required
def dashboard():
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User updated successfully")
            return render_template('dashboard.html')
        except:
            flash("User updated failed")
            return render_template('dashboard.html')
    else:
        return render_template('dashboard.html')
   


#invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500



if __name__ == '__main__':


    app.run(debug=True)
