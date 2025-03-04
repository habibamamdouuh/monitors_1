import psycopg2
import serial
from threading import Thread
from flask import Flask, render_template, request, session, redirect, flash
from flask_socketio import SocketIO, emit
from psycopg2.extras import DictCursor, RealDictCursor
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)
# socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

database_connection_session = (psycopg2.connect
    (
    host="ep-silent-sound-a5udo5gz.us-east-2.aws.neon.tech",
    database="FinalTrans",
    user="FinalTrans_owner",
    password="efmUkJg41rxS",
    port=5432
))

cur = database_connection_session.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())

cur.close()
database_connection_session.close()

# database_connection_session = psycopg2.connect(
#     host="ep-silent-sound-a5udo5gz.us-east-2.aws.neon.tech",
#     database="FinalTrans",
#     user="FinalTrans_owner",
#     password="efmUkJg41rxS",
#     port=5432
# )

# Arduino Serial Connection
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=1)

# Global variable to store sensor data
sensor_data = {
    'Humidity': "N/A",
    'Temperature': "N/A",
    'BPM': "N/A"
}

# Thread to read data from Arduino
# def read_arduino_data():
#     global sensor_data
#     while True:
#         try:
#             line = arduino.readline().decode('utf-8').strip()
#             if line:
#                 print(f"Raw Arduino Data: {line}")  # Debug: Log raw Arduino data
#                 parts = line.split(',')
#                 for part in parts:
#                     key, value = part.split(':')
#                     if key.strip() == "Temperature":
#                         sensor_data[key.strip()] = float(value)
#                     elif key.strip() == "Humidity":
#                         sensor_data[key.strip()] = float(value)
#                     else:
#                         sensor_data[key.strip()] = float(value)
#                 print(f"Updated Sensor Data: {sensor_data}")  # Debug: Log updated data
#         except Exception as e:
#             print(f"Error reading Arduino data: {e}")
#
# # Start the thread to read data

# Thread to read data from Arduino
def read_arduino_data():
    global sensor_data
    while True:
        try:
            line = arduino.readline().decode('utf-8').strip()
            if line:
                print(f"Raw Arduino Data: {line}")  # Debug raw Arduino data

                parts = line.split(',')
                for part in parts:
                    try:
                        key, value = part.split(':')
                        key = key.strip()
                        value = value.strip()

                        if key == "Humidity":
                            sensor_data[key] = float(value.replace('%', ''))  # Remove % and convert to float
                        elif key == "Temperature":
                            sensor_data[key] = float(value.replace('°C', ''))  # Remove °C
                        elif key == "BPM":
                            sensor_data[key] = float(value)  # Convert to integer
                        else:
                            print(f"Unknown key: {key}, Value: {value}")  # Debug unexpected values

                    except ValueError as e:
                        print(f"Error parsing part: {part}, Error: {e}")

                print(f"Updated Sensor Data: {sensor_data}")  # Debug parsed data

        except Exception as e:
            print(f"Error reading Arduino data: {e}")


Thread(target=read_arduino_data, daemon=True).start()

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/index')
def index():
    babydata=session.get('baby')
    return render_template('index.html', babydata=babydata)

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     message = None
#     baby_data = None  # Store baby information after signup
#
#     if request.method == 'GET':
#         return render_template('signup.html')
#
#     elif request.method == 'POST':
#
#             # Collect form data
#             fname = request.form.get('firstname')
#             lname = request.form.get('lastname')
#             email = request.form.get('email')
#             password = request.form.get('password')
#             confirm_password = request.form.get('confirm_password')
#             baby_gender = request.form.get('baby_gender')
#             contact = request.form.get('contact')
#             address = request.form.get('address')
#             parent1 = request.form.get('parent1')
#             parent2 = request.form.get('parent2')
#
#
#
#             if password != confirm_password:
#                 message = 'Passwords do not match!'
#                 return render_template('signup.html', msg=message)
#
#
#
#             # Perform database operations
#             with database_connection_session.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
#                 # Check if baby (user) exists
#                 cur.execute('SELECT * FROM baby WHERE email = %s', (email,))
#                 if cur.fetchone():
#                     message = "User already exists!"
#                 else:
#                     # Insert new baby into the database
#                     cur.execute(
#                         '''INSERT INTO baby (fname, lname, email, password,  baby_gender, contact, address, parent1, parent2)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#                         RETURNING id
#                         ''',
#                         (fname, lname, email, password, baby_gender, contact, address, parent1, parent2)
#                     )
#                     database_connection_session.commit()
#                     new_baby_id = cur.fetchone()['id']
#
#                     # Fetch the newly created baby's data
#                     cur.execute(
#                         '''
#                         SELECT fname, lname, email, baby_gender, contact, address, parent1, parent2
#                         FROM baby
#                         WHERE id = %s
#                         ''',
#                         (new_baby_id,)
#                     )
#                     baby_data = cur.fetchone()
#                     message = "Baby record created successfully!"

