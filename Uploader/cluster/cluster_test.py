import json
from numpy import dot
import scipy
from numpy.linalg import norm
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

with open("temp_cluster_data.json", 'r', encoding="utf-8") as f:
    texts = json.load(f)['texts']
"""
processed_texts = []
for text in texts[:500]:
    processed_texts.append(word_tokenize(text.lower()))

model= Doc2Vec.load("d2v_2.model")

for document in processed_texts:
    for compare_doc in processed_texts:
        if not document == compare_doc:
            a = model.infer_vector(document)
            b = model.infer_vector(compare_doc)
            sim = scipy.spatial.distance.cosine(a, b)
            print(f"{' '.join(document[:20])} ---- {' '.join(compare_doc[:20])} ------ {sim}")
            print()
"""
