import pickle

from flask import current_app
from process import *

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
                nrc_emotion[splitted[0]] = {'anger': float(splitted[1]),
                                                    'disgust': float(splitted[3]),
                                                    'fear': float(splitted[4]),
                                                    'joy': float(splitted[5]),
                                                    'sadness': float(splitted[8]),
                                                    'surprise': float(splitted[9])}

    # NRC Affect Intensity (2018)
    with open(current_app.config['DATA_ROOT'] + 'lexicons/nrc_affect_intensity.txt', 'r') as f:
        f.readline()
        for line in f:
            splitted = line.strip().split('\t')
            if splitted[0] not in nrc_affect_intensity:
                nrc_affect_intensity[splitted[0]] = {'anger': float(splitted[1]),
                                                    'disgust': float(splitted[3]),
                                                    'fear': float(splitted[4]),
                                                    'joy': float(splitted[5]),
                                                    'sadness': float(splitted[8]),
                                                    'surprise': float(splitted[9])}

    # NRC Hashtag Emotion Lexicon (2015)
    with open(current_app.config['DATA_ROOT'] + 'lexicons/NRC-Hashtag-Emotion-Lexicon-v0.2.txt', 'r') as f:
        f.readline()
        for line in f:
            splitted = line.strip().split('\t')
            splitted[0] = splitted[0].replace('#','')
            if splitted[0] not in nrc_hashtag_emotion:
                nrc_hashtag_emotion[splitted[0]] = {'anger': float(splitted[1]),
                                                    'disgust': float(splitted[3]),
                                                    'fear': float(splitted[4]),
                                                    'joy': float(splitted[5]),
                                                    'sadness': float(splitted[8]),
                                                    'surprise': float(splitted[9])}


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

# ********* Python Wrapper for Stanford CoreNLP ********* #
# ********* Class definition implemented from "https://github.com/Lynten/stanford-corenlp" with slight modifications ********* #

