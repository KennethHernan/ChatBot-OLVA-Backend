from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
from db import db
from user import User
import bcrypt
import smtplib
from flask_cors import CORS
from flask_pymongo import PyMongo
from email.mime.text import MIMEText

app = Flask(__name__)

socket_io = SocketIO(app, cors_allowed_origins="*")

# MongoDb Prueba de Login
app.config['MONGO_URI'] = 'mongodb+srv://jore24:jore24@olva1.3g92oyt.mongodb.net/olva1?retryWrites=true&w=majority'
mongo = PyMongo(app)

CORS(app)

dbcolec = mongo.db.usuario
# dbcolec = mongo.db.messages

for document in dbcolec.find():
    print(document)


# Ruta para el registro de usuarios
@app.route('/register', methods=['POST'])
def register():
    dbcolec = mongo.db.usuario
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        email = data['email']

        # Verificar si el usuario ya existe en la base de datos
        existing_user = dbcolec.find_one({'username': username})
        if existing_user:
            return jsonify({'message': 'El usuario ya está registrado'})

        # Generar el hash de la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insertar el nuevo usuario en la base de datos
        dbcolec.insert_one({
            'username': username, 
            'password': hashed_password,
            'email': email
        })

        # Enviar correo electrónico de bienvenida
        sender_email = 'jore24@autonoma.edu.pe'  # Reemplaza con tu dirección de correo electrónico
        receiver_email = email  # Usar la dirección de correo electrónico proporcionada por el usuario
        subject = 'Bienvenido a nuestra aplicación'  # Asunto del correo electrónico
        message = 'Hola {},\n\nGracias por registrarte en nuestra aplicación.'.format(username)  # Cuerpo del correo electrónico
        
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        smtp_server = 'smtp.gmail.com'  # Servidor SMTP de Gmail (puedes usar otro si prefieres)
        smtp_port = 587  # Puerto SMTP de Gmail

        smtp_username = 'jore24@autonoma.edu.pe'  # Tu dirección de correo electrónico
        smtp_password = 'x'  # Tu contraseña de correo electrónico
        
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
        except smtplib.SMTPException as e:
            error_message = str(e)
            response = {
                'message': 'Error en el registro',
                'error': error_message
            }
            return jsonify(response), 500

        response = {
            'message': 'Registro exitoso',
            'username': username,
            'email': email
        }

        return jsonify(response)
    except Exception as e:
        error_message = str(e)
        response = {
            'message': 'Error en el registro',
            'error': error_message
        }
        return jsonify(response), 500

@app.route('/login', methods=['POST', 'GET'])
def login():
    dbcolec = mongo.db.usuario
    # Obtener los datos del JSON enviado en la solicitud
    data = request.get_json()

    # Extraer los datos necesarios del JSON
    username = data.get('username')
    password = data.get('password')

    # Buscar el usuario en la base de datos
    user = dbcolec.find_one({'username': username})

    if user:
        hashed_password = user.get('password')
        # Verificar si la contraseña es correcta
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            session['user_id'] = str(user.get('_id'))

            response = {
                'message': 'Inicio de sesión exitoso',
                'username': username
            }
        else:
            response = {
                'message': 'Contraseña incorrecta'
            }
    else:
        response = {
            'message': 'Usuario no encontrado'
        }

    # Devolver la respuesta en formato JSON
    return jsonify(response)

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