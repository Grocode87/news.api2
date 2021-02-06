import csv
import sys
from nltk.tokenize import word_tokenize
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)



texts = []
def get_text():
    for i in range(3):
        print(i)
        with open("../temp_data/news_dataset/articles" + str(i+ 1) + ".csv", 'r',encoding="latin1") as f:
            csv_reader = csv.reader(f, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    yield row    
                    line_count += 1
            print(f'Processed {line_count} lines.')

"""
for row in get_text():
    with open('../temp_data/news_dataset/processed_doc_texts.csv', 'a', encoding='latin1') as f:
        text = word_tokenize(row[9].lower())
        f.write(' '.join(text) + '\n')
"""


#print(f"Preprocessed {len(processed_texts)} texts")


class MyCorpus(object):
    def __iter__(self):
        with open('../temp_data/news_dataset/processed_doc_texts.csv', 'r', encoding='latin-1') as f:
            for i, line in enumerate(f):
                if line:
                    if len(line)>5:
                        yield TaggedDocument(words=line.split(), tags=[str(i)])

print("create model")

model = Doc2Vec(vector_size=200,
                min_count=2,
                dm =1)
print("building vocab")
model.build_vocab(MyCorpus())

print("training")
model.train(MyCorpus(), total_examples=model.corpus_count, epochs=50)

"""
print("starting to train model")

for epoch in range(150):
    print('iteration {0}'.format(epoch))
    model.train(MyCorpus(),
                total_examples=model.corpus_count,
                epochs=1)
    # decrease the learning rate
    model.alpha -= 0.0002
    # fix the learning rate, no decay
    model.min_alpha = model.alpha
    model.save("d2v_3.model")
"""
print("finished")

model.save("d2v_3.model")
print("Model Saved")