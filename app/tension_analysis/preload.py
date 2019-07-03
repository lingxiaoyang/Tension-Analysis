import csv
import pickle

from flask import current_app

from keras.models import load_model
from nltk.stem.wordnet import WordNetLemmatizer
from stanfordcorenlp import StanfordCoreNLP


__all__ = [
    'model',
    'lb',
    'tokenizer_tweets',
    'max_tweet_length',
    'tokenizer_hash_emo',
    'max_hash_emo_length',
    'boosters',
    'cues',
    'bingliu_mpqa',
    'nrc_emotion',
    'nrc_affect_intensity',
    'nrc_hashtag_emotion',
    'afinn',
    'ratings',
    'stopwords',
    'slangs',
    'negated',
    'emoticons',
    'lmtzr',
    'hedge_words',
    'discourse_markers',
    'nlp',
]


# Pre-trained model
current_app.logger.info('Loading pre-trained emotion recognition model...')

model = load_model(current_app.config['DATA_ROOT'] + 'models/model.h5')
with open(current_app.config['DATA_ROOT'] + 'models/variables-slim.p', 'rb') as f:
    lb, tokenizer_tweets, max_tweet_length, tokenizer_hash_emo, max_hash_emo_length = pickle.load(f)

boosters = []
with open(current_app.config['DATA_ROOT'] + "resources/booster_words.txt", 'r') as f:
    for line in f:
        if '#' not in line.strip():
            boosters.append(line.strip())

cues = []
with open(current_app.config['DATA_ROOT'] + "resources/cues.txt", 'r') as f:
    for line in f:
        if '#' not in line.strip():
            cues.append(line.strip())


# Emotion lexicons
current_app.logger.info('Loading emotion lexicons...')

bingliu_mpqa = {}
nrc_emotion = {}
nrc_affect_intensity = {}
nrc_hashtag_emotion = {}
afinn = {}
ratings = {}
stopwords = []
slangs = {}
negated = {}
emoticons = []


def load_emotion_lexicons():
    # Ratings by Warriner et al. (2013)
    with open(current_app.config['DATA_ROOT'] + 'lexicons/Ratings_Warriner_et_al.csv', 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    for i in range(1, len(rows)):
        # Normalize values
        valence = (float(rows[i][2]) - 1.0)/(9.0-1.0)
        arousal = (float(rows[i][5]) - 1.0)/(9.0-1.0)
        dominance = (float(rows[i][8]) - 1.0)/(9.0-1.0)
        ratings[rows[i][1]] = {"Valence": valence, "Arousal": arousal, "Dominance": dominance}

    # NRC Emotion Lexicon (2014)
    with open(current_app.config['DATA_ROOT'] + 'lexicons/NRC-emotion-lexicon-wordlevel-v0.92.txt', 'r') as f:
        f.readline()
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in nrc_emotion:
                nrc_emotion[splitted[0]] = {
                    'anger': float(splitted[1]),
                    'disgust': float(splitted[3]),
                    'fear': float(splitted[4]),
                    'joy': float(splitted[5]),
                    'sadness': float(splitted[8]),
                    'surprise': float(splitted[9])
                }

    # NRC Affect Intensity (2018)
    with open(current_app.config['DATA_ROOT'] + 'lexicons/nrc_affect_intensity.txt', 'r') as f:
        f.readline()
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in nrc_affect_intensity:
                nrc_affect_intensity[splitted[0]] = {
                    'anger': float(splitted[1]),
                    'disgust': float(splitted[3]),
                    'fear': float(splitted[4]),
                    'joy': float(splitted[5]),
                    'sadness': float(splitted[8]),
                    'surprise': float(splitted[9])
                }

    # NRC Hashtag Emotion Lexicon (2015)
    with open(current_app.config['DATA_ROOT'] + 'lexicons/NRC-Hashtag-Emotion-Lexicon-v0.2.txt', 'r') as f:
        f.readline()
        for line in f:
            splitted = line.strip().split('\t')
            splitted[0] = splitted[0].replace('#', '')
            if splitted[0] not in nrc_hashtag_emotion:
                nrc_hashtag_emotion[splitted[0]] = {
                    'anger': float(splitted[1]),
                    'disgust': float(splitted[3]),
                    'fear': float(splitted[4]),
                    'joy': float(splitted[5]),
                    'sadness': float(splitted[8]),
                    'surprise': float(splitted[9])
                }

    # BingLiu (2004) and MPQA (2005)
    with open(current_app.config['DATA_ROOT'] + 'lexicons/BingLiu.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in bingliu_mpqa:
                bingliu_mpqa[splitted[0]] = splitted[1]
    with open(current_app.config['DATA_ROOT'] + 'lexicons/mpqa.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in bingliu_mpqa:
                bingliu_mpqa[splitted[0]] = splitted[1]

    with open(current_app.config['DATA_ROOT'] + 'lexicons/AFINN-en-165.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in afinn:
                score = float(splitted[1])
                normalized_score = (score - (-5)) / (5-(-5))
                afinn[splitted[0]] = normalized_score

    with open(current_app.config['DATA_ROOT'] + 'lexicons/stopwords.txt', 'r') as f:
        for line in f:
            stopwords.append(line.strip())

    with open(current_app.config['DATA_ROOT'] + 'lexicons/slangs.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split(',', 1)
            slangs[splitted[0]] = splitted[1]

    with open(current_app.config['DATA_ROOT'] + 'lexicons/negated_words.txt', 'r') as f:
        for line in f:
            splitted = line.strip().split(',', 1)
            negated[splitted[0]] = splitted[1]

    with open(current_app.config['DATA_ROOT'] + 'lexicons/emoticons.txt', 'r') as f:
        for line in f:
            emoticons.append(line.strip())


load_emotion_lexicons()


# Load hedge lexicons
current_app.logger.info('Loading hedge lexicons...')

lmtzr = WordNetLemmatizer()
hedge_words = []
discourse_markers = []


def load_hedge_lexicons():
    with open(current_app.config['DATA_ROOT'] + "resources/hedge_words.txt", "r") as f:
        for line in f:
            if '#' in line:
                continue
            elif line.strip() != "":
                hedge_words.append(line.strip())

    with open(current_app.config['DATA_ROOT'] + "resources/discourse_markers.txt", "r") as f:
        for line in f:
            if '#' in line:
                continue
            elif line.strip() != "":
                discourse_markers.append(line.strip())


load_hedge_lexicons()


# Load NLP server Python interface
current_app.logger.info('Loading StanfordCoreNLP Python interface...')
nlp = StanfordCoreNLP('http://stanford_nlp:9999', port=9999)
