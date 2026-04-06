from flask import Flask
import os

app = Flask(__name__)

STATUS = r"C:\PA_AI\status"

@app.route("/")
def home():

    html = "<h2>PA_AI System Status</h2><ul>"

    for file in os.listdir(STATUS):

        path = os.path.join(STATUS,file)

        with open(path) as f:
            time = f.read()

        html += f"<li>{file} : {time}</li>"

    html += "</ul>"

    return html

app.run(host="0.0.0.0", port=5000)