from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import pyodbc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc://flask_user:StrongPassword123@localhost/HorseApp?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'  # Required for session management

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# -------- Models --------
class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    
    def get_id(self):
        return str(self.user_id)  # Flask-Login expects the ID as a string

class Horse(db.Model):
    __tablename__ = 'Horses'
    horse_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    coat = db.Column(db.String(100), nullable=False)
    country_of_birth = db.Column(db.String(100), nullable=False)
    breeder = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Numeric(10,2), nullable=True)
    national_id = db.Column(db.String(50), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------- Authentication Routes --------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    
    login_user(user)
    return jsonify({"message": "Logged in successfully"}), 200

# -------- Add Horse Route (Protected) --------
@app.route('/add_horse', methods=['POST'])
@login_required
def add_horse():
    data = request.get_json()

    new_horse = Horse(
        name=data['name'],
        gender=data['gender'],
        date_of_birth=data['date_of_birth'],
        breed=data['breed'],
        coat=data['coat'],
        country_of_birth=data['country_of_birth'],
        breeder=data.get('breeder', None),
        price=data.get('price', None),
        national_id=data['national_id'],
        owner_id=int(current_user.get_id())  # Use the logged-in user's ID
    )
    
    db.session.add(new_horse)
    db.session.commit()
    return jsonify({"message": "Horse added successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
