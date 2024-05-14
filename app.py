# from flask import Flask , request
# from flask_cors import CORS, cross_origin

# app = Flask(__name__)
# CORS(app , resources={r"/*" : {
#     "origins" : "*", 
#     "methods" : ["GET" , "POST"]
#     }})

# api_v2_cors_config = {
#   "origins": ["http://localhost:5000"],
#   "methods": ["OPTIONS", "GET", "POST"],
#   "allow_headers": ["Authorization", "Content-Type"]
# }


# @app.route('/api/v2/hello')
# @cross_origin(**api_v2_cors_config)
# def v2_hello():
#     param1 = request.args.get('name')
#     param2 = request.args.get('phone')
#     print(param1 , param2)
#     return 'Hello World'


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8510, debug=True)

from flask import Flask, jsonify , request
from backend import *
import uuid
from datetime import datetime
# from src.nlpsim.nlpsim_main import * 
import json
from flask_cors import CORS , cross_origin

question_generator  = None
db = None
nlp_obj = None
verify_ans = None


def create_app():
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

    # initilization of every thing 
    def initialize_processor_in_background():
        global   db , nlp_obj , verify_ans
        verify_ans = VerifyAnswer()
        db = MongoDatabase()
        # nlp_obj = GetSimilarity()
        collections = db.list_collection_names()
        if 'auth' not in collections:
            db.create_collection('auth')
        if 'quiz_data' not in collections:
            db.create_collection('quiz_data')

    initialize_processor_in_background()

    def create_uuid():
        while True:
            uuid_id = str(uuid.uuid1())  # Generate UUID and convert to string
            is_present = db.find_one_document('auth', {'uuid': uuid_id})  # Check if the UUID already exists
            if not is_present:
                return uuid_id
            
    # score
    def score(arr):
        score = 0 
        for question in arr:
            if question['isCorrect'] == 'True'.lower():
                score += 1
        return score 
        
    # on first page
    @app.route('/')
    def index():
        return {}
    
    # get question on first time 
    @app.route('/get_questions')
    @cross_origin(**api_v2_cors_config)
    def get_question():
        global question_generator 
        data_frame = {'hindi' : df_hindi , 'english' :df_eng}
        lang = request.args.get('lang')
        question_generator = RandomQuestion(data_frame[lang])
        all_question = question_generator.get_all_question(lang)
        return all_question
    
    @app.route('/api/guest_user')
    @cross_origin(**api_v2_cors_config)
    def guest():
        try:
            unique_id = create_uuid()
            name = request.args.get('name')
            phone = request.args.get('phone')
            request_data = {"phone" :phone , "name" : name }
            request_data['uuid'] = str(unique_id)
            request_data['created_at'] = datetime.now()
            data = [request_data]
            db.insert_many_documents('auth' , data )  
            return {"unique_id" : unique_id}
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/before_login_quiz_data')
    @cross_origin(**api_v2_cors_config)
    def insert_quiz():
        try:
            uuid = request.args.get('uuid')
            name = request.args.get('name')
            quiz = request.args.getlist('quiz')
            phone = request.args.get('phone')
            request_data = {'quiz' : quiz , 'uuid' : uuid , 'name' : name , 'phone' : phone} 
            print(request_data)
            request_data['created_at'] = datetime.now()
            request_data['score'] = score(request_data['quiz'])
            data = [request_data]
            db.insert_many_documents('quiz_data' , data )  
            return {'msg' : 'insert done!'}
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/after_login_update')
    @cross_origin(**api_v2_cors_config)
    def update_data_after_login():
        try:
            name = request.args.get('name')
            phone = request.args.get('phone')
            uuid = request.args.get('uuid')
            to_update = {'name' : name , 'phone' :phone}
            db.update_many_documents('auth' , uuid , to_update)
            db.update_many_documents('quiz_data' , uuid , to_update)
            res = db.order_by_score('test' , {"score": -1})
            print(res)
            return {'winner' : res[:10]}
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # check question is right or wrong if the answer is given in speech 
    @app.route('/api/verify_answer')
    @cross_origin(**api_v2_cors_config)
    def verify_answer():
        user_answer = request.args.get('user_answer')
        row_number = int(request.args.get('question_id')) if request.args.get('question_id') else 0
        print({'u' :user_answer})
        correct_answer = question_generator.get_right_answer(row_number)
        print({'a' : correct_answer})
        # output = nlp_obj.process(s1 = user_answer , s2 = correct_answer )
        output = verify_ans.run_completion(f"user_answer = {user_answer} , correct_answer = {correct_answer} ")
        print(output)
        return {'is_correct' : output.lower() , 'correct_answer' : correct_answer }
    
    @app.route('/your_score', methods=['POST'])
    def score_of_game():
        data = request.json
        your_uuid = data['uuid']
        score = db.find_one_document('quiz_data' , {"uuid": your_uuid },{ "score": 1, "_id": 0 })
        return score
    
    # Define error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return 'Page not found', 404
    
    return app 
   

if __name__ == '__main__':
    app = create_app() 
    app.run(host = '0.0.0.0' ,port= 8502 , debug=True)
    
