from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data = {
    'url': None,
    'function': '',
    'executar_algo': False,
    'volume': None,
    'recommendations': {}
}

@app.route('/')
def home():
    global data
    return render_template('home.html', dado=data)

@app.route('/next')
def next():
    global data
    data['function'] = 'next'
    data['executar_algo'] = True
    return jsonify(data)

@app.route('/pause')
def pause():
    global data
    data['function'] = 'pause'
    data['executar_algo'] = True
    return jsonify(data)

@app.route('/get_video', methods=['POST'])
def get_video():
    global data
    url = request.form.get('url')
    data['executar_algo'] = True
    data['function'] = 'change_video'
    data['url'] = url
    return render_template('home.html', dado=data)

@app.route('/get_data')
def change_video():
    global data
    return jsonify(data)

@app.route('/post_volume', methods=['POST'])
def post_volume():
    global data
    volume = request.get_json()
    data['volume'] = int(volume['volume'])
    return jsonify(data)

@app.route('/get_volume')
def get_volume():
    global data
    return jsonify(data)

@app.route('/reset_data')
def changed():
    global data
    data['executar_algo'] = False
    data['function'] = ''
    return jsonify(data)

@app.route('/post_recommendations', methods=['POST'])
def reccomendations():
    global data
    ytreccomendations = request.get_json()
    print(ytreccomendations)
    if ytreccomendations != {}:
        data['recommendations'] = ytreccomendations
    print(data)
    return render_template('home.html', dado=data)

@app.route('/get_recommendetions')
def get_reccomendations():
    global data
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
