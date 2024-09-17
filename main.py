import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Ticket
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.urandom(24)
db.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    logger.info(f"Session state at index: {session}")
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pin = request.form.get('pin')
        logger.info(f"Login attempt with PIN: {pin}")
        user = User.query.filter_by(pin=pin).first()
        if user:
            session['user_id'] = user.id
            session.permanent = True  # Extend session lifetime
            logger.info(f"User with ID {user.id} logged in successfully. Session: {session}")
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt with PIN: {pin}")
            flash('Invalid PIN. Please try again.', 'error')
    logger.info(f"Session state at login GET: {session}")
    return render_template('login.html')

@app.route('/logout')
def logout():
    logger.info(f"User logged out. Session before logout: {session}")
    session.pop('user_id', None)
    logger.info(f"Session after logout: {session}")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    logger.info(f"Session state at dashboard: {session}")
    if 'user_id' not in session:
        logger.warning("Unauthorized access attempt to dashboard")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user is None:
        logger.error(f"User with ID {session['user_id']} not found in database")
        session.pop('user_id', None)
        return redirect(url_for('login'))
    tickets = Ticket.query.filter_by(user_id=user.id).all()
    logger.info(f"Retrieved {len(tickets)} tickets for user {user.id}")
    logger.info(f"User {user.id} accessed dashboard successfully")
    return render_template('dashboard.html', user=user, tickets=tickets)

@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    logger.info(f"Submitting ticket. Session state: {session}")
    if 'user_id' not in session:
        logger.warning("Unauthorized ticket submission attempt")
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    logger.info(f"Received ticket data: {data}")
    logger.info(f"Attempting to create new ticket: {data}")
    
    try:
        new_ticket = Ticket(
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            user_id=session['user_id']
        )
        db.session.add(new_ticket)
        db.session.commit()
        logger.info(f"Ticket submitted successfully. Ticket ID: {new_ticket.id}")
        logger.info(f"Ticket saved to database. Ticket details: {new_ticket.__dict__}")
        return jsonify({'message': 'Ticket submitted successfully', 'id': new_ticket.id})
    except Exception as e:
        logger.error(f"Error submitting ticket: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred while submitting the ticket'}), 500

@app.route('/close_ticket/<int:ticket_id>', methods=['POST'])
def close_ticket(ticket_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    ticket = Ticket.query.get(ticket_id)
    if ticket and ticket.user_id == session['user_id']:
        ticket.is_closed = True
        db.session.commit()
        return jsonify({'message': 'Ticket closed successfully'})
    return jsonify({'error': 'Ticket not found or unauthorized'}), 404

@app.route('/clear_tickets', methods=['POST'])
def clear_tickets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    Ticket.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    return jsonify({'message': 'All tickets cleared successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will only create tables if they don't exist
        # Check if the test PIN exists, if not, add it
        test_pin = "52640628"
        if not User.query.filter_by(pin=test_pin).first():
            new_user = User(pin=test_pin)
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"Added test user with PIN: {test_pin}")
    app.run(host='0.0.0.0', port=5000)
