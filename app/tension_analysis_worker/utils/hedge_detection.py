import string

from nltk import ngrams
from nltk.metrics import jaccard_distance
from nltk.tokenize import word_tokenize

import global_config

from ..preload import discourse_markers, hedge_words, lmtzr, nlp


# ********* Disambiguate Hedge Terms ********* #
# ********* Returns true if (hedge) token is true hedge term, otherwise, returns false ********* #
def is_true_hedge_term(hedge, text):
    exclude = set(string.punctuation)

    if hedge == "assume":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[0] == "ccomp" and lmtzr.lemmatize(pair[1], 'v') == hedge:
                return True
        return False

    elif hedge == "appear":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if (pair[0] in ["xcomp", "ccomp"]) and lmtzr.lemmatize(pair[1], 'v') == hedge:
                return True
        return False

    elif hedge == "suppose":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[0] == "xcomp" and lmtzr.lemmatize(pair[1], 'v') == hedge:
                token = pair[2]
                for temp in tree:
                    if temp[0] == "mark" and temp[1] == token and temp[2] == "to":
                        return False
        return True

    elif hedge == "tend":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[0] == "xcomp" and lmtzr.lemmatize(pair[1], 'v') == hedge:
                return True
        return False

    elif hedge == "should":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[0] == "aux" and pair[2] == hedge:
                token = pair[1]
                for temp in tree:
                    if temp[1] == token and temp[2] == "have":
                        return False
        return True

    elif hedge == "likely":
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        for pair in tree:
            if pair[2] == hedge:
                token = pair[1]
                for temp in tree:
                    if temp[2] == token and temp[1] != "ROOT":
                        tag = nlp.pos_tag(temp[1])
                        if tag[0][1] in ["NN", "NNS", "NNP", "NNPS"]:
                            return False
        return True

    elif hedge == "rather":
        s = ''.join(ch for ch in text if ch not in exclude)
        list_of_words = s.split()
        next_word = list_of_words[list_of_words.index(hedge) + 1]
        if next_word == 'than':
            return False
        else:
            return True

    elif hedge == "think":
        words = word_tokenize(text)
        for i in range(len(words) - 1):
            if words[i] == hedge:
                tag = nlp.pos_tag(words[i + 1])
                if tag[0][1] == "IN":
                    return False
                    break
        return True

    elif hedge in ["feel", "suggest", "believe", "consider", "doubt", "guess", "presume", "hope"]:
        parse_trees = nlp.dependency_parse(text)
        tree = parse_trees[0]
        isRoot = False
        hasNSubj = False
        for pair in tree:
            if lmtzr.lemmatize(pair[2]) in [hedge] and pair[1] == "ROOT":
                isRoot = True
            elif lmtzr.lemmatize(pair[1]) in [hedge] and pair[0] == "nsubj":
                token = lmtzr.lemmatize(pair[1])
                subject = pair[2]
                hasNSubj = True

        if isRoot and hasNSubj:
            tags = nlp.pos_tag(text)
            status1 = False
            status2 = False
            for tag in tags:
                if lmtzr.lemmatize(tag[0]) == token and tag[1] in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                    status1 = True
                if subject.lower() in ["i", "we"]:
                    status2 = True
            if status1 and status2:
                return True
            else:
                return False


# ********* Determines if a sentence is hedged sentence or not ********* #
# ********* Returns true if sentence is hedged sentence, otherwise, returns false ********* #
def is_hedged_sentence(text):
    text = text.lower()

    if "n't" in text:
        text = text.replace("n't", " not")
    elif "n’t" in text:
        text = text.replace("n’t", " not")

    tokenized = word_tokenize(text)
    phrases = []
    status = False

    # Determine the n-grams of the given sentence
    for i in range(1, 6):
        phrases += ngrams(tokenized, i)

    # Determine whether hedge terms are present in the sentence and find out if they are true hedge terms
    for hedge in hedge_words:
        if hedge in tokenized and is_true_hedge_term(hedge, text):
            status = True
            break

    # Determine whether disocurse markers are present in the n-grams
    # Use Jaccard distance for measuring similarity
    if not status:
        for A in discourse_markers:
            for B in phrases:
                distance = 1 - jaccard_distance(set(A.split()), set(list(B)))
                if distance >= global_config.HEDGE_DETECTION_THRESHOLD:
                    status = True
                    break

            if status:
                break

    return status
