
import ast
from itertools import product
from collections import Counter
from nltk.util import ngrams

class Utils():

    def __init__(self) -> None:
        pass

    def get_attribute_type(self, word: str, dataset: str) -> tuple:
        # Convert the string to a Python list
        list_data = ast.literal_eval(dataset)

        # Create a dictionary from the list
        dictionary = {key.lower(): value for key, value in list_data}

        def jaccard_similarity(str1: str, str2: str, n: int) -> float:
            str1_ngrams = Counter(ngrams(str1, n))
            str2_ngrams = Counter(ngrams(str2, n))

            intersection = sum((str1_ngrams & str2_ngrams).values())
            union = sum((str1_ngrams | str2_ngrams).values())

            return float(intersection) / union

        book1_topics = list(dictionary.keys())
        book2_topics = [word]
        pairs = list(product(book1_topics, book2_topics))
        similarities = [jaccard_similarity(topic1, topic2, 2) for topic1, topic2 in pairs]
        similarity_pairs = list(zip(pairs, similarities, dictionary.values()))
        max_similarity_pair = max(similarity_pairs, key=lambda x: x[1])

        return max_similarity_pair
    
    def map_to_vis_domain(self, val, name):

        if(val.lower() in ["datetime", "date", "timestamp"]):
            return "temporal"
        
        if(val.lower() in ["char", "varchar", "varchar2", "text"]):
            return "nominal"
        
        if(val.lower() in ["real", "double", "float", "decimal", "boolean", "bool"]):
            return "quantitative"
        
        if(val.lower() in ["number", "int", "integer", "numeric"]): 
            if ("id" in name.lower()):
                return "ordinal"
            else :
                return "quantitative"