#This is the python file for a flask application that runs as the backend server integrating the
#deep learning models,the website interface, database as well as the react app for connecting with blockchain.


import requests
from io import BytesIO
import base64
import io
from flask import Flask, render_template, request, redirect, url_for, session
import os
from PIL import Image
import sqlite3
import cv2
from stegano import lsb
import time
import random
import string
import datetime
from flask import send_file, request, make_response
from tensorflow import keras
import tensorflow as tf
import matplotlib.pyplot as plt
from cryptography.fernet import Fernet
from diffusers import DiffusionPipeline


#Once models are downloaded add their relative paths here

path_to_price_pred_model=""
path_to_generator=""

username = ""

conn = sqlite3.connect('user_credentials.db')
cursor = conn.cursor()

app = Flask(__name__)

app.secret_key = "Divya@1"


def generate_random_string(length):
    characters = string.ascii_letters + string.digits 
    random_string = ''.join(random.choice(characters) for _ in range(length))
    random_string+='_'+str(return_nftid())
    return random_string


def print_table_rows(table):
    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()


def validate_user_credentials(username, password):
    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM registerdata WHERE username = ? AND password = ?', (username, password))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def generate_id():
    id = ''.join(random.choices(string.digits, k=20))
    return id


def generate_timestamp():
    timestamp = datetime.datetime.now()
    return timestamp


user_details = []


def log(username, id, action):
    try:
        conn = sqlite3.connect('user_credentials.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                timestamp TIMESTAMP,
                id TEXT PRIMARY KEY,
                username TEXT,
                action TEXT
            )
        ''')
        timestamp = generate_timestamp()
        cursor.execute('''
            INSERT INTO logs (timestamp, id, username, action)
            VALUES (?, ?, ?,?)
        ''', (timestamp, id, username, action))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("SQLite error:", e)


def get_all_details(username):
    global user_details
    try:
        conn = sqlite3.connect('user_credentials.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM registerdata WHERE username = ?', (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            user_details = list(result)
            return list(result)  
        else:
            return False  
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return None


@app.route('/')
def login():
    return render_template('what-we-do.html')


@app.route('/login', methods=['POST'])
def authorize_creds():
    global username
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_user_credentials(username, password):
            session['username'] = username
            user_details = get_all_details(username)
            id = user_details[1]
            log(username, id, "LOGIN")
            return render_template('homepage.html')

        else:
            return redirect(url_for('login'))


def check_id(id):
    try:
        conn = sqlite3.connect('user_credentials.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM registerdata")
        id_list = [row[0] for row in cursor.fetchall()]
        if id in id_list:
            return True  
        else:
            return False
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()


def check_username(username):
    try:
        conn = sqlite3.connect('user_credentials.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM registerdata")
        usernames = [row[0] for row in cursor.fetchall()]
        if username in usernames:
            return True  
        else:
            return False
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

@app.route('/redirect_login')
def redirect_to_login():
    return render_template('login.html')

@app.route('/redirect_home')
def redirect_home():
    return render_template('homepage.html')

@app.route('/success')
def success_reg():
    return render_template('successreg.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global user_id
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        email = request.form['email']

        if(password == confirmpassword):
            if (not check_username(username)):
                id = generate_id()
                while(check_id(id)):
                    id = generate_id()

                timestamp = generate_timestamp()
                conn = sqlite3.connect('user_credentials.db')
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS registerdata (
                        timestamp TIMESTAMP,
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        username TEXT,
                        password TEXT,
                        email TEXT
                        )
                ''')
                try:
                    cursor.execute('''
                        INSERT INTO registerdata (timestamp, id, name, username, password, email)
                        VALUES (?, ?, ?,?,?,?)''', (timestamp, id, name, username, password, email))
                    log(username, id, "REGISTER")
                    conn.commit()
                    print("Data inserted successfully!")
                    conn.close()
                    return redirect(url_for('success_reg'))

                except sqlite3.IntegrityError:
                    print("Error: The primary key (id) already exists.")

            else:
                return render_template('signup.html', message="Oh no! The username you entered has already been taken, try again!")
        else:
            return render_template('signup.html', message="Oops! You've entered non-matching passwords, try again!")

    if request.method == 'GET':
        return render_template('signup.html', message="Yay, you're almost there!")




def text_to_binary(text):
    """Convert a string to binary."""
    binary_result = ' '.join(format(ord(char), '08b') for char in text)
    return binary_result


def binary_to_text(binary_str):
    """Convert a binary string to text."""
    text = ''.join(chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8))
    return text

