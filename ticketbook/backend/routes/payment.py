from flask import Blueprint, request, jsonify
from database import db
from models import Booking, Payment
from routes.auth import get_current_user
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

# Card token simulation:
#   tok_test_valid   -> success
#   tok_test_decline -> declined (payment_status: declined, booking: failed)
#   anything else    -> declined


def simulate_payment(card_token):
    """Simulate payment gateway response."""
    if card_token == 'tok_test_valid':
        return 'success'
    return 'declined'


# POST /api/payment/pay
@payment_bp.route('/pay', methods=['POST'])
def pay():
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    booking_id = data.get('booking_id')
    card_token = data.get('card_token', '')

    if booking_id is None:
        return jsonify({'error': 'booking_id is required'}), 400
    if not card_token:
        return jsonify({'error': 'card_token is required'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    # Users can only pay their own bookings
    if user.role != 'admin' and booking.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    # TC-INT-05: block double payment
    if booking.status == 'paid':
        return jsonify({'error': 'Booking already paid'}), 409

    if booking.status == 'cancelled':
        return jsonify({'error': 'Cannot pay a cancelled booking'}), 409

    if booking.status == 'failed':
        return jsonify({'error': 'Cannot pay a booking with failed status, please create a new booking'}), 409

    # Get event price for payment record
    amount = booking.event.price if booking.event else 0.0

    payment_status = simulate_payment(card_token)

    payment = Payment(
        booking_id=booking.id,
        card_token=card_token,
        status=payment_status,
        amount=amount
    )
    db.session.add(payment)

    # TC-INT-04: success -> paid
    # TC-INT-06: declined -> failed
    if payment_status == 'success':
        booking.status = 'paid'
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'message': 'Payment successful',
            'payment_status': 'success',
            'booking_status': 'paid',
            'payment': payment.to_dict(),
            'booking': booking.to_dict()
        }), 200
    else:
        booking.status = 'failed'
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'message': 'Payment declined',
            'payment_status': 'declined',
            'booking_status': 'failed',
            'payment': payment.to_dict(),
            'booking': booking.to_dict()
        }), 402


# GET /api/payment/history
@payment_bp.route('/history', methods=['GET'])
def payment_history():
    user, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401

    if user.role == 'admin':
        payments = Payment.query.order_by(Payment.created_at.desc()).all()
    else:
        # Get only payments for user's bookings
        booking_ids = [b.id for b in user.bookings]
        payments = Payment.query.filter(Payment.booking_id.in_(booking_ids)).order_by(Payment.created_at.desc()).all()

    return jsonify({'payments': [p.to_dict() for p in payments], 'total': len(payments)}), 200
