from flask import Flask , request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app , resources={r"/*" : {
    "origins" : "*", 
    "methods" : ["GET" , "POST"]
    }})

api_v2_cors_config = {
  "origins": ["http://localhost:5000"],
  "methods": ["OPTIONS", "GET", "POST"],
  "allow_headers": ["Authorization", "Content-Type"]
}

@app.route('/')
def index():
    print('hello world')
    

@app.route('/api/v2/hello')
@cross_origin(**api_v2_cors_config)
def v2_hello():
    param1 = request.args.get('name')
    param2 = request.args.get('phone')
    print(param1 , param2)
    return 'or bhai'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8510, debug=True)

