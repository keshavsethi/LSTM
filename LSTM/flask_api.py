import model as md
from flask import Flask,request 
import json
import numpy as np
from flask import jsonify 
from random import seed
from random import gauss

app = Flask(__name__)

from multiprocessing.managers import BaseManager
from flask import g, session

def get_model():
    if not hasattr(g, 'model'):
        manager = BaseManager(('', 37844), b'password')
        manager.register('get_connection')
        manager.connect()
        g.model = manager.get_connection()

    return g.model

# model = md.Model("./weights")
#
@app.route('/predict_withone', methods=['POST'])
def predict_withone():
    print("predicting")
    model = get_model()
    event = json.loads(request.data)
    values = event["values"]
    prediction = model.run_model_online(values)
    prediction = {y: float(x) for y,x  in prediction.items()}
    print("value---------", prediction)
    return jsonify(prediction)   


@app.route('/resetmodel', methods=['POST'])
def resetmodel():
    prediction = model.model.reset_model()
    return "Success" 



@app.route('/predict_withmany', methods=['POST'])

def predict_withmany():
    event = json.loads(request.data)
    values = event["values"]
    print(values)
    prediction = model.model.predict(values)
    return jsonify(prediction)    



@app.route('/randomvalue', methods=['POST'])
def randomvalue():
    event = json.loads(request.data)
    values = event["values"]
    seed(1) 
    prediction = []
    for x in values:
        prediction.append(x + gauss(0, 5))
    return jsonify(prediction)

if __name__ =='__main__':
    app.run(debug=True)
