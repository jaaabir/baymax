from flask import Flask, request, jsonify
from baymax import read_json, start_greeting, get_basic_details, check_typos, get_symptoms, get_all_diseases, predict_diseases
from spellchecker import SpellChecker
from butils import clean_text
from datetime import datetime
import configparser
from flask_cors import CORS
from db import MonDb, LocDb
import py2neo
import aiml 
import os

app = Flask(__name__)
CORS(app)

def check_y_n(text):
    return 'y/n' in text

def get_bot_response(user_res):
    
    text = user_res.lower()
    response = (kernel.respond(text)).capitalize()
    STOP_CONVO = False
    symptoms = []
    if not response:
        if text == 'yes' or text == 'y':
            response = "Please specify your symptoms"
        elif text == 'no' or text == 'n':
            response = 'Analysing your symptoms, please wait while we process your information'
            STOP_CONVO = True
        else:
            text = clean_text(text, ['and', 'or'], ',.')
            nt, ch = spelling.check(text)
            # text = check_typos(text.split(), nt, ch).replace('experience', '')
            text = ' '.join(nt)
            symps = get_symptoms(text)
            if DEVELOPER_MODE:
                print(symps)
            symptoms += [str(symp) for symp in symps]
            response = "Do you have anymore symptoms? (y/n)"
        
    return response, check_y_n(response), symptoms, STOP_CONVO


def Date():
    r = r"%a %b %y %H:%M:%S"
    return datetime.now().strftime(r)


@app.post('/api/getsymps')
def detect_symptoms():
    
    res = request.get_json()
    userId = res['userId']
    userRes = res['message']
    botRes, isYn, symptoms, stop_convo = get_bot_response(userRes)
    JDB.add_user_symp(userId, symptoms)
    data = {
      "userId": userId,
      "body": {
        "message": botRes,
        "isUser": False,
        "type": {
          "yesNo": isYn,
          "selected": None,
        },
        "msgTime": Date(),
        "endConvo": stop_convo,
      },
      "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
    }     
    return jsonify(data)


@app.post('/api/savechat')
def update_history():
    userId  = request.get_json()['userId']
    history = request.get_json()['history']
    print(history)
    return jsonify({
        'success' : True,
        'code'    : 200 
    })

if __name__ == '__main__':
    DEVELOPER_MODE = True
    
    ### initializing configs 
    cfilename = 'config.ini' 
    config = configparser.ConfigParser()
    config.read(cfilename)
    DB = config['DB']
    GRAPH = config['graph']
    
    ### initializing dbs
    uri = DB['uri']
    filename = DB['filename']
    JDB = LocDb(filename)
    
    xml_filename = 'std-startup.xml'
    pattern = "load aiml b"
    kernel = aiml.Kernel()
    kernel.learn(xml_filename)
    kernel.respond(pattern)
    
    try:
        corpus = read_json(os.path.join('datasets', 'corpus.json'))['symptoms']
        spelling = SpellChecker(update_word_probs = True, corpus = corpus, verbose = DEVELOPER_MODE)
        spelling.vocabBuilder.add_to_dictionary(words =  [',', '.'])  
        app.run(debug = DEVELOPER_MODE, port = 6969)
    except py2neo.errors.ServiceUnavailable as err:
        print('Please start the Neo4j graph DB first ...')
        
        
        
        
# if user_res.strip() != '' and user_res != history[-1]['message']:
        
    #     bot_res, is_yes_or_no, stop_convo = get_bot_response(user_res)
    #     bot_data = {
    #             'message' : bot_res,
    #             'is_user' : False,
    #             'yes_no'  : is_yes_or_no,
    #             'class_'  : f'col s6 bot', 
    #             'end_convo' : stop_convo,
    #             'diseases' : [],
    #             'test' : []
    #         }
        
        
    #     if stop_convo:
    #         diseases = get_all_diseases(user_details['symptoms'])
    #         if DEVELOPER_MODE:
    #             print(diseases)
    #         history[-1]['diseases'] = predict_diseases(diseases, user_details['symptoms'], top = 3)
    