def encode_image_msb(image, secret_text):
    binary_text = text_to_binary(secret_text)
    pixels = list(image.getdata())
    encoded_pixels = []
    text_index = 0

    for pixel in pixels:
        if text_index < len(binary_text):
            pixel_binary = list(format(value, '08b') for value in pixel)
            pixel_binary[0] = binary_text[text_index] + pixel_binary[0][1:]
            text_index += 1
            encoded_pixels.append(tuple(int(value, 2) for value in pixel_binary))
        else:
            encoded_pixels.append(pixel)
    encoded_image = Image.new(image.mode, image.size)
    encoded_image.putdata(encoded_pixels)
    return encoded_image

def fetch_msb(image):
    pixels = list(image.getdata())
    binary_text = ''
    for pixel in pixels:
        red_binary = format(pixel[0], '08b')
        binary_text += red_binary[0]
    key = binary_to_text(binary_text)
    return key

def generate_key():
    return Fernet.generate_key()

def encrypt(message, key):
    cipher_suite = Fernet(key)
    encrypted_message = cipher_suite.encrypt(message.encode())
    return encrypted_message

def decrypt(encrypted_message, key):
    cipher_suite = Fernet(key)
    decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
    return decrypted_message


def extract_string(stego_image):
    secret_string = lsb.reveal(stego_image)
    if not secret_string:
        secret_string=fetch_msb(stego_image)
    if secret_string:
        return secret_string
    

