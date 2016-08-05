import nltk, excel_database,random, os.path, pickle,multiprocessing,time, multiprocess_parser,sys
from nltk.tokenize import word_tokenize
from nltk.classify import ClassifierI
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from statistics import mode
from joblib import Parallel, delayed
from nltk.stem import WordNetLemmatizer


class test_data():
	def __init__(self):
		self.word_features = []
		reload(sys)
		sys.setdefaultencoding('UTF8')

	def find_features(self,document):
		words = word_tokenize(document)
		#lemmatizer = WordNetLemmatizer()
		#words = [lemmatizer.lemmatize(item) for item in all_words]
		#print words
		features = {}
		for w in self.word_features:
			features[w] = (w in words)
		return features

	def create_set(self):
		all_words,documents = multiprocess_parser.doc_parsing()

		self.save_pickle(documents,'documents')
		all_words = nltk.FreqDist(all_words)
		self.word_features = list(all_words.keys())[:15000]
		self.save_pickle(self.word_features,'word_features')
		featuresets = multiprocess_parser.feature_set(documents,self.word_features)
		self.save_pickle(featuresets,'featuresets')

		random.shuffle(featuresets)
		#print(len(featuresets))
		testing_set = featuresets[int(0.9*len(featuresets)):]
		training_set = featuresets[:int(0.9*len(featuresets))]
		return training_set,testing_set

	def save_pickle(self,algo,algo_name):
		save_classifier = open("pickled_algos/"+algo_name+".pickle","wb")
		pickle.dump(algo, save_classifier)
		save_classifier.close()

	def load_pickle(self,algo_name):
		open_file = open("pickled_algos/"+algo_name+".pickle", "rb")
		classifier = pickle.load(open_file)
		open_file.close()
		return classifier

	def sentiment_algos(self):

		training_set, testing_set = self.create_set()
		classifiers_list = []

		naiveBayes_classifier = nltk.NaiveBayesClassifier.train(training_set)
		print("Original Naive Bayes Algo accuracy percent:", (nltk.classify.accuracy(naiveBayes_classifier, testing_set))*100)
		naiveBayes_classifier.show_most_informative_features(15)
		self.save_pickle(naiveBayes_classifier,'naiveBayes_classifier')
		classifiers_list.append(naiveBayes_classifier)

		MNB_classifier = SklearnClassifier(MultinomialNB())
		MNB_classifier.train(training_set)
		print("MNB_classifier accuracy percent:", (nltk.classify.accuracy(MNB_classifier, testing_set))*100)
		self.save_pickle(MNB_classifier,'MNB_classifier')
		classifiers_list.append(MNB_classifier)

		BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
		BernoulliNB_classifier.train(training_set)
		print("BernoulliNB_classifier accuracy percent:", (nltk.classify.accuracy(BernoulliNB_classifier, testing_set))*100)
		self.save_pickle(BernoulliNB_classifier,'BernoulliNB_classifier')
		classifiers_list.append(BernoulliNB_classifier)

		LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
		LogisticRegression_classifier.train(training_set)
		print("LogisticRegression_classifier accuracy percent:", (nltk.classify.accuracy(LogisticRegression_classifier, testing_set))*100)
		self.save_pickle(LogisticRegression_classifier,'LogisticRegression_classifier')
		classifiers_list.append(LogisticRegression_classifier)

		# LinearSVC_classifier = SklearnClassifier(LinearSVC())
		# LinearSVC_classifier.train(training_set)
		# print("LinearSVC_classifier accuracy percent:", (nltk.classify.accuracy(LinearSVC_classifier, testing_set))*100)
		# self.save_pickle(LinearSVC_classifier,'LinearSVC_classifier')
		# classifiers_list.append(LinearSVC_classifier)

		# NuSVC_classifier = SklearnClassifier(NuSVC())
		# NuSVC_classifier.train(training_set)
		# print("NuSVC_classifier accuracy percent:", (nltk.classify.accuracy(NuSVC_classifier, testing_set))*100)

		SGDC_classifier = SklearnClassifier(SGDClassifier())
		SGDC_classifier.train(training_set)
		print("SGDC_classifier accuracy percent:", (nltk.classify.accuracy(SGDC_classifier, testing_set))*100)
		self.save_pickle(SGDC_classifier,'SGDC_classifier')
		classifiers_list.append(SGDC_classifier)

		return classifiers_list


	def saved_algos(self):
		self.word_features = self.load_pickle("word_features")
		classifiers_list = []
		all_algos = ['naiveBayes_classifier','MNB_classifier','BernoulliNB_classifier','LogisticRegression_classifier','SGDC_classifier']
		for i in range(len(all_algos)):
			classifiers_list.append(self.load_pickle(all_algos[i]))

		# open_file = open("pickled_algos/SGDC_classifier5k.pickle", "rb")
		# SGDC_classifier = pickle.load(open_file)
		# open_file.close()

		return classifiers_list


	def sentiment_calc(self,new_algo,out_data):
		# ed = excel_database.excel_data(ticker)
		# ed.open_sheet()
		# out_data =  ed.reading_sheet()
		# out_data = ['skewed juvenile person walking on road','elaborate this for me','he is exceptionally responsive']
		if not (os.path.isfile("/home/vivek/Desktop/Stefano/Code/Algo1/pickled_algos/SGDC_classifier.pickle") and new_algo):
			classifiers_list = self.sentiment_algos()
		else :
			classifiers_list = self.saved_algos()

		voted_classifier = VoteClassifier(classifiers_list[0],classifiers_list[1],classifiers_list[2],classifiers_list[3],classifiers_list[4])
		sentiment_votes,pos_count, neg_count = [],0,0
		for i in range(len(out_data)):
	   		headlineData_features = self.find_features(out_data[i])
	   		try : 
	   			#print '\n',voted_classifier.classify(headlineData_features),voted_classifier.confidence(headlineData_features),' :: ',out_data[i]
	   			sentiment_votes.append(voted_classifier.classify(headlineData_features))
	   			if voted_classifier.classify(headlineData_features) == 'pos':
	   				pos_count += float(voted_classifier.confidence(headlineData_features))
	   			if voted_classifier.classify(headlineData_features) == 'neg':
	   				neg_count += float(voted_classifier.confidence(headlineData_features))
	   		except Exception as e:
	   			print e,' :: ',out_data[i]
	   	sentiment_value = (pos_count - neg_count)/(len(out_data))
	   	print mode(sentiment_votes),' :: ', sentiment_value
	   	return sentiment_value


class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        return mode(votes)

    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)

        choice_votes = votes.count(mode(votes))
        conf = float(choice_votes) / len(votes)
        return conf

# Lemmitizing, Named Entry Recognition, removing stop words