# author : muhammed jaabir
# python version : 3.8.2

import configparser
from warnings import filterwarnings as filt 
from butils import clean_text, get_symptoms, remove_element_from_list
from collections import Counter 
from datetime import datetime 
from api.graph import App
import pandas as pd
from sys import exit
import py2neo
import random 
import aiml 
import re
import json
from spellchecker import SpellChecker 
import os 


def greetings_day():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    if hour >= 0 and hour <= 12:
        day = 'morning'
    elif hour == 12 and minute == 0:
        day = 'noon'
    elif hour >= 12 and hour <= 16:
        day = 'afternoon'
    else:
        day = 'evening'
        
    return day
    

def start_greeting(return_ = False):
    greetings = [
        'hi, my name is baymax. ',
        f'good {greetings_day()}, '
    ]
    
    if return_:
        return random.choice(greetings).capitalize() + ' ' + 'how can i help you today ?'.capitalize()
    print('bb >>> ' + random.choice(greetings).capitalize(), end = ' ')
    print('how can i help you today ?'.capitalize())
    
def info(txt):
    print(f'bb  >>> {txt.capitalize()}')
    
def get_basic_details(return_ = False):
    if return_:
        return ['what is your name ?', 'what is your age ?', 'do you have the habit of drinking or smoking ? (y/n)', 'what are your currently experiencing symptoms ?']
    info('what is your name ?')
    name = input('MSG  >>> ')
    info('what is your age ?')
    age = int(input('MSG  >>> '))
    info('do you have the habit of drinking or smoking ? (y/n)')
    drink_smoke = input('MSG  >>> ')[0]
    return name, age, drink_smoke

def get_all_diseases(symptoms : list, n_diseases = 3, recursive = False):
    ### how it works :
    # this func will get one disease based on the specified symptom and then iterate more symptoms if there 
    # are any more in the list. if it dont find any symptom in middle of the traversal it will erase that symptom 
    # and move on to the next symptom for attaining the global minima. 
    ### cons / improvement :
    # must also consider the removed symptoms from the sub graph, because the patient is describing what they are experiencing. 
    if symptoms == []:
        return pd.DataFrame({'s': [], 'd': []})
    
    related_symp = pd.DataFrame({'d' : [], 's' : []})
    different_symp = pd.DataFrame({'d' : [], 's' : []})
    
    leng = len(symptoms)
    for i in range(leng):
        symps = symptoms[: i+1]
        ddf, nd = nominate_diseases(symps)
        if nd > 0:
            related_symp = get_all_symptoms(ddf.d.values)[0]
        else:
            if recursive:
                return pd.DataFrame({'s': [], 'd': []})
            # different_symp = pd.concat([different_symp, get_all_symptoms([symptoms[i]])[0]])
            different_symp = pd.concat([different_symp, get_all_diseases([symptoms[i]], n_diseases, True)])
            symptoms = remove_element_from_list(symptoms, i)
            
    return pd.concat([related_symp, different_symp]).drop_duplicates(['d', 's'])

def nominate_diseases(symptoms):
    query = "match (s1:SYMPTOM)-->(d:DISEASE), {path} where {condition} return d"
    p = ', '.join([f'(s{i + 2}:SYMPTOM)-->(d)' for i in range(len(symptoms) - 1)])
    if p == '':
        query = query.replace(',', '')
    c = ' and '.join([f"s{i + 1}.name contains '{symptom}'" for i, symptom in enumerate(symptoms)])
    query = query.format(path = p, condition = c)
    return traverse_graph(query)

def get_all_symptoms(diseases : list):
    query = "match (d:DISEASE)-->(s:SYMPTOM) where {condition} return d,s"
    c = ' or '.join([f"d.name contains '{disease}'" for disease in diseases])
    query = query.format(condition = c)
    return traverse_graph(query)
        
def traverse_graph(query):
    graph = App(uri, username, password)
    df = pd.DataFrame({'d' : [], 's' : []})
    
    sdf = (graph.custom_query(query))
    for key in sdf.columns:
        df[key] = sdf[key].apply(lambda x : x['name'])
        
    print(query)
    print(df.d.unique())
    n_diseases = df.iloc[:, 0].unique().shape[0]
    return df.drop_duplicates(['d', 's']), n_diseases

