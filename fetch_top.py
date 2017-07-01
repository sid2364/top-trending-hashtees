import json
import sys
import key_phrases
try:
	import config
except:
	print("Please put your CONSUMER_KEY and CONSUMER_SECRET in config.py, and try again.")
	sys.exit()
from application_only_auth import Client

TWTTR_API = 'https://api.twitter.com/'
TWTTR_API_VERSION = '1.1'
TWTTR_QUERY = '/search/tweets.json?q='
TWTTR_RECENT = 'result_type=recent'
HASHTAG = '%23'

def search(keywords, json_o):
	final = []
	def deep_search(keywords, json_o):
		found = {}
		if type(keywords) != type([]):
			keywords = [keywords]

		if type(json_o) == type(dict()):
			for keyword in keywords:
				if keyword in json_o.keys():
					found[keyword] = json_o[keyword]
				elif len(json_o.keys()) > 0:
					for key in json_o.keys():
						result = deep_search(keyword, json_o[key])
						if result:
							for k, v in result.items():
								found[k] = v
		elif type(json_o) == type([]):
			for node in json_o:
				result = deep_search(keywords, node)
				if result:
					for k, v in result.items():
						found[k] = v
		if found != {}:
			final.append(found)
		return found
	deep_search(keywords, json_o)
	return final

def get_top_n(word_list, n=5):
	word_counter = {}
	for word in word_list:
		if word in word_counter:
			word_counter[word] += 1
		else:
			word_counter[word] = 1
	popular_words = sorted(word_counter, key = word_counter.get, reverse = True)
	top_n = popular_words[:n]
	
	return hashtagify(top_n)

def hashtagify(word_list):
	return ['#' + word for word in word_list]

def get_hashtees(search_phrase, since='2012-01-01'):
	search_phrase = search_phrase.replace(' ', '%20')
	search_phrase = search_phrase.replace('#', HASHTAG)

	client = Client(config.CONSUMER_KEY, config.CONSUMER_SECRET)

	if since is not None:
		since_ = "%20since:"+since
	else:
		since_ = ''

	tweet = client.request(TWTTR_API + TWTTR_API_VERSION + TWTTR_QUERY + search_phrase + '&' + TWTTR_RECENT)

	hashtags_ele = search(["hashtags"], tweet)
	actual_tags = search(["text"], hashtags_ele)

	catch_words = [] 
	for tags in actual_tags:
		for k in tags:
			catch_words.append(tags[k])

	return catch_words

def accumulate_hashtees(text):
	phrases = key_phrases.get_best(text)
	catch_words_acc = []

	# Don't use append; we don't want list of lists, only one list
	catch_words_acc += get_hashtees(key_phrases.get_without_stopwords(text))

	for phrase in phrases:
		catch_words_acc += get_hashtees(phrase)

	return catch_words_acc


if __name__ == "__main__":
	try:
		words = accumulate_hashtees(raw_input("Enter your title or hashtag here: "))
		if not words:
			print("Sorry, I couldn't find any hashtags related to your query. Try again?")
			sys.exit()
		print("Here are some top trending #hashtags:-")
		for tag in get_top_n(words, 5):
			print tag
	except Exception as e:
		print("\nOops! There was an error: " + str(e))
	except KeyboardInterrupt as e:
		print('\nBye!')
