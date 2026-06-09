from flask import Blueprint, request, jsonify
from database import db
from models import Event
from routes.auth import get_current_user
from datetime import datetime

catalog_bp = Blueprint('catalog', __name__)


# GET /api/catalog/events
@catalog_bp.route('/events', methods=['GET'])
def list_events():
    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = Event.query

    if category:
        query = query.filter(Event.category == category)
    if date_from:
        try:
            df = datetime.fromisoformat(date_from)
            query = query.filter(Event.date >= df)
        except ValueError:
            return jsonify({'error': 'Invalid date_from format, use ISO 8601'}), 400
    if date_to:
        try:
            dt = datetime.fromisoformat(date_to)
            query = query.filter(Event.date <= dt)
        except ValueError:
            return jsonify({'error': 'Invalid date_to format, use ISO 8601'}), 400

    events = query.order_by(Event.date).all()
    return jsonify({'events': [e.to_dict() for e in events], 'total': len(events)}), 200


# GET /api/catalog/events/<id>
@catalog_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify({'event': event.to_dict()}), 200


# POST /api/catalog/events  (admin only)
@catalog_bp.route('/events', methods=['POST'])
def create_event():
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden: admin only'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['title', 'category', 'date', 'venue', 'price', 'seats_total']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        event_date = datetime.fromisoformat(data['date'])
    except ValueError:
        return jsonify({'error': 'Invalid date format, use ISO 8601'}), 400

    seats = int(data['seats_total'])
    event = Event(
        title=data['title'],
        category=data['category'],
        date=event_date,
        venue=data['venue'],
        price=float(data['price']),
        seats_total=seats,
        seats_available=data.get('seats_available', seats),
        description=data.get('description', '')
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'message': 'Event created', 'event': event.to_dict()}), 201


# PUT /api/catalog/events/<id>  (admin only)
@catalog_bp.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden: admin only'}), 403

    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    data = request.get_json() or {}
    if 'title' in data:
        event.title = data['title']
    if 'category' in data:
        event.category = data['category']
    if 'date' in data:
        try:
            event.date = datetime.fromisoformat(data['date'])
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    if 'venue' in data:
        event.venue = data['venue']
    if 'price' in data:
        event.price = float(data['price'])
    if 'seats_total' in data:
        event.seats_total = int(data['seats_total'])
    if 'seats_available' in data:
        event.seats_available = int(data['seats_available'])
    if 'description' in data:
        event.description = data['description']

    db.session.commit()
    return jsonify({'message': 'Event updated', 'event': event.to_dict()}), 200


# DELETE /api/catalog/events/<id>  (admin only)
@catalog_bp.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden: admin only'}), 403

    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'}), 200
