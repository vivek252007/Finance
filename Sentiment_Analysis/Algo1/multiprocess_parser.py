from joblib import Parallel, delayed
import multiprocessing,time,nltk,sys
from nltk.tokenize import word_tokenize

num_cores = multiprocessing.cpu_count()
reload(sys)
sys.setdefaultencoding('UTF8')

def processInput(p,senti):
	all_words, documents = [],[]
	#  j is adject, r is adverb, and v is verb
	#allowed_word_types = ["J","R","V"]
	allowed_word_types = ["J"]
	documents.append((p, senti))
	words_p = word_tokenize(p)
	pos = nltk.pos_tag(words_p)
	for wp in pos:
		if wp[1][0] in allowed_word_types:
			all_words.append(wp[0].lower())
	return all_words,documents	

def doc_parsing():
	num_cores = multiprocessing.cpu_count()
	all_wrds, docs= [],[]
	for i in ['pos','neg']:
		short_doc = open("training_set/"+i+".txt","r").read()
		parallel_data= Parallel(n_jobs=num_cores)(delayed(processInput)(p,i) for p in short_doc.split('\n'))
		for j in range(2):
			ret_list = [parallel_data[k][j] for k in range(len(parallel_data))]
			ret = [item for sublist in ret_list for item in sublist]
			if j == 0:
				all_wrds.append(ret) 
			else :
				ret.pop()
				docs.append(ret)

	all_words = [item for sublist in all_wrds for item in sublist]
	documents = [item for sublist in docs for item in sublist]

	#print list(set(ret))
	return all_words, documents

def find_features(document,word_features,category):
    words = word_tokenize(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return (features,category)

def feature_set(documents,word_features):
	#featuresets = [(find_features(rev,word_features,category)) for (rev, category) in documents]

	featuresets = Parallel(n_jobs = num_cores)(delayed(find_features)(rev,word_features,category) for (rev, category) in documents)
	return featuresets