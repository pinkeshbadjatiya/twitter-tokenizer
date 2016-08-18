#!/usr/bin/python3
import re
from parse_tweet import Tweet, SUBSTITUTION_STARTING_CHAR, SUBSTITUTION_ENDING_CHAR
from flask import Flask, render_template, redirect, url_for, request
from collections import defaultdict
import operator
from copy import deepcopy
import random

app = Flask(__name__)

DATASETS = "./datasets"

class Tokenizer:
    def __init__(self, file_name):
        self.file_name = DATASETS + "/" + file_name
        self.regex_tweet_check = re.compile(r"^RT @[\w\d]+:")
        self.tweets = []
        self.sentences = []
        self.graph = {
            "edges": defaultdict(list),
            "weights": defaultdict(int)
        }
        self.tokenBank = defaultdict(int)

    def load_tweets(self, max_tweet_count):
        with open(self.file_name, 'rb') as f:
            raw_tweets = f.readlines()

        self.tweets, tw = [], ""
        for line in raw_tweets:
            line = line.decode("utf-8")   # Very important especially for UNICODE chars
            if re.match(self.regex_tweet_check, line):
                if tw != "":
                    if max_tweet_count and max_tweet_count != -1 and len(self.tweets) >= max_tweet_count - 1:
                        break
                    self.tweets.append(Tweet("<s> " + tw.strip() + " </s>"))
                tw = ""
            tw += line
        self.tweets.append(Tweet("<s> " + tw.strip() + "</s>"))

        for tweet in self.tweets:
            for token in tweet.tokens:
                self.tokenBank[token] += 1

    # def load_corpus(self, max_sentence_count):
    #     raw_sentences = []
    #
    #     # TEMP_CHAR is ":$$"
    #     def cleanup(line):        # Cleanup !!
    #         # E. -> E$ to prevent new false sentence
    #         ALTER_FULLSTOPS = re.compile(r'([0-9A-Z])\.')
    #         line = re.sub(ALTER_FULLSTOPS, r'\1:$$', line)
    #
    #         # Mr./Mrs. -> Mr$/Mrs$ to prevent new false sentence
    #         ALTER_FULLSTOPS = re.compile(r'([Mr,Mrs,Dr])\.')
    #         line = re.sub(ALTER_FULLSTOPS, r'\1:$$', line)
    #         return line
    #
    #     def de_cleanup(line):
    #         # Revert the steps done for cleanup
    #         RESET_FULLSTOPS = re.compile(r':\$\$')
    #         line = re.sub(RESET_FULLSTOPS, r'.', line)
    #         return line
    #
    #     with open(self.file_name, 'rb') as f:
    #         for line in f.readlines():
    #             # Very important especially for UNICODE chars
    #             raw_sentences.append(cleanup(line.decode("utf-8")))
    #
    #     self.sentences = [Tweet("<s> " + de_cleanup(sen.strip()) + " . </s>") for sen in raw_sentences[0].split(".")]
    #     if max_sentence_count and max_sentence_count != -1:
    #         self.sentences = self.sentences[:max_sentence_count]

    def update_graph(self, n_gram, tokens):
        """ Does not work for n-gram == 1.
            Just skip as need to just randomly give words/tokens.
        """
        if n_gram == 1:
            return

        siz = len(tokens)
        dependency = n_gram - 1
        for i in range(siz):
            if i >= siz - 1:
                continue
            key = " ".join(tokens[i - dependency + 1: i + 1])
            self.graph["edges"][key].append(tokens[i + 1])
            self.graph["weights"][key + " " + tokens[i + 1]] += 1


    def develop_graph_data(self):
        # Develop data for 2b for unigrams
        # bank = sorted(self.tokenBank.items(), key=operator.itemgetter(1))     # Sort by frequency
        # bank.reverse()
        # with open("graph_2b.csv", mode="a") as f:
        #      for i in range(len(bank)):
        #          print(str(i + 1) + " " + str(bank[i][1]), file=f)


        # Develop data for 2c for all X's in P(<s/> | X)
        with open("graph_2c.csv", mode="a") as f:
            dic = defaultdict(int)
            for tw in self.tweets:
                if len(tw.tokens) >= 2:
                    if tw.tokens[-1] == "</s>":
                        dic[tw.tokens[-2]] += 1

            sor = sorted(dic.items(), key=operator.itemgetter(1))     # Sort by frequency
            sor.reverse()
            for i in range(len(sor)):
                print(str(i + 1) + " " + str(sor[i][1]), file=f)


    def generate_sentence(self, n_gram, generate_type, failures=0):
        """ Types of sentence generation:
            - random
            - random_unique
            - most_frequent
        """

        def most_frequent(lst):   # Return the most frequent element in a list
            if len(lst) < 1:      # Return end of line token when the list is empty
                return "</s>"     # (Forcefully ending the sentence generation)"
            return max(set(lst), key=lst.count)

        MAX_SENTENCE_LENGTH_FOR_1_GRAM = 20
        try:
            sentence = ["<s>"]
            dependency = n_gram - 1
            if n_gram == 1:
                if generate_type == "random":
                    sentence += [random.sample(self.tokenBank.keys(), 1)[0] for i in range(MAX_SENTENCE_LENGTH_FOR_1_GRAM)]
                elif generate_type == "most_frequent":
                    sentence += list(self.tokenBank)[:MAX_SENTENCE_LENGTH_FOR_1_GRAM]
                else:
                    sentence = ["-- !No generate_type specified! --"]
            else:
                if generate_type == "random":
                    while sentence[-1] != "</s>":
                        key = " ".join(sentence[-dependency:])
                        sentence.append(random.choice(self.graph["edges"][key]))
                elif generate_type == "most_frequent":
                    while sentence[-1] != "</s>":
                        key = " ".join(sentence[-dependency:])
                        sentence.append(most_frequent(self.graph["edges"][key]))
                else:
                    sentence = ["-- !No generate_type specified! --"]
            return {
                "sentence": " ".join(sentence),
                "generate_type": generate_type,
                "failures": failures
            }
        except IndexError:
            return self.generate_sentence(n_gram, generate_type, failures + 1)

