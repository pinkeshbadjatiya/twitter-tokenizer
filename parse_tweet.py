#!/usr/bin/python3
import re
from collections import defaultdict
from emoticons import Emoticons
from six import text_type
from copy import deepcopy


SUBSTITUTION_STARTING_CHAR = ">!"
SUBSTITUTION_ENDING_CHAR = "!<"


class Tweet(object):

    regexp = {"RT": "^RT",
              "MT": r"^MT",
              "HASHTAG": r"(#[\w\d]+)",
              "EMAILS": r"([\w\d]+[.|\w\d])+@([\w\d]+[.])+\w+",
              "UNICODE_GLYPHS": r"[\U0001F600-\U0001F64F]+",
              "UNICODE_CHARS": r"[\U000000A0-\U000FFFFF]+",
              "URL": r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
              "SPACES": r"\s+",
              "TWITTER_HANDLE": r"[^a-zA-Z0-9_](@[a-zA-Z0-9_]+)"}

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
        self.__count = defaultdict(int)         # All count must be zero initially
        self.ReplacementDict = {}

        # All these methods update the self.tweet to appropriate replacement
        self.RT = self.getAttributeRT(tweet)
        self.MT = self.getAttributeMT(tweet)
        self.Owner = "UNKNOWN"
        self.Emoticon = self.getAttributeEmoticon(tweet)

        self.tweet, self.UserHandles = self.getUserHandles(self.tweet, self.regexp["TWITTER_HANDLE"])
        self.tweet, self.Emails = self.getEmails(self.tweet, self.regexp["EMAILS"])
        self.tweet, self.Hashtags = self.getHashtags(self.tweet, self.regexp["HASHTAG"])
        self.tweet, self.URLs = self.getURLs(self.tweet, self.regexp["URL"])
        self.tweet, self.UnicodeGlyphs = self.getAttributeGlyphs(self.tweet, self.regexp["UNICODE_GLYPHS"])
        self.tweet, self.UnicodeChars = self.getAttributeUnicodeChars(self.tweet, self.regexp["UNICODE_CHARS"])

        # Tokenize the tweet!
        # This should happen after all the above extraction is done
        self.tokens = self.getTokens(self.tweet)

        # additional intelligence
        # if ( self.RT and len(self.UserHandles) > 0 ):  # change the owner of tweet?
        #     self.Owner = self.UserHandles[0]
        # return

    def __str__(self):
        """ for display method """
        return "owner %s, urls: %d, hashtags %d, user_handles %d, len_tweet %d, RT = %s, MT = %s" % \
               (self.Owner, len(self.URLs), len(self.Hashtags), len(self.UserHandles), len(self.tweet), self.RT, self.MT)

    def getTokens(self, tweet, getString=False):
        """ Convert the tweet into multiple tokens based on heuristics """

        # Copy for safety
        tweet = deepcopy(tweet)

        # 1. Separate the replaced special words with spaces to avoid problems
        ##################################################
        regex = [re.compile(r"(>!GLY\d!<)"),
                 re.compile(r"(>!HAND\d!<)"),
                 re.compile(r"(>!EMAIL\d!<)"),
                 re.compile(r"(>!HTAG\d!<)"),
                 re.compile(r"(>!URL\d!<)")
                 ]
        for reg in regex:
            tweet = reg.sub(r" \1 ", tweet)

        # Keep the rest of the unicode as it is.
        regex = [re.compile(r"(>!UNIC\d!<)")
                 ]
        for reg in regex:
            tweet = re.sub(reg, lambda m: self.ReplacementDict[m.group(0)], tweet)


        # 2. Cleanup the extra bits
        ##################################################
        # Pad numbers with commas to keep them from further tokenization.
        COMMA_IN_NUM = re.compile(r'(?<!,)([,،])(?![,\d])'), r' \1 '

        # Replace non-breaking spaces with normal spaces.
        NON_BREAKING = re.compile(u"\u00A0"), " "

        # Don't tokenize period unless it ends the line and that it isn't
        # preceded by another period, e.g.
        # "something ..." -> "something ..."
        # "something." -> "something ."
        FINAL_PERIOD_1 = re.compile(r"(?<!\.)\.$"), r" ."
        # Don't tokenize period unless it ends the line eg.
        # " ... stuff." ->  "... stuff ."
        FINAL_PERIOD_2 = re.compile(r"""(?<!\.)\.\s*(["'’»›”]) *$"""), r" . \1"

        # Treat continuous commas as fake German,Czech, etc.: „
        MULTI_COMMAS = re.compile(r'(,{2,})'), r' \1 '
        # Treat continuous dashes as fake en-dash, etc.
        MULTI_DASHES = re.compile(r'(-{2,})'), r' \1 '
        # Treat multiple periods as a thing (eg. ellipsis)
        MULTI_DOTS = re.compile(r'(\.{2,})'), r' \1 '

        # Left/Right strip, i.e. remove heading/trailing spaces.
        # These strip regexes should NOT be used,
        # instead use str.lstrip(), str.rstrip() or str.strip()
        # (They are kept for reference purposes to the original toktok.pl code)
        LSTRIP = re.compile(r'^ +'), ''
        RSTRIP = re.compile(r'\s+$'), '\n'
        # Merge multiple spaces.
        ONE_SPACE = re.compile(r' {2,}'), ' '

        self.TOKTOK_REGEXES = [COMMA_IN_NUM, NON_BREAKING, FINAL_PERIOD_1, FINAL_PERIOD_2,
                               MULTI_DOTS, MULTI_DASHES, MULTI_COMMAS, LSTRIP, RSTRIP,
                               ONE_SPACE]

        tweet = text_type(tweet)  # Converts input string into unicode.
        for regexp, subsitution in self.TOKTOK_REGEXES:
            tweet = regexp.sub(subsitution, tweet)

        # Finally, strips heading and trailing spaces
        # and converts output string into unicode.
        tweet = text_type(tweet.strip())
        return tweet if getString else tweet.split()

    def getAttributeRT(self, tweet):
        """ see if tweet is a RT """
        return re.search(Tweet.regexp["RT"], tweet.strip()) is not None

    def getAttributeMT(self, tweet):
        """ see if tweet is a MT """
        return re.search(Tweet.regexp["MT"], tweet.strip()) is not None

    def getAttributeEmoticon(self, tweet):
        """ see if tweet is contains any emoticons, +ve, -ve or neutral """
        emoji = list()
        for tok in re.split(Tweet.regexp["SPACES"], tweet.strip()):
            if tok in Emoticons.POSITIVE:
                emoji.append(tok)
                continue
            if tok in Emoticons.NEGATIVE:
                emoji.append(tok)
        return emoji

    def getAttributeGlyphs(self, tweet, UNICODE_GLYPHS_REGEX):
        """ see if tweet is contains any glyphs then get it! """

        replace_pattern = "GLY"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            self.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(self.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            self.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(UNICODE_GLYPHS_REGEX, replace_attr, tweet), replacements

    def getAttributeUnicodeChars(self, tweet, UNICODE_CHARS_REGEX):
        """ see if tweet is contains any glyphs then get it! """

        replace_pattern = "UNIC"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            self.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(self.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            self.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(UNICODE_CHARS_REGEX, replace_attr, tweet), replacements

    def getUserHandles(self, tweet, TWITTER_HANDLE_regex):
        """ given a tweet we try and extract all user handles in order of occurrence"""

        replace_pattern = "HAND"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            self.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(self.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            self.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(TWITTER_HANDLE_regex, replace_attr, tweet), replacements

    def getEmails(self, tweet, EMAIL_regex):
        """ given a tweet we try and extract all user handles in order of occurrence"""

        replace_pattern = "EMAIL"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            self.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(self.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            self.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(EMAIL_regex, replace_attr, tweet), replacements

    def getHashtags(self, tweet, HASHTAG_regex):
        """ return all hashtags"""

        replace_pattern = "HTAG"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            self.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(self.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            self.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(HASHTAG_regex, replace_attr, tweet), replacements

    def getURLs(self, tweet, URL_regex):
        """ URL : [http://]?[\w\.?/]+"""

        replace_pattern = "URL"
        replacements = []
        def replace_attr(matchobj):
            nonlocal replace_pattern, replacements
            self.__count[replace_pattern] += 1
            substitution = SUBSTITUTION_STARTING_CHAR + replace_pattern + str(self.__count[replace_pattern]) + SUBSTITUTION_ENDING_CHAR
            self.ReplacementDict[substitution] = matchobj.group(0)
            replacements.append(matchobj.group(0))
            return substitution

        return re.sub(URL_regex, replace_attr, tweet), replacements