class StanfordCoreNLP:
    def __init__(self, path_or_host, port=None, memory='4g', lang='en', timeout=5000, quiet=True,
                 logging_level=logging.WARNING, max_retries=100):
        self.path_or_host = path_or_host
        self.port = port
        self.memory = memory
        self.lang = lang
        self.timeout = timeout
        self.quiet = quiet
        self.logging_level = logging_level

        logging.basicConfig(level=self.logging_level)

        # Check args
        #self._check_args()

        if path_or_host.startswith('http'):
            self.url = path_or_host + ':' + str(port)
            logging.info('Using an existing server {}'.format(self.url))
        else:

            # Check Java
            if not subprocess.call(['java', '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) == 0:
                raise RuntimeError('Java not found.')

            # Check if the dir exists
            if not os.path.isdir(self.path_or_host):
                raise IOError(str(self.path_or_host) + ' is not a directory.')
            directory = os.path.normpath(self.path_or_host) + os.sep
            self.class_path_dir = directory

            # Check if the language specific model file exists
            switcher = {
                'en': 'stanford-corenlp-[0-9].[0-9].[0-9]-models.jar',
                'zh': 'stanford-chinese-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar',
                'ar': 'stanford-arabic-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar',
                'fr': 'stanford-french-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar',
                'de': 'stanford-german-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar',
                'es': 'stanford-spanish-corenlp-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-models.jar'
            }
            jars = {
                'en': 'stanford-corenlp-x.x.x-models.jar',
                'zh': 'stanford-chinese-corenlp-yyyy-MM-dd-models.jar',
                'ar': 'stanford-arabic-corenlp-yyyy-MM-dd-models.jar',
                'fr': 'stanford-french-corenlp-yyyy-MM-dd-models.jar',
                'de': 'stanford-german-corenlp-yyyy-MM-dd-models.jar',
                'es': 'stanford-spanish-corenlp-yyyy-MM-dd-models.jar'
            }
            if len(glob.glob(directory + switcher.get(self.lang))) <= 0:
                raise IOError(jars.get(
                    self.lang) + ' not exists. You should download and place it in the ' + directory + ' first.')

            self.port = 9999

            # Start native server
            logging.info('Initializing native server...')
            cmd = "java"
            java_args = "-Xmx{}".format(self.memory)
            java_class = "edu.stanford.nlp.pipeline.StanfordCoreNLPServer"
            class_path = '"{}*"'.format(directory)

            args = [cmd, java_args, '-cp', class_path, java_class, '-port', str(self.port)]

            args = ' '.join(args)

            logging.info(args)

            # Silence
            with open(os.devnull, 'w') as null_file:
                out_file = None
                if self.quiet:
                    out_file = null_file

                self.p = subprocess.Popen(args, shell=True, stdout=out_file, stderr=subprocess.STDOUT)
                logging.info('Server shell PID: {}'.format(self.p.pid))

            self.url = 'http://localhost:' + str(self.port)

        # Wait until server starts
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_name = urlparse(self.url).hostname
        time.sleep(1)  # OSX, not tested
        trial = 1
        while sock.connect_ex((host_name, self.port)):
            if trial > max_retries:
                raise ValueError('Corenlp server is not available')
            logging.info('Waiting until the server is available.')
            trial += 1
            time.sleep(1)
        logging.info('The server is available.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        logging.info('Cleanup...')
        if hasattr(self, 'p'):
            try:
                parent = psutil.Process(self.p.pid)
            except psutil.NoSuchProcess:
                logging.info('No process: {}'.format(self.p.pid))
                return

            if self.class_path_dir not in ' '.join(parent.cmdline()):
                logging.info('Process not in: {}'.format(parent.cmdline()))
                return

            children = parent.children(recursive=True)
            for process in children:
                logging.info('Killing pid: {}, cmdline: {}'.format(process.pid, process.cmdline()))
                # process.send_signal(signal.SIGTERM)
                process.kill()

            logging.info('Killing shell pid: {}, cmdline: {}'.format(parent.pid, parent.cmdline()))
            # parent.send_signal(signal.SIGTERM)
            parent.kill()

    def annotate(self, text, properties=None):
        if sys.version_info.major >= 3:
            text = text.encode('utf-8')

        r = requests.post(self.url, params={'properties': str(properties)}, data=text,
                          headers={'Connection': 'close'})
        return r.text

    def tregex(self, sentence, pattern):
        tregex_url = self.url + '/tregex'
        r_dict = self._request(tregex_url, "tokenize,ssplit,depparse,parse", sentence, pattern=pattern)
        return r_dict

    def tokensregex(self, sentence, pattern):
        tokensregex_url = self.url + '/tokensregex'
        r_dict = self._request(tokensregex_url, "tokenize,ssplit,depparse", sentence, pattern=pattern)
        return r_dict

    def semgrex(self, sentence, pattern):
        semgrex_url = self.url + '/semgrex'
        r_dict = self._request(semgrex_url, "tokenize,ssplit,depparse", sentence, pattern=pattern)
        return r_dict

    def word_tokenize(self, sentence, span=False):
        r_dict = self._request('ssplit,tokenize', sentence)
        tokens = [token['originalText'] for s in r_dict['sentences'] for token in s['tokens']]

        # Whether return token span
        if span:
            spans = [(token['characterOffsetBegin'], token['characterOffsetEnd']) for s in r_dict['sentences'] for token
                     in s['tokens']]
            return tokens, spans
        else:
            return tokens

    def pos_tag(self, sentence):
        r_dict = self._request(self.url, 'pos', sentence)
        words = []
        tags = []
        for s in r_dict['sentences']:
            for token in s['tokens']:
                words.append(token['originalText'])
                tags.append(token['pos'])
        return list(zip(words, tags))

    def ner(self, sentence):
        r_dict = self._request(self.url, 'ner', sentence)
        words = []
        ner_tags = []
        for s in r_dict['sentences']:
            for token in s['tokens']:
                words.append(token['originalText'])
                ner_tags.append(token['ner'])
        return list(zip(words, ner_tags))

    def parse(self, sentence):
        r_dict = self._request(self.url, 'pos,parse', sentence)
        return [s['parse'] for s in r_dict['sentences']][0]

    def dependency_parse(self, text):
        r_dict = self._request(self.url, 'depparse', text)
        ls = []
        for s in r_dict['sentences']:
            tmp = []
            for dep in s['basicDependencies']:
                tmp.append((dep['dep'], dep['governorGloss'], dep['dependentGloss']))
            ls.append(tmp)
        return ls

    def coref(self, text):
        r_dict = self._request('coref', text)

        corefs = []
        for k, mentions in r_dict['corefs'].items():
            simplified_mentions = []
            for m in mentions:
                simplified_mentions.append((m['sentNum'], m['startIndex'], m['endIndex'], m['text']))
            corefs.append(simplified_mentions)
        return corefs

    def switch_language(self, language="en"):
        self._check_language(language)
        self.lang = language

    def _request(self, url, annotators=None, data=None, *args, **kwargs):
        if sys.version_info.major >= 3:
            data = data.encode('utf-8')

        properties = {'annotators': annotators, 'outputFormat': 'json'}
        params = {'properties': str(properties), 'pipelineLanguage': self.lang}
        if 'pattern' in kwargs:
            params = {"pattern": kwargs['pattern'], 'properties': str(properties), 'pipelineLanguage': self.lang}

        logging.info(params)
        r = requests.post(url, params=params, data=data, headers={'Connection': 'close'})
        r_dict = json.loads(r.text)

        return r_dict

    def _check_args(self):
        self._check_language(self.lang)
        if not re.match('\dg', self.memory):
            raise ValueError('memory=' + self.memory + ' not supported. Use 4g, 6g, 8g and etc. ')

    def _check_language(self, lang):
        if lang not in ['en', 'zh', 'ar', 'fr', 'de', 'es']:
            raise ValueError('lang=' + self.lang + ' not supported. Use English(en), Chinese(zh), Arabic(ar), '
                                                   'French(fr), German(de), Spanish(es).')

nlp = StanfordCoreNLP('http://stanford_nlp:9999', port=9999)
