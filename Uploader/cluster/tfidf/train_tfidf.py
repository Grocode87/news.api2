import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD


def load_preprocessed_texts():
    with open("../../temp_data/processed_texts_140.txt", "r", encoding='utf-8') as f:
        return f.readlines()

texts = load_preprocessed_texts()
print("texts loaded")

tfidfVectorizer = TfidfVectorizer(max_df=0.85)
svd = TruncatedSVD(n_components=1400, n_iter=10, random_state=42)

print("training tfidf vectorizer")
vectors = tfidfVectorizer.fit_transform(texts)

print("training truncated svd")
svd.fit(vectors)

print("saving models")
pickle.dump(tfidfVectorizer, open("tfidf-140.p", "wb"))
pickle.dump(svd, open("svd-140.p", "wb"))
print("trained and saved models")
print("EXIT")