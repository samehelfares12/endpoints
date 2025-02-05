from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# إنشاء التطبيق
app = Flask(__name__)

# إعدادات الاتصال بقاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://flaskuser:StrongPassword123@DESKTOP-JV0T64E/db?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء كائن db للتعامل مع قاعدة البيانات
db = SQLAlchemy(app)

# تعريف الـ Model (الجداول) فقط إذا لم تكن موجودة بالفعل في قاعدة البيانات

class User(db.Model):
    __tablename__ = 'users'
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    PhoneNumber = db.Column(db.String(15), unique=True)
    ProfilePicture = db.Column(db.String(255))

    horses = db.relationship('Horse', backref='owner', lazy=True)
    health_records = db.relationship('HealthRecord', backref='vet', lazy=True)
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    sent_messages = db.relationship('Chat', foreign_keys='Chat.SenderID', backref='sender', lazy=True)
    received_messages = db.relationship('Chat', foreign_keys='Chat.ReceiverID', backref='receiver', lazy=True)
    appointments = db.relationship('VetAppointment', backref='vet', lazy=True)

class Horse(db.Model):
    __tablename__ = 'horses'
    HorseID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Breed = db.Column(db.String(100))
    FatherID = db.Column(db.Integer, db.ForeignKey('horses.HorseID'))
    MotherID = db.Column(db.Integer, db.ForeignKey('horses.HorseID'))
    DateOfBirth = db.Column(db.Date)
    HealthStatus = db.Column(db.String(255))
    Achievements = db.Column(db.Text)
    OwnerID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    ProfilePicture = db.Column(db.String(255))

    health_records = db.relationship('HealthRecord', backref='horse', lazy=True)
    posts = db.relationship('Post', backref='horse', lazy=True)
    appointments = db.relationship('VetAppointment', backref='horse', lazy=True)
    certificates = db.relationship('Certificate', backref='horse', lazy=True)

class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    HealthRecordID = db.Column(db.Integer, primary_key=True)
    HorseID = db.Column(db.Integer, db.ForeignKey('horses.HorseID'), nullable=False)
    Date = db.Column(db.Date, default=datetime.utcnow)
    Details = db.Column(db.Text, nullable=False)
    VetID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)

class Post(db.Model):
    __tablename__ = 'posts'
    PostID = db.Column(db.Integer, primary_key=True)
    HorseID = db.Column(db.Integer, db.ForeignKey('horses.HorseID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    Content = db.Column(db.Text, nullable=False)
    MediaURL = db.Column(db.String(255))
    VoiceNoteURL = db.Column(db.String(255))
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    CommentID = db.Column(db.Integer, primary_key=True)
    PostID = db.Column(db.Integer, db.ForeignKey('posts.PostID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    Content = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    __tablename__ = 'likes'
    LikeID = db.Column(db.Integer, primary_key=True)
    PostID = db.Column(db.Integer, db.ForeignKey('posts.PostID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class Chat(db.Model):
    __tablename__ = 'chat'
    ChatID = db.Column(db.Integer, primary_key=True)
    SenderID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    ReceiverID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    Message = db.Column(db.Text, nullable=False)
    SentAt = db.Column(db.DateTime, default=datetime.utcnow)
    Seen = db.Column(db.Boolean, default=False)

class VetAppointment(db.Model):
    __tablename__ = 'vet_appointments'
    AppointmentID = db.Column(db.Integer, primary_key=True)
    HorseID = db.Column(db.Integer, db.ForeignKey('horses.HorseID'), nullable=False)
    VetID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    AppointmentDate = db.Column(db.DateTime, nullable=False)
    Reason = db.Column(db.Text, nullable=False)
    Status = db.Column(db.String(50), default='Pending')

class Certificate(db.Model):
    __tablename__ = 'certificates'
    CertificateID = db.Column(db.Integer, primary_key=True)
    HorseID = db.Column(db.Integer, db.ForeignKey('horses.HorseID'), nullable=False)
    IssuedDate = db.Column(db.Date, default=datetime.utcnow)
    CertificateType = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    DocumentURL = db.Column(db.String(255))



# تعريف الـ route لإضافة بيانات جديدة في جدول الـ users
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    print(data)  # تأكد من البيانات اللي جايه من Postman

    required_fields = ['name', 'email', 'password', 'phone_number', 'profile_picture']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "All fields are required: name, email, password, phone_number, profile_picture"}), 400

    existing_user = User.query.filter_by(Email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email already exists"}), 400

    new_user = User(
        Name=data['name'],
        Email=data['email'],
        Password=data['password'],  # تأكد من تشفير كلمة المرور عند الاستخدام الفعلي
        PhoneNumber=data['phone_number'],
        ProfilePicture=data['profile_picture']
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User added successfully!",
        "user": {
            "name": new_user.Name,
            "email": new_user.Email,
            "phone_number": new_user.PhoneNumber,
            "profile_picture": new_user.ProfilePicture
        }
    }), 201

# تعريف الـ route للتحقق من بيانات تسجيل الدخول
@app.route('/login', methods=['GET'])
def login():
    # الحصول على البيانات من الاستعلام (query parameters)
    email = request.args.get('email')
    password = request.args.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # البحث عن المستخدم بناءً على البريد الإلكتروني
    user = User.query.filter_by(Email=email).first()

    # إذا لم يتم العثور على المستخدم
    if not user:
        return jsonify({"message": "User not found"}), 404

    # تحقق من كلمة المرور (تأكد من مقارنة كلمات المرور بشكل آمن في الإنتاج)
    if user.Password != password:
        return jsonify({"message": "Invalid password"}), 401

    # إذا تم التحقق من البيانات بنجاح
    return jsonify({
        "message": "Login successful",
        "user": {
            "name": user.Name,
            "email": user.Email,
            "phone_number": user.PhoneNumber,
            "profile_picture": user.ProfilePicture
        }
    }), 200


# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)