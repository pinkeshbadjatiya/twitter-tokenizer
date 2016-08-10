#!/usr/bin/python3
import re
from collections import defaultdict
from emoticons import Emoticons


SUBSTITUTION_STARTING_CHAR = ">!"
SUBSTITUTION_ENDING_CHAR = "!<"



class Tweet(object):
    #  "ALNUM": r"(@[a-zA-Z0-9_]+)",
    #  "UNICODE_GLYPHS": [^\u0000-\u007F]+
    #   "URL": r"([https://|http://]?[a-zA-Z\d\/]+[\.]+[a-zA-Z\d\/\.]+)",

    regexp = {"RT": "^RT",
              "MT": r"^MT",
              "HASHTAG": r"(#[\w\d]+)",
              "MENTIONS": r"(@[\w\d]+)",
              "EMAILS": r"([\w\d]+[.|\w\d])+@([\w\d]+[.])+\w+",
              "UNICODE_GLYPHS": r"[\U0001F600-\U0001F64F]+",
              "URL": r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
              "SPACES": r"\s+",
              "TWITTER_HANDLE": r"(@[a-zA-Z0-9_]+)"}

    __count = defaultdict(int)         # All count must be zero initially
    ReplacementDict = {}
    unicode_glyphs_compiled = re.compile(regexp["UNICODE_GLYPHS"], re.UNICODE)
    regexp = dict((key, re.compile(value)) for key, value in regexp.items())
    regexp["UNICODE_GLYPHS"] = unicode_glyphs_compiled  # Get the unicode compiled regex

    def __init__(self, tweet):
        """ properties:

            RT, MT - boolean
            URLs - list of URL
            Hashtags - list of tags
        """
        self.origTweet, self.tweet = tweet, tweet

        # All these methods update the self.tweet to appropriate replacement
        self.tweet, self.UserHandles = Tweet.getUserHandles(self.tweet, self.regexp["TWITTER_HANDLE"])
        self.RT = Tweet.getAttributeRT(tweet)
        self.MT = Tweet.getAttributeMT(tweet)
        self.Owner = "UNKNOWN"
        self.Emoticon = Tweet.getAttributeEmoticon(tweet)

        self.tweet, self.Mentions = Tweet.getMentions(self.tweet, self.regexp["MENTIONS"])
        self.tweet, self.Hashtags = Tweet.getHashtags(self.tweet, self.regexp["HASHTAG"])
        self.tweet, self.URLs = Tweet.getURLs(self.tweet, self.regexp["URL"])
        self.tweet, self.UnicodeGlyphs = Tweet.getAttributeGlyphs(self.tweet, self.regexp["UNICODE_GLYPHS"])
        # self.tweet = Tweet.getAttributeGlyphs(tweet, Tweet.regexp["UNICODE_GLYPHS"])

        # additional intelligence
        # if ( self.RT and len(self.UserHandles) > 0 ):  # change the owner of tweet?
        #     self.Owner = self.UserHandles[0]
        # return

    def __str__(self):
        """ for display method """
        return "owner %s, urls: %d, hashtags %d, user_handles %d, len_tweet %d, RT = %s, MT = %s" % \
               (self.Owner, len(self.URLs), len(self.Hashtags), len(self.UserHandles), len(self.tweet), self.RT, self.MT)

    @staticmethod
    def getAttributeRT(tweet):
        """ see if tweet is a RT """
        return re.search(Tweet.regexp["RT"], tweet.strip()) is not None

    @staticmethod
    def getAttributeMT(tweet):
        """ see if tweet is a MT """
        return re.search(Tweet.regexp["MT"], tweet.strip()) is not None

    @staticmethod
    def getAttributeEmoticon(tweet):
        """ see if tweet is contains any emoticons, +ve, -ve or neutral """
        emoji = list()
        for tok in re.split(Tweet.regexp["SPACES"], tweet.strip()):
            if tok in Emoticons.POSITIVE:
                emoji.append(tok)
                continue
            if tok in Emoticons.NEGATIVE:
                emoji.append(tok)
        return emoji

    @classmethod
    def getAttributeGlyphs(cls, tweet, UNICODE_GLYPHS_REGEX):
        """ see if tweet is contains any glyphs then get it! """

        replace_pattern = "GLY"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            cls.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(cls.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            cls.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(UNICODE_GLYPHS_REGEX, replace_attr, tweet), replacements

    @classmethod
    def getUserHandles(cls, tweet, TWITTER_HANDLE_regex):
        """ given a tweet we try and extract all user handles in order of occurrence"""

        replace_pattern = "HAND"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            cls.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(cls.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            cls.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(TWITTER_HANDLE_regex, replace_attr, tweet), replacements
        # return re.findall(Tweet.regexp["TWITTER_HANDLE"], tweet)

    @classmethod
    def getHashtags(cls, tweet, HASHTAG_regex):
        """ return all hashtags"""

        replace_pattern = "HTAG"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            cls.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(cls.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            cls.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(HASHTAG_regex, replace_attr, tweet), replacements
        # return re.findall(Tweet.regexp["HASHTAG"], tweet)

    @classmethod
    def getMentions(cls, tweet, MENTIONS_regex):
        """ return all mentions"""

        replace_pattern = "MEN"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            cls.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(cls.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            cls.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(MENTIONS_regex, replace_attr, tweet), replacements
        # return re.findall(Tweet.regexp["MENTIONS"], tweet)

    @classmethod
    def getURLs(cls, tweet, URL_regex):
        """ URL : [http://]?[\w\.?/]+"""

        replace_pattern = "URL"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            cls.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(cls.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            cls.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(URL_regex, replace_attr, tweet), replacements
        # return re.findall(Tweet.regexp["URL"], tweet)
