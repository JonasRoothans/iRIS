from classes.moduleManager import ModuleManager
from classes.module import Module
from datetime import date
import re
from collections import defaultdict
import json
import os
import yake
import numpy as np


def extract_keywords(text):
    language = "nl"
    max_ngram_size = 1
    deduplication_threshold = 1
    deduplication_algo = 'seqm'
    windowSize = 1
    numOfKeywords = 20

    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold,
                                                dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords,
                                                features=None)
    keywords = custom_kw_extractor.extract_keywords(text)

    #for kw in keywords:
     #   print(kw)
    all_keywords = [w[1] for w in keywords]
    return all_keywords


def load():
    mm = ModuleManager()

    for m_id in mm.all():
        m = Module(m_id)

        if m.date and m.get_date() > date(2022,4,22):
            mm.addmodule(m_id)

    mm.sort_chronological()
    return mm


def keywordAnalysis():
    mm = load()

    # Step 1: Aggregate keyword-to-module map and module-to-keywords map.
    keyword_map = dict(dict())


    for module in mm.modules:
        if not module.keywords:
            module.extract_keywords()
            module.save()

        print(module.title)
        for word in module.keywords:
            word_lower = word.lower()
            # If 'word' does not already exist in keyword_map, create a new nested dictionary for it
            if word_lower not in keyword_map:
                keyword_map[word_lower] = {}

            # Now update the nested dictionary with module.module_id as the key and module.keywords[word] as the value
            keyword_map[word_lower][module.module_id] = module.keywords[word]



    # Step 3: Compute relations
    relations = defaultdict(lambda: defaultdict(float))
    occurrences = [len(keyword_map[word]) for word in keyword_map]
    percentile_95 = np.percentile(occurrences, 95)

    keyword_map = {key: value for key, value in keyword_map.items() if len(value) <= percentile_95}

    #---Save
    directory_path = os.path.join('json','relations')

    file_path = os.path.join(directory_path, 'keyword_map.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(keyword_map, f, ensure_ascii=False, indent=4)
        f.flush() #some files were truncated, hopefully this helps
    #----

    for word, ids in keyword_map.items():
        print(word)
        if len(ids) > 1:  # Only consider keywords shared by more than one module
            unique_ids = list(ids.keys())  # Remove duplicates
            n_keyword_occurrences = len(unique_ids)


            for i_idx in range(len(unique_ids)):
                for j_idx in range(i_idx + 1, len(unique_ids)):  # Avoid double counting (i -> j == j -> i)
                    i = unique_ids[i_idx]
                    j = unique_ids[j_idx]

                    # Compute relation score for (i, j)
                    score = keyword_map[word][i] * keyword_map[word][j] / n_keyword_occurrences
                    relations[i][j] += score
                    relations[j][i] += score  # Relations are symmetric


    for module in mm.modules:
        print('\n-----------')
        print(module)
        weights = relations.get(module.module_id, {})
        sorted_weights = sorted(weights.items(), key = lambda x: x[1], reverse =True)

        filtered_weights = [item for item in sorted_weights if item[0] not in module.children]


        dict_weights = [{'id': t[0], 'weight': t[1]} for t in filtered_weights]
        module.related = dict_weights
        module.save()



    directory_path = os.path.join('json','relations')

    file_path = os.path.join(directory_path, 'keyword_map.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(keyword_map, f, ensure_ascii=False, indent=4)
        f.flush() #some files were truncated, hopefully this helps


    file_path = os.path.join(directory_path, 'relations.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(relations, f, ensure_ascii=False, indent=4)
        f.flush()  # some files were truncated, hopefully this helps