# def write_to_file(file_name, tweets):
#     with open(file_name, mode="w", encoding="utf8") as f:
#         for tweet in tweets:
#             print(tweet.tweet, file=f)


@app.route("/tweets//")
@app.route("/tweets/<filename>")
@app.route("/tweets/<filename>/<int:max_tweet_count>")
def display_tweets(filename=None, max_tweet_count=None):
    if not filename:
        return redirect(url_for('display_tweets', filename="tweets.en.txt", max_tweet_count=max_tweet_count))

    t = Tokenizer(filename)
    t.load_tweets(max_tweet_count)

    tweets = []
    for t in t.tweets:
        tweet = {}
        tweet["tweet"] = t.origTweet
        tweet["glyphs"] = []
        tweet["unicodes"] = []
        tweet["handles"] = []
        tweet["emails"] = []
        tweet["hashtags"] = []
        tweet["urls"] = []

        for (k, v) in t.ReplacementDict.items():
            if re.match(r">!GLY\d!<", k):
                tweet["glyphs"].append(v)
            elif re.match(r">!UNIC\d!<", k):
                tweet["unicodes"].append(v)
            elif re.match(r">!HAND\d!<", k):
                tweet["handles"].append(v)
            elif re.match(r">!EMAIL\d!<", k):
                tweet["emails"].append(v)
            elif re.match(r">!HTAG\d!<", k):
                tweet["hashtags"].append(v)
            elif re.match(r">!URL\d!<", k):
                tweet["urls"].append(v)
        tweets.append(tweet)

    return render_template('tweets.html', filename=filename, tweets=tweets)


@app.route("/tokenize/", methods=["GET"])
def tokenize():
    filename = request.args.get("filename", "tweets.en.txt")
    max_tweet_count = int(request.args.get("max_tweet_count", -1))

    t = Tokenizer(filename)
    t.load_tweets(max_tweet_count)

    tweets = []
    for t in t.tweets:
        tweet = {}
        tweet["tweet"] = t.origTweet
        tweet["tokens"] = t.tokens
        tweet["ReplacementDict"] = t.ReplacementDict
        tweets.append(tweet)

    return render_template('tokenize.html', filename=filename, tweets=tweets)


@app.route("/stats/", methods=["GET"])
def generate_statistics():
    # filename = request.args.get("filename", "real_soldiers_of_fortune.txt")
    filename = request.args.get("filename", "tweets.en.txt")
    max_sentence_count = int(request.args.get("max_sentences", -1))
    n_gram = int(request.args.get("n_gram", 1))
    generate_sentence = int(request.args.get("generate_sentence", 0))
    generate_type = request.args.get("generate_type", "")
    sort_type = request.args.get("sort_type", "frequency")

    t = Tokenizer(filename)
    t.load_tweets(max_sentence_count)

    # Now consider each line like a single Tweet and run the code for the tweet

    # Create a token_corpus
    # token_corpus[n_gram][token1 token2 ... ]
    MAX_N_GRAM = n_gram + 1
    token_corpus = {}
    for i in range(MAX_N_GRAM + 1):
        token_corpus[i + 1] = defaultdict(int)

    # Develop all n-grams
    for i in range(1, MAX_N_GRAM + 1):
        for sentence in t.tweets:
            tokens = [sentence.ReplacementDict.get(t, t) for t in sentence.tokens]
            for start_ind in range(len(tokens)):
                end_ind = start_ind + i
                if end_ind > len(tokens):
                    continue
                make_key = " ".join(tokens[start_ind: end_ind])
                token_corpus[i][make_key] += 1

            # For creating graph as linked_list
            t.update_graph(n_gram, tokens)

    if generate_sentence:
        random_sentence = t.generate_sentence(n_gram, generate_type=generate_type)
    else:
        random_sentence = None

    # Sort by frequency
    corpus_stats = sorted(token_corpus[n_gram].items(), key=operator.itemgetter(1))
    corpus_stats.reverse()

    # Now calculate probablity for token ending the sentence
    result = []
    for (k, v) in corpus_stats:
        sen = {}
        sen["token"] = k
        sen["freq"] = v
        sen["probablity_ending"] = (token_corpus[n_gram + 1][k + " " + "</s>"] * 1.0)/token_corpus[n_gram][k]
        # sen["probablity_ending"] = (token_corpus[n_gram + 1][k + " " + "</s>"] * 1.0)/token_corpus[1]["</s>"]
        result.append((sen, sen["probablity_ending"]))

    # # Sort by probablity
    if sort_type == "probablity":
        result = sorted(result, key=operator.itemgetter(1))
        result.reverse()
    elif sort_type == "frequency":
        pass
        # Default sorted by freq
    else:
        print("unknown Sort Type")

    # Used to generate graph, use once only
    # t.develop_graph_data()

    return render_template('generate_statistics.html', filename=filename,
                           result=result, n_gram=n_gram, sentence=random_sentence)

@app.route("/")
def main():
    return redirect(url_for('display_tweets'))


# @app.route("/write")
# def write():
#     write_to_file("output_file.txt", t.tweets)
#     return "Success!"

if __name__ == "__main__":
    app.run()
