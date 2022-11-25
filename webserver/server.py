#Baouya Abdelhakim
#Server edition to Interogate the server
import threading 
from flask import Flask
from flask import request
from nn_make_prediction import WaterOutputPredictor
import time

webapp = Flask(__name__)
predictor = WaterOutputPredictor('./conf/current_model_configuration.json')
predictor.predict_for([1.53, 10.2, 31.12])



values=-1

def start_loop(parameters):
    global values
    global predictor
    not_started = True

    while not_started:
        print('In start loop')

        print('Server started, quiting start_loop')

        #parameters =[1.53, 10.2, 31.12]
        print(parameters)
        calculated_values = predictor.predict_for(parameters)
        print(calculated_values)   
        not_started =False       
        values =calculated_values[0]


@webapp.route('/water-management/cecebre-dam/make-prediction', methods = ['POST'])
def make_prediction():
    global values
    not_started = True
              
    print('Started runner')
    json = request.json
    parameters = [
        float(json['water_flow']),
        float(json['rain_precipitation']),
        float(json['water_height'])
    ]
    #thread = threading.Thread(target=start_loop())
    #thread.start()  
    start_loop(parameters)
    while not_started:
        if(values!=-1):

            time.sleep(0.1)
            not_started =False         
        else:
            print("Waiting")                  
         
  
    return  {
        'predicted_values': {
            'water_flow': values
        }
    }

#print(make_prediction( ) )
if __name__ == "__main__":
    #predictor = WaterOutputPredictor('./conf/current_model_configuration.json')
    #predictor.predict_for([1.53, 10.2, 31.12])
    webapp.run(host="127.0.0.1",port=5000,threaded=False)
