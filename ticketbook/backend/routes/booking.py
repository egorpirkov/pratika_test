from flask import Blueprint, request, jsonify
from database import db
from models import Booking, Event
from routes.auth import get_current_user
from datetime import datetime

booking_bp = Blueprint('booking', __name__)


# POST /api/booking/create
@booking_bp.route('/create', methods=['POST'])
def create_booking():
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    event_id = data.get('event_id')
    if event_id is None:
        return jsonify({'error': 'event_id is required'}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    if event.seats_available <= 0:
        return jsonify({'error': 'No seats available'}), 409

    booking = Booking(
        user_id=user.id,
        event_id=event.id,
        status='pending'
    )
    event.seats_available -= 1
    db.session.add(booking)
    db.session.commit()

    return jsonify({
        'message': 'Booking created',
        'booking_id': booking.id,
        'booking': booking.to_dict()
    }), 200


# GET /api/booking/<booking_id>
@booking_bp.route('/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    # Users can only see their own bookings; admins see all
    if user.role != 'admin' and booking.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    return jsonify({'booking': booking.to_dict()}), 200


# GET /api/booking/my
@booking_bp.route('/my', methods=['GET'])
def my_bookings():
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401

    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings], 'total': len(bookings)}), 200


# POST /api/booking/<booking_id>/cancel
@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if user.role != 'admin' and booking.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    if booking.status == 'paid':
        return jsonify({'error': 'Cannot cancel a paid booking'}), 409

    if booking.status == 'cancelled':
        return jsonify({'error': 'Booking already cancelled'}), 409

    old_status = booking.status
    booking.status = 'cancelled'
    booking.updated_at = datetime.utcnow()

    # Restore seat
    event = Event.query.get(booking.event_id)
    if event:
        event.seats_available += 1

    db.session.commit()
    return jsonify({'message': 'Booking cancelled', 'booking': booking.to_dict()}), 200


# GET /api/booking/all  (admin only)
@booking_bp.route('/all', methods=['GET'])
def all_bookings():
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401
    if user.role != 'admin':
        return jsonify({'error': 'Forbidden: admin only'}), 403

    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings], 'total': len(bookings)}), 200
