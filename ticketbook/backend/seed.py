from database import db
from models import User, Event
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def seed_data():
    if not User.query.filter_by(email='user@test.com').first():
        db.session.add(User(
            email='user@test.com',
            password_hash=generate_password_hash('Test1234!'),
            name='Test User',
            role='user'
        ))

    if not User.query.filter_by(email='admin@test.com').first():
        db.session.add(User(
            email='admin@test.com',
            password_hash=generate_password_hash('Admin1234!'),
            name='Admin User',
            role='admin'
        ))

    if Event.query.count() == 0:
        events = [
            Event(id=1, title='Рок-концерт: Ночные Снайперы', category='concert',
                  date=datetime.utcnow() + timedelta(days=10), venue='Stadium Live, Москва',
                  price=2500.0, seats_total=500, seats_available=250,
                  description='Легендарный рок-концерт'),
            Event(id=2, title='Балет: Лебединое озеро', category='theater',
                  date=datetime.utcnow() + timedelta(days=15), venue='Большой театр, Москва',
                  price=5000.0, seats_total=300, seats_available=120,
                  description='Классический балет Чайковского'),
            Event(id=3, title='Кино: Дюна 3', category='cinema',
                  date=datetime.utcnow() + timedelta(days=3), venue='Кинотеатр Октябрь',
                  price=800.0, seats_total=150, seats_available=80,
                  description='Продолжение эпической саги'),
            Event(id=4, title='Джазовый вечер', category='concert',
                  date=datetime.utcnow() + timedelta(days=7), venue='Клуб Эссе, Санкт-Петербург',
                  price=1500.0, seats_total=100, seats_available=45,
                  description='Живой джаз в уютной атмосфере'),
            Event(id=5, title='Спектакль: Гамлет', category='theater',
                  date=datetime.utcnow() + timedelta(days=20), venue='МХТ им. Чехова',
                  price=3500.0, seats_total=400, seats_available=200,
                  description='Шекспировская трагедия в современной постановке'),
        ]
        for e in events:
            db.session.add(e)

    db.session.commit()
    print('[seed] Test data loaded.')
