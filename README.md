# twitter-tokenizer
A pretty tokenizer based on twitter dataset

- Strictly use `python3`
- USAGE: `python3 main.py` or `./main.py`
- Routes:
  - `/` or `/tweets/<filename>/<int:max_tweet_count>`: Shows different features extracted from tweets using regex
    - Params in URL:
      - `filename` : Name of file
      - `max_tweet_count` : First specific no of tweets that we need to consider.
  - `/tokenize` : Shows the tokens extracted from the tweet using simple & logical heuristics.
  - `/stats` : Show the stats of multiple n-grams and generates sentences based on the n-gram choosen.
    - GET paramas:
      - `filename`            = request.args.get("filename", "tweets.en.txt")
      - `max_sentence_count`  = int(request.args.get("max_sentences", -1))
      - `n_gram`              = int(request.args.get("n_gram", 1))
      - `generate_sentence`   = int(request.args.get("generate_sentence", 0))
      - `generate_type`       = request.args.get("generate_type", "")
      - `sort_type`           = request.args.get("sort_type", "frequency")


Example URL's:
http://localhost:5000/tweets/tweets.en.txt
http://localhost:5000/tokenize/
http://localhost:5000/stats/?generate_sentence=1&n_gram=1&generate_type=random
http://localhost:5000/stats/?generate_sentence=1&n_gram=2&generate_type=random&sort_type=probablity

Sentence generation types:
This happens untill we reach the MAX_RECURSION_LIMIT or we find a <s/>
- `random`
  - 1-gram : This chooses the next token completely randomely.
  - n-gram : This chooses the next token with probablity propotional to its frequency with that token.

- `most_frequent`
  - 1-gram : Chooses the top "MAX_SENTENCE_LENGTH_FOR_1_GRAM" no of unigrams based on frequency
  - n-gram : Chooses the next most frequent token(n-1 gram) along with the current token.

-
Reasons:
1. It considers a lot of cases which include, "s...", "25,000", "this...", "are-", "lets play!!!", "25/3", "25metres/sec", "pinkesh@gmail.com", URL's, emoticons, glyphs, UNICODE chars, Multilingual Support etc.
2. It provides a simple API interface to use. You can request any type of data using the GET parameters specified