def get_timestamp_by_key(credential_string):
    try:
        conn = sqlite3.connect('user_credentials.db')
        cursor = conn.cursor()
        select_sql = """
        SELECT timestamp FROM nft_encrypt
        WHERE key = ?
        """
        cursor.execute(select_sql, (credential_string,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]  
        else:
            return None  
    except sqlite3.Error as e:
        print("Error retrieving timestamp:", e)
    finally:
        if conn:
            conn.close()

def return_nftid():
    connection = sqlite3.connect("user_credentials.db")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM nft_encrypt")
    count = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return count+1

        
def predict_price(image):
    model = tf.keras.models.load_model(path_to_price_pred_model)
    image = tf.image.resize_with_crop_or_pad(image, 224, 224)
    image = tf.expand_dims(image, axis=0)
    prediction = model.predict(image)
    return str("{:.6f}".format(float(prediction[0][0])))+"ETH"


def authenticate_image(image, secret_message):
    global user_details
    generator = keras.models.load_model(path_to_generator)
    image = tf.image.resize_with_crop_or_pad(image, 256, 256)
    image = tf.image.adjust_brightness(
        image, delta=-0.1)  

    img1 = tf.expand_dims(image, axis=0)
    prediction = generator(img1, training=True)
    image_np = prediction[0].numpy()
    smoothed_image = cv2.GaussianBlur(image_np, (3, 3), 0.5)
    pred_image = Image.fromarray((smoothed_image * 255).astype('uint8'))
    print(type(pred_image)) 
    encoded_image = lsb.hide(pred_image, secret_message)
    log(username, id, "AUTHENTICATE")
    return encoded_image

def get_key_from_nft(image):
    try:
        key=lsb.reveal(image)
        return key
    except:
        return False

def encrypt_key_fetch(image):
    try:
        if isinstance(image, io.BytesIO):
            image = Image.open(image)
        key = lsb.reveal(image)
        return key
    except Exception as e:
        print("Error:", e)
        return None

def insert_crypto_record(encoding, encrypted_message, key):
    conn = sqlite3.connect('user_credentials.db')
    timestamp=generate_timestamp()
    cursor = conn.cursor()
    insert_record_query = '''
    INSERT INTO crypto_encrypt (timestamp, encoding, encrypted_message, key)
    VALUES (?, ?, ?, ?);
    '''
    cursor.execute(insert_record_query, (timestamp, encoding, encrypted_message, key))
    conn.commit()
    conn.close()

def get_key_and_encoding(encrypted_message):
    conn = sqlite3.connect('user_credentials.db') 
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT  encoding, encrypted_message, key FROM crypto_encrypt WHERE encrypted_message LIKE ?', ('%' + encrypted_message + '%',))
        result = cursor.fetchone()
        if result:
            encoding, encrypted_message, key = result
            return encoding, encrypted_message, key
        else:
            return None, None
    finally:
        conn.close()

@app.route('/check_nft', methods=['GET', 'POST'])
def check_nft():
    res=""
    global user_details
    if request.method == 'POST' and request.files != None:
        if 'image' in request.files:
            uploaded_image = request.files['image']
            image = tf.image.decode_image(uploaded_image.read())
            encrypted_message=encrypt_key_fetch(uploaded_image)
            res="Oops! This NFT is not registered with us. It is not NFTGenesis certified."

            if encrypted_message:
                encrypted_message=encrypted_message[2:]
                encoding, encrypted_message, key=get_key_and_encoding(encrypted_message)
                if encoding:
                    key=key.decode('utf-8')
                    encoding_image = decrypt(encrypted_message, key)
                    nftid=encoding_image.split("_")[1]
                    retrieval_time=get_timestamp_by_key(key.encode("utf-8"))
                    res="This NFT has maximum rarity value. NFT#"+nftid+" has been NFTGenesis certified on "+str(retrieval_time)
                            
            img_data = tf.image.encode_png(image)
            img_bytes = io.BytesIO(img_data.numpy())
            img_data = base64.b64encode(img_bytes.getvalue()).decode()
            id = user_details[1]
            username = user_details[3]
            log(username, id, "VALIDATE")
            return render_template('check_nft.html', res=res,img_data=img_data,)

    return render_template('check_nft.html',res="Upload your NFT to find out if it is NFTGenesis certified.")



@app.route('/predict', methods=['POST', 'GET'])
def predict():
    global user_details
    name = user_details[2]
    global username
    if request.method == 'POST' and request.files != None:
        if 'image' in request.files:
            uploaded_image = request.files['image']
            if uploaded_image.filename != '':
                image = tf.image.decode_image(uploaded_image.read())
                market_price=predict_price(image)
                id = user_details[1]
                username = user_details[3]
                log(username, id, "PREDICT")
                image = tf.image.resize_with_crop_or_pad(image, 224, 224)
                img_data = tf.image.encode_png(image)
                img_bytes = io.BytesIO(img_data.numpy())
                img_data = base64.b64encode(img_bytes.getvalue()).decode()
                return render_template('price_predict.html', NFT_price=market_price, img_data=img_data, )

    return render_template('price_predict.html', name=name, )


@app.route('/mint', methods=['GET', 'POST'])
def mint():
    global user_details
    id = user_details[1]
    username = user_details[3]
    log(username, id, "MINT")
    return redirect('http://localhost:3000/create-nft')
        

@app.route('/about_us', methods=['POST', 'GET'])
def about_us():
    return render_template('about-us.html', )


@app.route('/download', methods=['GET', 'POST'])
def download_image():
    global user_details
    img_data = request.form['img_data']
    img_bytes = base64.b64decode(img_data)
    response = make_response(img_bytes)
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Disposition'] = 'attachment; filename=image.png'
    id = user_details[1]
    log(username, id, "DOWNLOAD")
    return response


def is_message_present(encrypted_message):
    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()
    check_message_query = '''
    SELECT EXISTS (
        SELECT 1
        FROM crypto_encrypt
        WHERE encrypted_message = ?
    );
    '''
    cursor.execute(check_message_query, (encrypted_message,))
    result = cursor.fetchone()[0]
    conn.close()
    return bool(result)

@app.route('/auth_wp', methods=['POST', 'GET'])
def auth_wp():
    global user_details
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST' and request.files != None:
        if 'image' in request.files:
            uploaded_image = request.files['image']
            image = tf.image.decode_image(uploaded_image.read())
            secret_message = generate_random_string(20)
            save_key=secret_message[:2]+secret_message.split("_")[1]
            key = generate_key()
            secret_message = encrypt(secret_message, key)
            while(is_message_present(secret_message)):
                secret_message = encrypt(secret_message, key)
            insert_crypto_record(save_key,secret_message,key)
            resized_image = authenticate_image(image, secret_message)
            img_bytes = io.BytesIO()
            resized_image.save(img_bytes, format='PNG')
            img_data = base64.b64encode(img_bytes.getvalue()).decode()
            id = user_details[1]
            username = user_details[3]
            log(username, id, "AUTHENTICATE")
            return render_template('result.html', img_data=img_data,)

    return render_template('authenticate.html')


@app.route('/text-to-nft', methods=['POST'])
def stable_diffusion():
    def generate(prompt):
        pipeline = DiffusionPipeline.from_pretrained("sarathAI/NFT-Genesis")
        generated_image = pipeline(prompt)
        return generated_image
    text=request.form['keyword']
    url1 = generate(text)
    response = requests.get(url1)
    image = Image.open(io.BytesIO(response.content))
    secret_message = generate_random_string(20)
    save_key=secret_message[:2]+secret_message[-1]
    key = generate_key()
    secret_message = encrypt(secret_message, key)
    insert_crypto_record(save_key,secret_message,key)
    resized_image = lsb.hide(image, secret_message) 
    img_bytes = io.BytesIO()
    resized_image.save(img_bytes, format='PNG')
    img_data = base64.b64encode(img_bytes.getvalue()).decode()
    id = user_details[1]
    username = user_details[3]
    log(username, id, "GENERATE")
    return render_template('result.html', img_data=img_data)


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


if __name__ == '__main__':
    app.run(debug=True)
