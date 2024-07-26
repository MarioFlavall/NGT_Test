from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ngt:eaRiqJ5<Fod*i~Zp@34.89.74.186:5432/postgres'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["SQLALCHEMY_DATABASE_URI"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
# app.config['JWT_SECRET_KEY'] = path = os.environ["JWT_SECRET_KEY"]


db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class TickerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(6), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open = db.Column(db.Numeric(16, 6), nullable=False)
    high = db.Column(db.Numeric(16, 6), nullable=False)
    low = db.Column(db.Numeric(16, 6), nullable=False)
    close = db.Column(db.Numeric(16, 6), nullable=False)
    adj_close = db.Column(db.Numeric(16, 6), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

@app.route('/ticker_data/<int:ticker_data_id>', methods=['PUT'])
@jwt_required()
def update_ticker_data(ticker_data_id):
    data = request.get_json()
    ticker_data = TickerData.query.get_or_404(ticker_data_id)
    for key, value in data.items():
        if key != 'id':
            setattr(ticker_data, key, value)
    db.session.commit()
    return jsonify({'message': 'Ticker data updated'})
@app.route('/tickers', methods=['GET'])
@jwt_required()
def get_tickers():
    """Returns a list of unique ticker symbols"""
    tickers = TickerData.query.distinct(TickerData.ticker)
    update_ticker_data(1)
    return jsonify([ticker.ticker for ticker in tickers])

@app.route('/tickers/<string:ticker>', methods=['GET'])
@jwt_required()
def get_ticker_data(ticker):
    "Returns a list of ticker data for the specified ticker"
    ticker_data = TickerData.query.filter_by(ticker=ticker).all()
    return jsonify([data.to_dict() for data in ticker_data])


@app.route('/ticker_data/<int:ticker_data_id>', methods=['DELETE'])
@jwt_required()
def delete_item(ticker_data_id):
    ticker_data = TickerData.query.get_or_404(ticker_data_id)
    db.session.delete(ticker_data)
    db.session.commit()
    return jsonify({'message': 'Ticker data deleted'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
