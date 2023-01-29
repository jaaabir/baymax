from importlib.machinery import WindowsRegistryFinder
import re 
import spacy
from string import punctuation
from nltk.corpus import stopwords 
from nltk.stem import PorterStemmer
from num2words import num2words


nlp = spacy.load("en_core_web_md")
# symp_nlp = spacy.load("pt_models\en_ner_bc5cdr_md-0.5.1\en_ner_bc5cdr_md\en_ner_bc5cdr_md-0.5.1")
symp_nlp = spacy.load('en_core_sci_lg')
stop_words = set(stopwords.words())

def join_wordsV2(tokens, replace = {}):
    tkns = []
    txts = [t.text for t in tokens] 
    pos = [replace[i.pos_] if i.pos_ in replace.keys() else i.pos_ for i in tokens] + ['END']
    prev_txt_appended = False
    n = len(txts)
    for i in range(1, n + 1):
        curr_pos = pos[i]
        prev_pos = pos[i - 1]
        txt = None
        if curr_pos == prev_pos:
            if prev_txt_appended and len(tkns) > 0: # beta vers functionality
                tkns.pop()                          # beta vers functionality
            txts[i] = f"{txts[i - 1]} {txts[i]}"
            txt = txts[i]
            prev_txt_appended = True
        else:
            if prev_pos != 'PUNCT' and not prev_txt_appended:
                txt = txts[i - 1]
            elif i == (n - 1) and curr_pos != 'PUNCT':
                txt = txts[i]
            prev_txt_appended = False
        
        if txt:
            tkns.append(txt)
        
    return tkns


def adv_to_adj(doc):
  if doc[-2:] == 'ly':
    doc = doc[:-2]
  elif doc[-3:] == 'ing':
    doc = doc[:-3]
  return doc

def clean_text(text, keep_sw = [], keep_punct = '', nlp = nlp):
    # tokenize -> lemma -> remove stop words  -> clean text 
    punct = re.sub(r'[{}]'.format(keep_punct), '', punctuation)
    sws = stop_words - set(keep_sw)
    text = text.replace('.', ' dotpunct')
    tt = []
    for doc in nlp(text):
      if (doc.text not in sws):
        if re.search(r'[{}]'.format(keep_punct), doc.text):
          doc = doc.lemma_
        else:
          doc = re.sub(r'[{}]'.format(punct), '', doc.lemma_)
        if doc.isdigit():
          doc = num2words(doc).replace('-', ' ')
        tt.append(doc.replace('dotpunct', '.'))
    return ' '.join(tt)

def clean_textV2(sent):
    # lower -> lemma & POS
    txts = []
    pos = None
    stem = PorterStemmer()
    sent = re.sub(r'[{}]'.format(punctuation), '', sent.lower())
    for doc in nlp(sent):
        if doc.text not in stop_words:
            t = doc.lemma_
            # t = stem.stem(lem)
            txts.append(t)
            pos = doc.pos_
    return [' '.join(txts), pos]

def preprocess_pipeline(text, replace = {}, get_pos = 'NOUN'):
    clean_txt = []
    for t in join_wordsV2(nlp(text), replace = replace):
        txt, pos = clean_textV2(t)
        if pos == get_pos:
            clean_txt.append(txt)
    return clean_txt


def get_specified_pos(cleaned_text, pos = 'NOUN', verbose = True):
    if verbose:
        print(f'Extrating tokens based on {pos}')
    
    return {i[0] for i in cleaned_text if i[1] == pos}


def get_symptoms(text):
    return symp_nlp(text).ents


def remove_element_from_list(arr, ind):
    return arr[:ind] + arr[ind + 1:]