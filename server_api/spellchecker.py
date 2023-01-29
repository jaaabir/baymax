from turtle import update
from nltk.corpus import words
import spacy
from collections import Counter 
from time import time 
from string import punctuation
import re 
import json 

class Dict:
  def __init__(self):
    self.dictionary = set(words.words())

  def find(self, word : str) -> bool:
    return word in self.dictionary
  
  def add(self, word : str) -> None:
    self.dictionary.add(word)

  def delete(self, word : str) -> bool: 
    if self.find(word):
      self.dictionary.remove(word)
      return True
    return False

class BuildVocab(Dict):
  def __init__(self):
    super().__init__()
    self.alphabets = [chr(i) for i in range(97, 97+26)]

  def get_vocab(self, word : str) -> set:
    word = word.lower()
    n = len(word)
    vocabs = self.insert(word, n) + self.remove(word, n) + self.switch(word, n) + self.replace(word, n)
    return set(vocabs)

  def insert(self, word : str, n : int) -> list:
    vocabs = []
    for i in range(1, n + 1):
      lword = list(word)
      lword.insert(i, '')
      for a in self.alphabets:
        lword[i] = a 
        nword = ''.join(lword)
        if self.find(nword) and nword != word:
          vocabs.append(nword)

    return vocabs
  
  def remove(self, word : str, n : int) -> list:
    vocabs = []
    for i in range(n):
      lword = list(word)
      lword.remove(lword[i])
      nword = ''.join(lword)
      if self.find(nword) and nword != word:
        vocabs.append(nword)

    return vocabs

  def switch(self, word : str, n : int) -> list:
    vocabs = []
    lword = list(word)
    for i in range(n - 1):
      lword[i], lword[i + 1] = lword[i + 1], lword[i]
      nword = ''.join(lword)
      if self.find(nword) and nword != word:
        vocabs.append(nword)
      lword[i], lword[i + 1] = lword[i + 1], lword[i]

    return vocabs

  def replace(self, word : str, n : int) -> list:
    vocabs = []
    for i in range(n):
      lword = list(word)
      for a in self.alphabets:
        lword[i] = a
        nword = ''.join(lword)
        if self.find(nword) and nword != word:
          vocabs.append(nword)

    return vocabs

  def delete_if_not_found(self, vocabs : list) -> list:
    corpus = []
    for word in vocabs:
      if self.find(word):
        corpus.append(word)
    
    return corpus

  def add_to_dictionary(self, words : list) -> None:
    for i, w in enumerate(words):
      self.add(w)
    print(f'Added {i + 1} new words to the dictionary ...')
    
class SpellChecker:
  def __init__(self, update_word_probs : bool = False, corpus : list = [], ignore_punct = True, verbose : bool = False):

    st = time()

    self.ignonre_punct = ignore_punct
    self.vocabBuilder = BuildVocab()
    self.nlp = spacy.load("en_core_web_md")
    self.cache = {
        'table' : None,
        'r'     : 0,
        'c'     : 0
    }
    self.word_probabilities = {}
    self.total_words = 0
    self.update_word_probs = update_word_probs
    if update_word_probs:
        assert corpus, "corpus should not be none if update word probs is set to [TRUE]"
        self.total_words = self.update_word_probabilities(corpus)
    
    ed = time()
    if verbose:
      print()
      print(f'loaded the model in : {round(ed - st, 2)} sec(s) ...')
  
  def check(self, text : str) -> str:
    new_text = [] # strings
    changed  = [] # bools
    text = self.clean_(text, return_tokens = True)
    total_words = self.update_word_probabilities(text)
    for doc in text:
      text = doc.text
      if not self.vocabBuilder.find(text):
        vocab = self.vocabBuilder.get_vocab(text)
        self.update_word_probabilities(vocab)
        top_suggestion_words = self.get_top_suggestions(text, vocab, total_words)  # have to edit this in the main script file ( compute the word count probs for all the symptoms )
        # top_suggestion_words = list(vocab)
        if len(top_suggestion_words) > 0:
          top_word = [top_suggestion_words[0][0], self.min_edit_distance(text, top_suggestion_words[0])[1]]
          for target in top_suggestion_words[1:]:
            _, distance = self.min_edit_distance(text, target)
            if distance < top_word[1]:
              top_word = [target[0], distance]
          new_text.append(top_word[0])
          changed.append(True)
        else:
          new_text.append(text)
          changed.append(False)
      else:
        new_text.append(text)
        changed.append(False)
    return new_text, changed

  def get_top_suggestions(self, word, vocabs, total_words, top_n = 15):
    print(vocabs)
    print()
    suggestions = []
    for vocab in vocabs:
      print(vocab, total_words, self.compute_word_probabilty(self.word_probabilities[vocab], total_words))
      suggestions.append([vocab, self.compute_word_probabilty(self.word_probabilities[vocab], total_words)])
    print(suggestions, word)
    if len(suggestions) > 0:
      return list(zip(sorted(suggestions, key = lambda x : x[1], reverse = True)[:top_n]))[0]
    return suggestions

  def min_edit_distance(self, source : str, target : str):
    r = len(source)
    c = len(target)
    table = self.build_matrix(r, c)
    for row in range(1, r + 1):
      for col in range(1, c + 1):
        s,t = source[row - 1], target[col - 1]
        rep_ = table[row - 1][col - 1] + 2 if s != t else table[row - 1][col - 1]
        id_  = table[row - 1][col] + 1
        di_  = table[row][col - 1] + 1  
        table[row][col] = min(rep_, id_, di_)
    
    return table, table[row][col]

  def build_matrix(self, r, c):
    if (r == self.cache['r']) and (c == self.cache['c']):
      return self.cache['table']

    mat = [[0] * (c + 1) for _ in range(r + 1)]
    mat[0] = [i for i in range(c + 1)]
    for i in range(1, r + 1):
      mat[i][0] = i 
    self.cache['table'] = mat
    self.cache['r'] = r
    self.cache['c'] = c

    return mat  

  def get_word_count(self, text):
    c = Counter(text)
    n = sum(c.values())
    return dict(c), n

  def clean_(self, text, return_tokens = False):
    # text = text.lower()
    # text = re.sub(r'[.,]', ' ', text)
    # text = re.sub(r'[{}]'.format(punctuation), '', text)
    if return_tokens:
      text = [i for i in self.nlp(text) if i.text.strip() != '']
    return text

  def compute_word_probabilty(self, word_frequency, total_words):
    return word_frequency / total_words

  def update_word_probabilities(self, words : list) -> int:
    if self.update_word_probs:
      n = self.total_words
      for word in words:
        if self.vocabBuilder.find(word):
          if word in self.word_probabilities.keys():
            self.word_probabilities[word] += 1
            # n += (self.word_probabilities[word] - 1)
            n += 1
          else:
            self.word_probabilities[word] = 1
    else:
      self.word_probabilities, n = self.get_word_count(words)

    return n
