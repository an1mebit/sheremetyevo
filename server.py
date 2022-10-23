from flask import Flask, request
from flask_cors import CORS, cross_origin
from item import Item
from analytic import get_task_info

app = Flask(__name__)
CORS(app=app)

@cross_origin(origins=["*"], supports_credentials=True)
@app.route("/", methods=['POST'])
def index():
    json_data = request.get_json()
    print(json_data)
    return Item(__root__=get_task_info(json_data)).json()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)