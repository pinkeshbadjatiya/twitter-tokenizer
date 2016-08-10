#!/usr/bin/python3

import re
from parse_tweet import Tweet


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



if __name__ == "__main__":
    # t = Tokeniser("tweets.en.txt")
    t = Tokeniser("test.txt")
    t.load_tweets()
    write_to_file("output_file.txt", t.tweets)
    # import pdb; pdb.set_trace()
