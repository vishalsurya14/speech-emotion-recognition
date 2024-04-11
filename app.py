from flask import Flask, render_template, request, redirect, url_for
import pickle
import soundfile
import librosa
import numpy as np



from flask import Flask,render_template,request,session,redirect,url_for
import pickle
import re
import numpy as np
from flask_mysqldb import MySQL
import MySQLdb.cursors
# from*. import UserInput  # Import your UserInput model


app = Flask(__name__) 




# app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'


  
mysql = MySQL(app)


@app.route('/', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('home.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
  

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)





# app = Flask(__name__)
app.config["SECRET_KEY"] = "speechemotionkey"

observed_emotions = ['calm', 'happy', 'fearful', 'disgust', 'neutral','angry','sad']

pre =  ""
em = ""

emotion_emoji = {
    "calm": "😌",
    'happy': "😃", 
    'fearful': "😨", 
    'disgust':"🤢",
    "angry" : "😡",
    "neutral" : "😐",
    'sad':"😞"
}


# this portion was commented.
def extract_feature(file_name, mfcc, chroma, mel):
    with soundfile.SoundFile(file_name) as sound_file:
        X = sound_file.read(dtype="float32")
        sample_rate=sound_file.samplerate
        if chroma:
            stft=np.abs(librosa.stft(X))
        result=np.array([])
        if mfcc:
            mfccs=np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
            result=np.hstack((result, mfccs))
        if chroma:
            chroma=np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
            result=np.hstack((result, chroma))
        if mel:
            mel=np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T,axis=0)
            result=np.hstack((result, mel))
    return result


# this portion was commented
model_name = "./modelhybridEmotion.pkl" 
ml_model = pickle.load(open(model_name,"rb"))


@app.route('/home', methods=["GET","POST"])
def home():
    return render_template('home.html')


@app.route('/prediction', methods=["GET","POST"])
def index():   
     return render_template('prediction.html')

# this portion was commented
@app.route('/realtimeprediction', methods=["GET","POST"])
def audio():
    prediction1 = ""
    emoji1= ""
    if request.method == "POST":
        print("Form Data recieved")
        if "file" not in request.files:
            print("1")
            return redirect(request.url)
    # blank file hanlde 
        file = request.files["file"]
        if file.filename == "":
            print("2")
            return redirect(request.url)
        if file:
            features = extract_feature(file_name=file,mfcc= True, chroma= True, mel= True )
            features = features.reshape(1, -1)
            prediction1 = ml_model.predict(features)
            prediction1 = prediction1[0]
            print(prediction1)
            if prediction1 in observed_emotions:
                emoji1 = emotion_emoji[prediction1]
                print(emoji1)
    global pre, em
    pre = prediction1            
    em = emoji1
    print(pre, em)
    return render_template("realtimepredection.html",  prediction1=prediction1, emoji1=emoji1)
    
#this portion was commented
@app.route('/redirect', methods=["GET","POST"])
def red():
    predict = pre
    emoj= em
    return render_template("redirectprediction.html", pred=predict, emo=emoj)


if __name__ == '__main__':
    app.run(debug=True)