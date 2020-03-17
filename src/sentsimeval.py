import pandas as pd
import numpy as np
import zipfile
from sklearn.metrics.pairwise import cosine_similarity
from vectorizers.tfidfvectorgenerator import TfidfVectorGenerator
from vectorizers.doc2vecgenerator import Doc2VecGenerator
from vectorizers.sent2vecgenerator import Sent2VecGenerator
from vectorizers.bertgenerator import BertGenerator

class SentenceSimilarityEvaluation:
    def __init__(self, zipfilename,type):
        self.df = None
        self.vectorizers = {"tfidf":TfidfVectorGenerator(),
                            "doc2vec":Doc2VecGenerator(),
                            "bert":BertGenerator(),
                            "sent2vec":Sent2VecGenerator()}
        self.read_data(zipfilename)   
        all_questions = self.get_corpus()
        self.build_model(type,all_questions)
        
    def get_corpus(self):
        q1_column =  self.df["question1"].tolist()
        q2_column =  self.df["question2"].tolist()
        unique_qs = set(q1_column + q2_column)
        return list(unique_qs)
    
    def read_data(self,zipfilename):
        with zipfile.ZipFile(zipfilename) as z:
            csvfilename = zipfilename.replace("zip","csv")
            csvfilename = csvfilename.replace("data/","")
            print(csvfilename)
            with z.open(csvfilename) as f:
                self.df = pd.read_csv(f)
        self.df = self.df.drop(['id', 'qid1', 'qid2'], axis=1)
        self.df = self.df.dropna(axis = 0, how ='any') 

    def build_model(self,type,questions):
        self.vectorizer = self.vectorizers[type]
        self.vectorizer.vectorize(questions)
                
    def check_duplicate(self):
        computed_is_duplicate = []
        n_matching_rows = 0      

        for index, row in self.df.iterrows():
            if index == 10: # Checking only small sample
                break
            q1 = row['question1']
            q2 = row['question2']
            is_duplicate = row['is_duplicate']
            q1_array = self.vectorizer.query(q1)
            q2_array = self.vectorizer.query(q2)
            sims = cosine_similarity(q1_array, q2_array)
            c_is_duplicate = 0
            if sims[0][0] > 0.9:
                c_is_duplicate = 1
            computed_is_duplicate.append(c_is_duplicate)
            if c_is_duplicate == is_duplicate:
                n_matching_rows += 1
        accuracy = n_matching_rows / len(computed_is_duplicate)
        return accuracy
    
if __name__ == "__main__":
    csvfile = "data/quora_duplicate_train_small.zip"
    senteval = SentenceSimilarityEvaluation(csvfile,'doc2vec')
    accuracy = senteval.check_duplicate()
    print(accuracy)
