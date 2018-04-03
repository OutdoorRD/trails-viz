from flask import Flask, request, send_from_directory
app = Flask(__name__, static_url_path='')

@app.route('/')
def get_page():
    return app.send_static_file('index.html')
