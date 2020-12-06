from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename

################
# import the necessary packages
#import speech_recognition as sr
import io
import os
import wave
from playsound import playsound
from scipy.io import wavfile
from google.cloud import  speech
from google.cloud.speech_v1 import types
import os
from google.oauth2 import service_account

################

STATIC_FOLDER = './static'

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('input.html')

@app.route("/upload-audio", methods=["GET", "POST"])
def upload_audio():
    if request.method == 'POST':
        if request.files:
            #Reading the uploaded image
            audio = request.files["audio"]
            audioName = audio.filename
            audio.save(os.path.join(STATIC_FOLDER, audioName))
            
            # load the example image and convert it to grayscale
            pathtoaudio = os.path.join(STATIC_FOLDER, audioName)
            credentials = service_account.Credentials.from_service_account_file(os.path.join(STATIC_FOLDER,"credentials.json"))

            client = speech.SpeechClient(credentials=credentials)
            wf=wave.open(pathtoaudio,'rb')
            channel_count = wf.getnchannels()
            with io.open(pathtoaudio,'rb') as audio_file:
                content = audio_file.read()
                audio = speech.RecognitionAudio(content=content)

            config = types.RecognitionConfig(
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz= 16000,
                language_code='en-US',
                audio_channel_count=channel_count)
            text='It looks like you uploaded non valid audio format'
            try:
                response = client.recognize(config=config, audio=audio)
                text=''
                for result in response.results:
                    print('Transcript: {}'.format(result.alternatives[0].transcript))
                    text = text + result.alternatives[0].transcript
                
            except Exception as exp:
                print(text)
                print(exp)
            

            return redirect(url_for('output',text=text)) 
    else :
        return redirect(url_for('home'))

@app.route('/output')
def output():
    text= request.args.get('text')
    return render_template('output.html', text = text )

if __name__ == '__main__':
   app.run(debug=True)