def recommend_symptoms(df, n_symptoms = 3):
    disease = Counter(df.d.values).most_common(1)[0]
    symptom = df.iloc[:, 0].sample(3).values.tolist()
    return symptom

def accuracy(n, N):
    return n/N

def predict_diseases(df, symptoms, top = 3):
    diseases = []
    # print('some' in symptoms, type(symptoms[0].text))
    for d, rdf in df.groupby('d'):
        score = 1
        for s in rdf.s:
            for sym in symptoms:
                if s == sym.text:
                    score -= 0.01
        diseases.append((d, score))
                
    return sorted(diseases, key = lambda x : x[1])[:top]

def clean_simp(symptoms):
    s = [i.strip().lower() for i in re.split(r",|, | , ", symptoms)] if str(symptoms) != 'nan' else []
    return s 

def print_bb(response):
    print(f"bb  >>> {response}")
    
    
def read_json(fname):
    with open(fname, 'r') as file:
        f = json.load(file)
    return f

def check_typos(txt : list, new_txt : list, changed_ : list) -> tuple : 
    nt = []
    for ind, i in enumerate(changed_):
        nt.append(new_txt[ind])
        if i:
            print_bb(f'did you mean {new_txt[ind]} ? (y/n)')
            to_change = input('MSG >>> ').lower()
            if to_change[0] == 'n':
                nt.append(txt[ind])  
    return ' '.join(nt)
            
    
def chat(**kwargs):
    STOP_CONVO = False
    while not STOP_CONVO:
        text = input('MSG >>> ').lower()
        response = (kernel.respond(text)).capitalize()
        if response:
            print_bb(response)
        else:
            # preprocess and analyze the user text
            if text == 'yes' or text == 'y':
                print_bb("Please specify your symptoms")
            elif text == 'no' or text == 'n':
                STOP_CONVO = True
            else:
                text = clean_text(text, ['and', 'or'], ',.')
                print(text)
                nt, ch = kwargs['spelling'].check(text)
                text = check_typos(text.split(), nt, ch)
                symps = get_symptoms(text)
                if VERBOSE:
                    print(symps)
                user_details['symptoms'] += [symp for symp in symps]
                print_bb("Do you have anymore symptoms ? (yes/no)")
    

def main():
    corpus = read_json(os.path.join('dataset', 'corpus.json'))['symptoms']
    spelling = SpellChecker(update_word_probs = True, corpus = corpus, verbose = VERBOSE)
    spelling.vocabBuilder.add_to_dictionary(words =  [',', '.'])    
    start_greeting()   
    name, age, drink_smoke = get_basic_details()    
    user_details['name'] = name
    user_details['age'] = age
    user_details['drink_smoke'] = drink_smoke
    info('what are your currently experiencing symptoms ?')
    chat(spelling = spelling)
    
    print('collected symptoms \n {s} \n'.format(s = user_details['symptoms']))
    
    diseases = get_all_diseases(user_details['symptoms'])
    if VERBOSE:
        print(diseases)
    top_diseases = predict_diseases(diseases, user_details['symptoms'], top = 2)

    print('\nYou are more likely to have the following diseases '.center(60, '='))
    for d, score in top_diseases:
        print()
        print(f'{d.capitalize()} | {1 - score}')
      
        
if __name__ == "__main__":
    
    cfilename = 'config.ini' 
    config = configparser.ConfigParser()
    config.read(cfilename)
    CONFIG = config['graph']
    uri, username, password = CONFIG['uri'], CONFIG['username'], CONFIG['password']
    if not (uri and username and password):
        print('Store your Neo4j URI, username and password in config.ini file')
        exit()  
        
    VERBOSE = True
    xml_filename = 'std-startup.xml'
    pattern = "load aiml b"
    kernel = aiml.Kernel()
    kernel.learn(xml_filename)
    kernel.respond(pattern)

    if not VERBOSE:
        print('Running in production mode ...')
        print('All further warnings are ignored ...')
        filt('ignore')
    else:
        print('Running in development mode ...\n')


    user_details = {
        'name'   : None,
        'age'    : None,
        'drink_smoke' : None,
        'symptoms' : [],
        'effect_of_disease' : None,
        'predicted_diseases' : []
    }
    
    try:
        main()
    except py2neo.errors.ServiceUnavailable as err:
        print('Please start the Neo4j graph DB first ...')
        
        
