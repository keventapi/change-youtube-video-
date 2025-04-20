from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data = {
    'url': None,
    'funtion': 'change_video',
    'executar_algo': False
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/get_video', methods=['POST'])
def get_video():
    global data
    url = request.form.get('url')
    data['executar_algo'] = True
    data['url'] = url
    return jsonify(data)

@app.route('/change_video')
def change_video():
    global data
    return jsonify(data)

@app.route('/changed')
def changed():
    global data
    data['executar_algo'] = False
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
