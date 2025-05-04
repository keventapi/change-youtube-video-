from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data = {
    'url': None,
    'function': 'change_video',
    'executar_algo': False,
    'recomendations': {}
}

@app.route('/')
def home():
    global data
    return render_template('home.html', dado=data)

@app.route('/get_video', methods=['POST'])
def get_video():
    global data
    url = request.form.get('url')
    data['executar_algo'] = True
    data['url'] = url
    return render_template('home.html', dado=data)

@app.route('/change_video')
def change_video():
    global data
    return jsonify(data)

@app.route('/changed')
def changed():
    global data
    data['executar_algo'] = False
    return jsonify(data)

@app.route('/reccomendations', methods=['POST'])
def reccomendations():
    global data
    ytreccomendations = request.get_json()
    print(ytreccomendations)
    if ytreccomendations != {}:
        data['recomendations'] = ytreccomendations
    print(data)
    return render_template('home.html', dado=data)

@app.route('/get_reccomendetions')
def get_reccomendations():
    global data
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
