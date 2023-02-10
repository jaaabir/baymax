from server_api.db import MonDb
import streamlit as st
import numpy
import pandas as pd
import matplotlib.pyplot as plt
from server_api.api.graph import App
from configparser import ConfigParser
import os
import sys
from collections import Counter

#from streamlit import cli as stcli


def main():
    if 'detected_symptoms' not in st.session_state:
        st.session_state.detected_symptoms = 'value'

    if 'diseases' not in st.session_state:
        st.session_state.diseases = 'value'
    print(st.session_state['detected_symptoms'])

    col1 = st.container()
    col2 = st.container()
    col3 = st.container()

    col1, col2, col3 = st.columns(3)
    refresh()
    btn = st.button('refresh')
    if btn:
        refresh()
    common_symptoms()
    common_pred_diseases()


def refresh():

    mondb = MDB.get_data()
    query = "MATCH (s)-[r] -> (d) RETURN s, d"

    detected_simp = []
    disease = []
    for i in mondb:
        disease += [i[0] for i in i['diseases']]
        detected_simp += i['detected_symptoms']

    cq = GAp.custom_query(query)
    print(cq)

    st.session_state['detected_symptoms'] = detected_simp
    st.session_state['diseases'] = disease
    # return mondb, cq


def common_symptoms():
    counts = Counter(st.session_state['detected_symptoms']).most_common()
    df_counts = pd.DataFrame(counts, columns=['symp', 'count'])
    print(df_counts)
    fig, x = plt.subplots()
    x.pie(df_counts['count'], labels=df_counts['symp'], autopct='%1.1f%%')
    st.pyplot(fig)


def common_pred_diseases():
    counts = Counter(st.session_state['diseases']).most_common()
    df_counts = pd.DataFrame(counts, columns=['dis', 'count'])
    print(df_counts)
    fig, x = plt.subplots()
    x.pie(df_counts['count'], labels=df_counts['dis'], autopct='%1.1f%%')
    st.pyplot(fig)


if __name__ == "__main__":

    cfilename = os.path.join('server_api', 'config.ini')
    config = ConfigParser()
    config.read(cfilename)
    DB = config['DB']
    GRAPH = config['graph']

    # initializing dbs
    passwd = DB['password']
    uri = DB['uri'].format(passwd)
    db_name = DB['dbname']
    collection = DB['collection']

    try:
        MDB = MonDb(uri, db_name, collection)
    except:
        uri = DB['uri2'].format(passwd)
        MDB = MonDb(uri, db_name, collection)

    GAp = App(GRAPH['uri'], GRAPH['username'], GRAPH['password'])
    # if st._is_running_with_streamlit:
    #     main()
    # else:
    #     sys.argv = ["streamlit", "run", sys.argv[0]]
    #     sys.exit(stcli.main())

    main()
