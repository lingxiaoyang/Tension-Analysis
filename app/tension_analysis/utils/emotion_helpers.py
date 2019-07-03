from tension_analysis.packages import *


def clean_texts(texts):
    cleaned_tweets = []
    hash_emos = []

    for text in texts:
        hash_emo = []
        text = re.sub('(!){2,}', ' <!repeat> ', text)
        text = re.sub('(\?){2,}', ' <?repeat> ', text)

        # Tokenize using tweet tokenizer
        tokenizer = TweetTokenizer(strip_handles=False, reduce_len=True)
        tokens = tokenizer.tokenize(text.lower())
        lemmatizer = WordNetLemmatizer()


        # Emojis and emoticons
        if text_has_emoji(text):
            temp = []
            for word in tokens:
                if char_is_emoji(word):
                    hash_emo.append(UNICODE_EMOJI[word])
                elif word in emoticons:
                    hash_emo.append(word)
                else:
                    temp.append(word)
            tokens = temp

        # Hashtags
        temp = []
        for word in tokens:
            if '#' in word:
                word = word.replace('#','')
                hash_emo.append(word)
            else:
                temp.append(word)
        tokens = temp

        # Replace slangs and negated words
        temp = []
        for word in tokens:
            if word in slangs:
                temp += slangs[word].split()
            elif word in negated:
                temp += negated[word].split()
            else:
                temp.append(word)
        tokens = temp

        # Replace user names
        tokens = ['<user>'  if '@' in word else word for word in tokens]

        #Replace numbers
        tokens = ['<number>' if word.isdigit() else word for word in tokens]

        # Remove urls
        tokens = ['' if 'http' in word else word for word in tokens]

        # Lemmatize
        #tokens = [lemmatizer.lemmatize(word) for word in tokens]

        # Remove stop words
        tokens = [word for word in tokens if word not in stopwords]

        # Remove tokens having length 1
        tokens = [word for word in tokens if word != '' and len(word) > 1]

        cleaned_tweets.append(tokens)
        hash_emos.append(hash_emo)

    return cleaned_tweets, hash_emos


# This function returns a n-dimensional feature vector
def feature_generation(texts, hashtags):
    analyzer = SentimentIntensityAnalyzer()
    feature_dimension = 29
    feature_vectors = []

    for i in range(len(texts)):
        feats = [0] * feature_dimension
        for word in texts[i]:
            # Warriner er al.
            if word in ratings:
                feats[0] += ratings[word]['Valence']
                feats[1] += ratings[word]['Arousal']
                feats[2] += ratings[word]['Dominance']

            # Vader Sentiment
            polarity_scores = analyzer.polarity_scores(word)
            feats[3] += polarity_scores['pos']
            feats[4] += polarity_scores['neg']
            feats[5] += polarity_scores['neu']

            # NRC Emotion
            if word in nrc_emotion:
                feats[6] += nrc_emotion[word]['anger']
                feats[7] += nrc_emotion[word]['disgust']
                feats[8] += nrc_emotion[word]['fear']
                feats[9] += nrc_emotion[word]['joy']
                feats[10] += nrc_emotion[word]['sadness']
                feats[11] += nrc_emotion[word]['surprise']

            # NRC Affect Intensity
            if word in nrc_affect_intensity:
                feats[12] += nrc_affect_intensity[word]['anger']
                feats[13] += nrc_affect_intensity[word]['disgust']
                feats[14] += nrc_affect_intensity[word]['fear']
                feats[15] += nrc_affect_intensity[word]['joy']
                feats[16] += nrc_affect_intensity[word]['sadness']
                feats[17] += nrc_affect_intensity[word]['surprise']

            # AFINN
            if word in afinn:
                feats[18] += float(afinn[word])

            # BingLiu and MPQA
            if word in bingliu_mpqa:
                if bingliu_mpqa[word] == 'positive':
                    feats[19] += 1
                else:
                    feats[20] += 1


        count = len(texts[i])
        if count == 0:
            count = 1
        newArray = np.array(feats)/count
        feats = list(newArray)

        # Presence of consecutive exclamation mark or question mark
        for word in texts[i]:
            if word == '<!REPEAT>':
                feats[21] = 1
            elif word == '<?REPEAT>':
                feats[22] = 1

        for word in hashtags[i]:
            #NRC Hashtag Emotion
            if word in nrc_hashtag_emotion:
                feats[23] += nrc_hashtag_emotion[word]['anger']
                feats[24] += nrc_hashtag_emotion[word]['disgust']
                feats[25] += nrc_hashtag_emotion[word]['fear']
                feats[26] += nrc_hashtag_emotion[word]['joy']
                feats[27] += nrc_hashtag_emotion[word]['sadness']
                feats[28] += nrc_hashtag_emotion[word]['surprise']

        feature_vectors.append(feats)
    return np.array(feature_vectors)


def create_tokenizer(lines):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(lines)
    return tokenizer


def max_length(lines):
    return max([len(s) for s in lines])


def encode_text(tokenizer, lines, length):
    encoded = tokenizer.texts_to_sequences(lines)
    padded = pad_sequences(encoded, maxlen=length, padding='post')
    return padded

def char_is_emoji(character):
    return character in emoji.UNICODE_EMOJI

def text_has_emoji(text):
    for character in text:
        if character in emoji.UNICODE_EMOJI:
            return True
    return False
