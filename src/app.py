from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)

socket_io = SocketIO(app, cors_allowed_origins="*")




@socket_io.on('connect')
def handle_connect():
    socket_id = request.sid
    initial_message = '¡Hola! Soy un asistente virtual. ¿En qué puedo ayudarte hoy?'
    options = ['Soporte', 'Sucursal', 'Desconocido', 'asdsasd', 'awqeqwd']
    initial_bot_message = {
        'socket_id': 'bot',
        'message': initial_message,
        'options': options
    }
    emit('message', initial_bot_message, room=socket_id)


@socket_io.on('disconnect')
def handle_disconnect():
    print('Client disconnected')





if __name__ == "__main__":
    socket_io.run(app, host="0.0.0.0", port=5000)