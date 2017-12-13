# -*- coding: utf-8 -*-

from flask import Flask, jsonify

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'compute complexity',
        'description': u'task1', 
        'done': False
    },
    {
        'id': 2,
        'title': u'ompute complexity',
        'description': u'task2', 
        'done': False
    }
]

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

if __name__ == '__main__':
    app.run(debug=True)