from flask import Flask
from flask_cors import CORS
from database import db
from models import User, Event, Booking, Payment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/ticketbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ticketbook-secret-key-for-testing'

CORS(app, resources={r"/api/*": {"origins": "*"}})
db.init_app(app)

from routes.auth import auth_bp
from routes.catalog import catalog_bp
from routes.booking import booking_bp
from routes.payment import payment_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(catalog_bp, url_prefix='/api/catalog')
app.register_blueprint(booking_bp, url_prefix='/api/booking')
app.register_blueprint(payment_bp, url_prefix='/api/payment')


@app.route('/api/health')
def health():
    return {'status': 'ok', 'service': 'TicketBook API v1.0'}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from seed import seed_data
        seed_data()
    app.run(host='0.0.0.0', port=5000, debug=False)
