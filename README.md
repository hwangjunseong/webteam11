ERD
<img width="312" alt="image" src="https://github.com/user-attachments/assets/49ada7ff-ea87-4c01-bfdb-0fa5b5a16a5f">

DB : Mysql

API 설계 
사용자에 대한 CRUD , LOGIN, LOGOUT
크롤링 : 미리 정해놓은 category인 스포츠 , 음악, 주식에 대해 BeautifulSoup 라이브러리를 사용하여 해당 naver 기사 크롤링
크로링한 내용 전부 삭제, 개별 삭제
포스트의 add_crawlpost : 크롤링한 데이터를 바탕으로 Categories 테이블에 있던 내용을 Posts 테이블로 그대로 전달
포스트 삭제, 포스트 편집, 포스트 전체 읽기, 개별 읽기
검색 : 포스트의 content에 사용자가 입력한 내용이 들어있다면 해당 포스트 보여줌
유효성 검사 : flask의 wtforms
서버 안에 있는 이미지 폴더에 이미지 저장

인증 방식
LoginManager :  Flask 애플리케이션에 로그인 기능을 추가하고, 현재 사용자의 인증 상태를 추적

ORM : SQLAlchemy
데이터베이스의 테이블과 Python의 클래스를 매핑하여 객체 지향적인 방식으로 데이터베이스 작업
SQLAlchemy의 세션: 데이터베이스 트랜잭션을 관리하는 역할
db.session.commit()은 현재 세션에 존재하는 모든 변경 사항을 트랜잭션 단위로 커밋하여 데이터베이스에 반영
서버가 로그인 상태를 저장함

Table 설계, 관계 설정
Users의 한명의 사용자가 여러 Posts를 가질 수 있음 => 1:N 관계
Users의 한명의 사용자가 여러 Categories를 가질 수 있음 =>  1:N 관계

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added= db.Column(db.DateTime,  default=func.now())
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref = 'poster')
    categories = db.relationship('Categories', backref = 'categorier')

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=func.now())
    category = db.Column(db.String(255)) #category
    url =  db.Column(db.String(255))
    post_pic = db.Column(db.String(255), nullable=True)
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
