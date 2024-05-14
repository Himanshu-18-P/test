from flask import Flask , request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app , resources={r"/api/*" : {
    "origins" : "*"
    }})


@app.route('/api/index')
def index():
    print('hello world')

   

@app.route('/api/hello' , methods=['POST'])
def v2_hello():
    data = request.json 
    param1 = data['name']
    param2 = data['phone']
    print(param1 , param2)
    return {'a' : [param1 , param2]}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8510, debug=True)

