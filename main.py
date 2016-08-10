#!/usr/bin/python3
import re
from parse_tweet import Tweet, SUBSTITUTION_STARTING_CHAR, SUBSTITUTION_ENDING_CHAR
from flask import Flask, render_template

app = Flask(__name__)


class Tokeniser:
    def __init__(self, file_name):
        self.file_name = file_name
        self.regex_tweet_check = re.compile(r"^RT @[\w\d]+:")
        self.tweets = []

    def load_tweets(self):
        with open(self.file_name, 'rb') as f:
            raw_tweets = f.readlines()

        self.tweets, tw = [], ""
        for line in raw_tweets:
            line = line.decode("utf-8")   # Very important especially for UNICODE chars
            if re.match(self.regex_tweet_check, line):
                if tw != "":
                    self.tweets.append(Tweet(tw))
                tw = ""
            tw += line
        self.tweets.append(Tweet(tw))


def write_to_file(file_name, tweets):
    with open(file_name, mode="w", encoding="utf8") as f:
        for tweet in tweets:
            print(tweet.tweet, file=f)


@app.route("/")
def main():
    filename = "tweets.en.txt"
    t = Tokeniser(filename)
    t.load_tweets()

    tweets = []
    for t in t.tweets:
        tweet = {}
        tweet["tweet"] = t.origTweet
        tweet["glyphs"] = []
        tweet["unicodes"] = []
        tweet["handles"] = []
        tweet["hashtags"] = []
        tweet["urls"] = []

        for (k, v) in t.ReplacementDict.items():
            if re.match(r">!GLY\d!<", k):
                tweet["glyphs"].append(v)
            elif re.match(r">!UNIC\d!<", k):
                tweet["unicodes"].append(v)
            elif re.match(r">!HAND\d!<", k):
                tweet["handles"].append(v)
            elif re.match(r">!HTAG\d!<", k):
                tweet["hashtags"].append(v)
            elif re.match(r">!URL\d!<", k):
                tweet["urls"].append(v)
        tweets.append(tweet)

    # write_to_file("output_file.txt", t.tweets)
    return render_template('tweets.html', filename=filename, tweets=tweets)


@app.route("/write")
def write():
    write_to_file("output_file.txt", t.tweets)
    return "Success!"

if __name__ == "__main__":
    app.run()