#
# return render_template('signup.html', msg=message, baby_data=baby_data)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = None
    baby_data = None  # Store baby information after signup

    if request.method == 'GET':
        return render_template('signup.html')

    elif request.method == 'POST':
        # Collect form data
        fname = request.form.get('firstname')
        lname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        baby_gender = request.form.get('baby_gender')
        contact = request.form.get('contact')
        address = request.form.get('address')
        parent1 = request.form.get('parent1')
        parent2 = request.form.get('parent2')

        if password != confirm_password:
            message = 'Passwords do not match!'
            return render_template('signup.html', msg=message)

        try:
            # Create a NEW database connection inside the route
            database_connection_session = psycopg2.connect(
                host="ep-silent-sound-a5udo5gz.us-east-2.aws.neon.tech",
                database="FinalTrans",
                user="FinalTrans_owner",
                password="efmUkJg41rxS",
                port=5432
            )

            with database_connection_session.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                # Check if baby (user) exists
                cur.execute('SELECT * FROM baby WHERE email = %s', (email,))
                if cur.fetchone():
                    message = "User already exists!"
                else:
                    # Insert new baby into the database
                    cur.execute(
                        '''
                        INSERT INTO baby (fname, lname, email, password, baby_gender, contact, address, parent1, parent2)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        ''',
                        (fname, lname, email, password, baby_gender, contact, address, parent1, parent2)
                    )
                    database_connection_session.commit()
                    new_baby_id = cur.fetchone()['id']

                    # Fetch the newly created baby's data
                    cur.execute(
                        '''
                        SELECT fname, lname, email, baby_gender, contact, address, parent1, parent2
                        FROM baby
                        WHERE id = %s
                        ''',
                        (new_baby_id,)
                    )
                    baby_data = cur.fetchone()
                    message = "Baby record created successfully!"
        except Exception as e:
            print(f"Database error: {e}")
            message = "Internal Server Error"
        finally:
            # Close the connection to avoid leaks
            if database_connection_session:
                database_connection_session.close()

    return render_template('signup.html', msg=message, baby_data=baby_data)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     message = None
#     if request.method == 'GET':
#         return render_template('login.html')
#     elif request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#
#         # Secure the query to avoid SQL injection
#         with database_connection_session.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
#             cur.execute('SELECT * FROM baby WHERE email=%s AND password=%s', (email, password))
#             babydata = cur.fetchone()
#
#             if babydata:
#                 # Save user data to the session
#                 session['baby'] = dict(babydata)
#
#
#                 # Redirect to the patient dashboard or home
#                 return redirect('/index')
#             else:
#                 # If user data is not found, the email or password is incorrect
#                 message = 'Invalid email or password'
#                 return render_template('login.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Create a NEW database connection inside the route
            database_connection_session = psycopg2.connect(
                host="ep-silent-sound-a5udo5gz.us-east-2.aws.neon.tech",
                database="FinalTrans",
                user="FinalTrans_owner",
                password="efmUkJg41rxS",
                port=5432
            )

            with database_connection_session.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute('SELECT * FROM baby WHERE email=%s AND password=%s', (email, password))
                babydata = cur.fetchone()

                if babydata:
                    # Save user data to the session
                    session['baby'] = dict(babydata)
                    return redirect('/index')
                else:
                    message = 'Invalid email or password'
                    return render_template('login.html', message=message)
        except Exception as e:
            print(f"Database error: {e}")
            message = "Internal Server Error"
            return render_template('login.html', message=message)
        finally:
            # Close the connection to avoid leaks
            if database_connection_session:
                database_connection_session.close()


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/redirect_based_on_age', methods=['POST'])
def redirect_based_on_age():
    babydata = session.get('baby')  # Retrieve baby data from session

    if babydata and 'age' in babydata:
        age = babydata['age']  # Get age as a string

        # Redirect based on the text value of age
        if age == "Newborns":
            return redirect('/m4')

    else:
        flash("Baby data is missing or age is not available.")
        return redirect('/index')
@app.route('/m4',methods=['GET','POST'])
def m4():
       return render_template ('m4.html')




@socketio.on('request_sensor_data')
def send_sensor_data():
    print(f"Sending Sensor Data: {sensor_data}")  # Debug: Log data being sent
    emit('sensor_data', sensor_data)


# if __name__ == '__main__':
#     print("Server running at http://127.0.0.1:5000")
#     socketio.run(app, allow_unsafe_werkzeug=True)
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)


