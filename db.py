import config
from tinydb import TinyDB, Query
from typing import Union
from tinydb.database import Document

tests = TinyDB('tests.json', indent = 4)
users = TinyDB('user_data.json', indent = 4)
results = TinyDB('results.json', indent = 4)

test = tests.table('Test')
user = users.table('Users')

q = Query()

def is_admin(chat_id):
    admin_id = config.get_adminid()
    if str(chat_id) in admin_id:
        return True
    else:
        return False
    
def is_start(chat_id):
    user_one = user.get(doc_id=str(chat_id))
    return user_one == None

def save_pdf(test_id:str, file_path: str, test_answer: str):
    test.insert(
        {
            'test_id': test_id,
            "file_path": file_path,
            "test_answer": test_answer
        }
    )
    return True

def register(chat_id, fullname, username):
    user.insert(document=Document({
        "fullname": fullname,
        "username": username
    }, doc_id = chat_id))



def user_search(chat_id):
    return user.get(doc_id=str(chat_id))

def get_testid(test_id):
    test_one = test.search(q.test_id == str(test_id))
    return test_one

def result_save(true_total, false_total, score, test_id, chat_id):
    user_one_result = results.table(str(chat_id))
    user_one_result.insert(document=Document({
            "true_total": true_total,
            "false_total": false_total,
            "score": score
        }, doc_id = test_id))
    

def check_user_test(test_answer: str, chat_id):
    test_data = test_answer.split('*')
    if len(test_data) != 2:
        return 'error_testid'   
    
    test_id = test_data[0].strip()
    user_answer_raw = test_data[1].strip().lower().replace(' ', '')
    
    true_test = get_testid(test_id=test_id)
    if not true_test:
        return 'test_not_found'
    
    true_test_answer = true_test[0]['test_answer'].split('\n')
    true_test_answer = [x.strip().lower().replace(' ', '') for x in true_test_answer if x.strip()]
    
    correct_answers = []
    correct_points = []

    for item in true_test_answer:
        parts = item.split(':') 
        if len(parts) != 3:
            return 'error_format_true'  
        correct_answers.append(parts[1].strip().lower())
        correct_points.append(int(parts[2].strip()))
    
    total_questions = len(correct_answers)
    user_answers = [
        x.strip().lower()
        for x in user_answer_raw.split(':')
        if x.strip()
    ]

    if len(user_answers) != total_questions:
        return 'answer_length_error'
    
    true_total = 0
    false_total = 0
    total_score = 0

    for true_ans, user_ans, point in zip(correct_answers, user_answers, correct_points):
        if true_ans == user_ans:
            true_total += 1
            total_score += point
        else:
            false_total += 1

    result_save(true_total, false_total, total_score, test_id, chat_id)

    return {
        "correct": true_total,
        "wrong": false_total,
        "score": total_score,
        "total_questions": total_questions
    }

def admin_get_result(testID: str):
    table_all = sorted(list(results.tables()))
    result_user_data = []
    for table in table_all:
        table_data = dict(results.table(table).get(doc_id=testID))
        if table_data != None:
            user_data = user_search(table)
            user_data['true_total'] = table_data['true_total']
            user_data['false_total'] = table_data['false_total']
            user_data['score'] = table_data['score']
            result_user_data.append(user_data)
    result_user_data = sorted(result_user_data, key=lambda x: x['true_total'], reverse=True)
    return result_user_data
