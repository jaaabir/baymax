from time import time 

def merge_corpus(corpus, text):
    new_corpus = []
    split_by = '\n'

    for lines in corpus[:-1].split(split_by):
        new_corpus.append(lines)
        
    for lines in text.split(split_by):
        new_corpus.append(lines)
    
    new_corpus.append(corpus[-1])
    
    return '\n'.join(new_corpus)

def start_automation(text, filename = 'basic_chat.aiml', backup = True):
    with open(filename, 'r') as file:
        corpus = file.read()
        
    if backup:
        with open(f'{filename[:-5]}_bk.aiml', 'w') as file:
            file.write(corpus)
        
    new_corpus = merge_corpus(corpus, text)
    
    with open(filename, 'w') as file:
        file.write(new_corpus)
        
def query_texts(questions, responses):
    sample_text = '''
    <category>
        <pattern>{}</pattern>
        <template>{}</template>
    </category>
'''

    queried_texts = []
    
    for i in range(len(questions)):
        question = questions[i].upper()
        response = responses[i]
        text = sample_text.format(question, response)
        queried_texts.append(text)
        
    return '\n'.join(queried_texts)

def main():
    questions = []
    responses = []
    text = query_texts(questions, responses)
    start_automation()
    
if __name__ == "__main__":
    main()