# def traverse_graph(symptoms : list, n_diseases = 3, return_query = False):
#     ### how it works :
#     # this func will get one disease based on the specified symptom and then iterate more symptoms if there 
#     # are any more in the list. if it dont find any symptom in middle of the traversal it will erase that symptom 
#     # and move on to the next symptom for attaining the global minima. 
#     ### cons / improvement :
#     # must also consider the removed symptoms from the sub graph, because the patient is describing what they are experiencing. 
#     if symptoms == []:
#         return pd.DataFrame({'s': [], 'd': []})
#     query         = 'match {traversal} {condition} return {svar}, {dvar}'
#     symptom_node  = "({svar}:SYMPTOM)"
#     relation_sd   = "-[:SYMPTOMS_OF]->"
#     relation_ds   = "-[:SYMPTOMS]->"
#     disesase_node = "({dvar}:DISEASE)"   
#     traversal     = (
#                     symptom_node.format(svar = 's1') + relation_sd + disesase_node.format(dvar = 'd1')
#                     + relation_ds + symptom_node.format(svar = 's2')
#                     )
#     condition     = "where {csvar}.name =~ '{symptom}'"
#     updated_condition = condition.format(csvar = 's1', symptom = symptoms[0])
#     print(query.format(traversal = traversal, condition = updated_condition, svar = 's2', dvar = 'd1'))
#     df, leng = get_all_diseases(query.format(traversal = traversal, condition = updated_condition, svar = 's2', dvar = 'd1'))
#     total_symptoms = len(symptoms)  
#     if leng > 1:
#         # condition += 'and' + condition[4:].format(svar = 's2', symptom = symptoms[1])
#         end_char_trav_leng = len(traversal)
#         end_char_cond_leng = len(updated_condition)
#         end_traversal = False
#         for ind, symptom in enumerate(symptoms[1:]):            
#             ind = ind + 2
#             traversal += relation_sd + disesase_node.format(dvar = f'd{ind}') + relation_ds + symptom_node.format(svar = f's{ind + 1}')
#             updated_condition += ' and' + condition[5:].format(csvar = f's{ind}', symptom = symptom)
#             print(query.format(traversal = traversal, condition = updated_condition, svar = f's{ind + 1}', dvar = f'd{ind}'))
#             sdf, leng = get_all_diseases(query.format(traversal = traversal, condition = updated_condition, svar = f's{ind + 1}', dvar = f'd{ind}'))
            
#             if leng == 0:
#                 traversal = traversal[:end_char_trav_leng]
#                 updated_condition = updated_condition[:end_char_cond_leng]
#             else:
#                 df = pd.concat([df, sdf])
#                 end_char_trav_leng = len(traversal)
#                 end_char_cond_leng = len(updated_condition)
                
#     return df


# def get_all_diseases(symptoms):
#     label = 'SYMPTOM'
#     graph = App(CONFIG['uri'], CONFIG['username'], CONFIG['password'])
#     df = pd.DataFrame({
#         's' : [],
#         'd' : [],
#     })
#     for name in symptoms:
#         query = f'MATCH (s:{label})-[r:SYMPTOMS_OF]->(d:DISEASE) where s.name contains "{name}" return s, d'
#         query = f"MATCH (s:{label} {{name : '{name}'}})-[r:SYMPTOMS_OF]->(d:DISEASE) return s, d"
#         sdf = (graph.custom_query(query))
#         try:
#             sdf["s"] = sdf["s"].apply(lambda x : x['name'])
#             sdf["d"] = sdf["d"].apply(lambda x : x['name']) 
#             df = pd.concat([df, sdf], axis = 0)
#         except KeyError as err:
#             pass
        
#     return df.drop_duplicates(['s', 'd'])
        
        
        