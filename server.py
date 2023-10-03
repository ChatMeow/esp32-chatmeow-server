from flask import Flask, request
import os, datetime, sys
import wave
import speech_recognition as sr

from meow_chatgpt.chat.chat import ChatModule
import logging
from meow_chatgpt.vits.vits_tts import save_vits_wav

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

bot = ChatModule()


def _write_wav(data, rates, bits, ch):
    t = datetime.datetime.utcnow()
    time = t.strftime('%Y%m%dT%H%M%SZ')
    if not os.path.exists(os.path.join(os.getcwd(), 'static')):
        os.mkdir(os.path.join(os.getcwd(), 'static'))
    filename = os.path.join("static", "raw.wav")
    wavfile = wave.open(filename, 'wb')
    wavfile.setparams((ch, int(bits / 8), rates, 0, 'NONE', 'NONE'))
    wavfile.writeframesraw(data)
    wavfile.close()
    return filename


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/upload", methods=["POST"])
def upload():
    total_bytes = 0
    sample_rates = 0
    bits = 0
    channel = 0
    bits = request.headers.get('x-audio-bits', '').lower()
    channel = request.headers.get('x-audio-channel', '').lower()
    sample_rates = request.headers.get('x-audio-sample-rates', '').lower()
    print("Audio information, sample rates: {}, bits: {}, channel(s): {}".format(sample_rates, bits, channel))
    data = request.get_data()
    print(len(data))
    filename = _write_wav(data, int(sample_rates), int(bits), int(channel))

    r = sr.Recognizer()
    harvard = sr.AudioFile(os.path.join("static", "raw.wav"))
    with harvard as source:
        audio = r.record(source)
    try:
        text = (r.recognize_google(audio, language='zh-CN'))
    except sr.exceptions.UnknownValueError:
        text = "..."

    logging.info("YOU: {}".format(text))
    response = bot.chat(text)
    logging.info("BOT: {}".format(response))
    save_vits_wav(response, "")
    return 'File {} was written, size {}'.format(filename, total_bytes)


app.run(debug=True, host="0.0.0.0", port=8000)
