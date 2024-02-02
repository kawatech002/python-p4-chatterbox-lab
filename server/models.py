from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.all()
        serialized_messages = [message.to_dict() for message in messages]
        return jsonify(serialized_messages)
    
    elif request.method == 'POST':
        data = request.json
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return make_response(jsonify({"error": "Both body and username are required"}), 400)

        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = db.session.query(Message).get(id)

    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    if request.method == 'GET':
        return jsonify(message.to_dict())

    elif request.method == 'PATCH':
        data = request.json
        new_body = data.get('body')

        if not new_body:
            return make_response(jsonify({"error": "New body is required for updating"}), 400)

        message.body = new_body
        db.session.commit()
        return jsonify(message.to_dict())

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response('', 204)