import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://Raj@localhost:5432/{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    

        self.new_question = {
            'question': 'What won the most NBA championships',
            'answer': 'Bill Russell',
            'difficulty': 2,
            'category': 6
        }

        self.search_term = {
            'searchTerm': 'Peanut'
        }

        self.quiz1 = {
            'quiz_category': {'type' : 'click', 'id': 0},
            'previous_questions': [5, 9, 4, 6]
        }

        self.quiz2 = {
            'quiz_category': {'type' : 'science', 'id': 1},
            'previous_questions': [20, 21]
        }


    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        print('***Inside the test_get_categories function *** \n')
        data = json.loads(res.data)
        print(f'Response data json formatted: {data} \n')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        


    def test_paginate_questions(self):
        res = self.client().get('/questions')
        print('***Inside the test_paginate_questions function *** \n')
        data = json.loads(res.data)

        print(f'response obtained from server is: {res} \n')
        #print(f'response.data from server is: {res.data}')
        print(f'Response data json formatted: {data} \n')
        number_questions = len(data['questions'])
        print(f'Number of questions sent back in this test: {number_questions} \n')

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(number_questions,10)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))


    def test_404_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        print('***test_404_requesting_beyond_valid_page function *** \n')
        print(f'Response data json formatted: {data} \n')
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
    

    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        print('***test_delete_question function *** \n')
        print(f'Response data Json formatted {data}')

        question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['total_questions'],18)
        self.assertEqual(question, None)
    
    def test_422_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        print('***test errorhandler with status code = 422 function *** \n')
        print(f'The data back from server: {data}')

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'unprocessable')


    def test_post_new_question(self):
        res = self.client().post('/questions', json = self.new_question)
        data = json.loads(res.data)

        print('***test_post_new_question function *** \n')
        print(f'The data back from server is {data}')


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    def test_405_wrong_method(self):
        res = self.client().post('/questions/100', json = self.new_question)
        data = json.loads(res.data)

        print('***test_405_wrong_method function *** \n')
        print(f'The data back from server is {data}')


        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    
    def test_search_question(self):
        res = self.client().post('/questions/search', json = self.search_term)
        data = json.loads(res.data)

        print('***test_search_question function *** \n')
        print(f'The data back from server is {data}')


        question_id = data['questions'][0]['id']
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question_id, 12)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    
    def test_get_question_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        print('*** test_get_question_by_categeory function *** \n')
        print(f'The data back from server is {data}')


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 1)


    def test_play_quiz1(self):
        res = self.client().post('/quizzes', json = self.quiz1)
        data = json.loads(res.data)


        print('*** test_play_quiz1 function *** \n')
        print(f'The data back from server is {data}')

        valid_id = False
        if data['question']['id'] not in self.quiz1['previous_questions']:
            valid_id = True

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))
        self.assertTrue(valid_id)


    def test_play_quiz2(self):
        res = self.client().post('/quizzes', json = self.quiz2)
        data = json.loads(res.data)


        print('*** test_play_quiz2 function *** \n')
        print(f'The data back from server is {data}')

        valid_id = False
        if data['question']['id'] not in self.quiz2['previous_questions']:
            valid_id = True

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))
        self.assertTrue(valid_id)
        self.assertEqual(data['question']['id'], 22)

    
    def test_400_bad_request(self):
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)

        print('**** inside the test_400_bad_request function ****')
        print(f'The data back from server is {data}')

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()