from flask import Flask

app = Flask(__name__)

@app.route("/", methods=['POST'])
def index(json):
    return "Hello, backend"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)