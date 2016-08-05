# -*- coding: utf-8 -*-
import sys,nltk,re
from nltk.corpus import stopwords,sentiwordnet as swn
from nltk.internals import find_jars_within_path
from nltk.tag.stanford import StanfordPOSTagger,StanfordNERTagger
from comp_data import comp_file_data, comp_goog_data
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

class stanford_nlp():
    def __init__(self,sentence):
        self.sentence = sentence.replace("’","").replace("n't"," not").replace("'","")
        self.stopwords = stopwords.words('english')

    def stop_wrds(self):
    	sent = []
    	stopwords_new = set(self.stopwords) - set(['but','against','with','up','down','over','under','all','few','nor','not','only'])
    	for word in word_tokenize(self.sentence):
    		if bool(2 <= len(word) <= 40 and word.lower() not in stopwords_new):
    			sent.append(word)
    	return sent

    def tokernizer(self,tagger):
    	stanford_dir = tagger._stanford_jar.rpartition('/')[0]
    	stanford_jars = find_jars_within_path(stanford_dir)
    	tagger._stanford_jar = ':'.join(stanford_jars)
    	#tags = tagger.tag(self.stop_wrds())
    	tags = tagger.tag(word_tokenize(self.sentence))
    	return tags

    def stan_tagger(self):
    	stanford_dir = "/home/vivek/Desktop/Stefano/Code/Algo2/"
    	tagger_filename= stanford_dir + "stanford-postagger/models/english-caseless-left3words-distsim.tagger"
    	my_path_to_jar= stanford_dir + "stanford-postagger/stanford-postagger.jar"
    	nertagger_filename= stanford_dir + "stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz"
    	ner_path_to_jar= stanford_dir + "stanford-ner/stanford-ner.jar"

    	pos_tagger = StanfordPOSTagger(model_filename = tagger_filename,path_to_jar= my_path_to_jar)
    	pos_tags = self.tokernizer(pos_tagger)
    	ner_tagger = StanfordNERTagger(model_filename = nertagger_filename,path_to_jar= ner_path_to_jar)
    	ner_tags = self.tokernizer(ner_tagger)
    	return pos_tags,ner_tags

    def get_continuous_chunks(self):
        print pos_tag(word_tokenize(self.sentence))
        chunked = ne_chunk(pos_tag(word_tokenize(self.sentence)),binary=True)
        prev = None
        continuous_chunk = []
        current_chunk = []
        print chunked
        #chunked.draw()
        for i in chunked:
            if type(i) == Tree:
                print type(i)
                current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            elif current_chunk:
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
            else:
                continue
        return continuous_chunk

class sent_processing():
    def __init__(self):
        self.n_lst = []
        self.lemmatizer = nltk.WordNetLemmatizer() #good for verbs
        self.stemmer = nltk.stem.porter.PorterStemmer() #good for Noun phrases

    def senti_score(self,code,word):
        pos_score,neg_score,all_pos_score,all_neg_score = 0,0,0,0
        for j in range(len(swn.senti_synsets(word))):
            try :
                word_var = swn.senti_synsets(word)[j]
                if str(word_var).split(' ')[0].split('.')[0][1:] == str(self.lemmatizer.lemmatize(word)).lower():
                    if str(word_var).split(' ')[0].split('.')[1] == code:
                        print 'lemmatizer'
                        print str(swn.senti_synsets(word)[j])
                        pos_score += word_var.pos_score() #positive score
                        neg_score += word_var.neg_score() 
                elif str(word_var).split(' ')[0].split('.')[0][1:] == str(self.stemmer.stem_word(word)).lower():
                    if str(word_var).split(' ')[0].split('.')[1] == code:
                        print 'stemmer'
                        print str(swn.senti_synsets(word)[j])
                        pos_score += word_var.pos_score() #positive score
                        neg_score += word_var.neg_score()
                else:
                    print 'all'
                    print str(swn.senti_synsets(word)[j])
                    all_pos_score += word_var.pos_score() #positive score
                    all_neg_score += word_var.neg_score()
            except Exception as e:
                print e
        if pos_score !=0 and neg_score != 0:
            return (pos_score - neg_score)/(pos_score+neg_score)
        else :
            if pos_score:
                return pos_score
            elif neg_score:
                return 0-neg_score
            else:
                if all_pos_score !=0 and all_neg_score != 0:
                    return (all_pos_score - all_neg_score)/(all_pos_score+all_neg_score)
                else :
                    if all_pos_score:
                        return all_pos_score
                    elif all_neg_score:
                        return 0-all_neg_score
                    else:
                        return 0

    def filter_news(self,np_lst,ticker):
        relevant,competitor,general,rival = False,False,False,0.0

        # data = comp_goog_data(ticker)
        # comp_data = data.ticker_comp_details()
        # comp_ticker = data.get_ticker()[0]
        comp_ticker = ticker
        data = comp_file_data(ticker)
        ticker_file_data = data.read_sheet()
        if np_lst:
            for comp in np_lst:
                group = False
                data = comp_goog_data(comp)
                head_ticker = data.get_ticker()[0]
                # for i in comp_data: # if it is one of the subsidiaries
                #     if i==comp:
                #         relevant,general,group = True,'relevant',True
                #         break
                if head_ticker.lower() == comp_ticker.lower(): # if their ticker symbol matches
                    relevant,general,group = True,'relevant',True
                if not group: # if it is a competitor
                    if head_ticker != 'No ticker':
                        data = comp_file_data(head_ticker)
                        head_file_data = data.read_sheet()
                        if head_file_data['Sector'] == ticker_file_data['Sector']:
                            competitor,general = True,'competitor'
                            rival = 0.8
                            if head_file_data['Industry'] == ticker_file_data['Industry']:
                                rival = 1
                        else:
                            rival = 0.2
                with open('fin_words','r') as infile: # it is in the list of general words
                    for line in infile:
                        if str(line).lower() == str(self.lemmatizer.lemmatize(self.stemmer.stem_word(comp))).lower():
                            general = True
                if relevant == True and competitor == True:
                        general = True
        else :
            general = True

        if self.n_lst:
            for noun in self.n_lst:
                with open('fin_words','r') as infile:
                    for line in infile:
                        if str(line.strip()).lower() == str(self.lemmatizer.lemmatize(self.stemmer.stem_word(noun))).lower():
                            general = True

        if relevant or competitor or general:
            return relevant,competitor,general,rival
        else :
            return relevant,competitor,general,rival

    def get_scores(self,pos_tagged):
        word_score = {}
        for i in pos_tagged:
            word,pos,code = str(i[0]), str(i[1]),''
            if pos == 'NN' or pos == 'NNS':
                self.n_lst.append(word)
                code = 'n'
            elif pos == 'VB' or pos == 'VBD' or pos == 'VBG' or pos == 'VBN' or pos == 'VBP' or pos == 'VBZ':
                code = 'v'
            elif pos == 'JJ' or pos == 'JJR' or pos == 'JJS':
                code = 'a'
            elif pos == 'RB' or pos == 'RBR' or pos == 'RBS':
                code = 'r'
            if code:
                #if self.senti_score(code,word): 
                word_score[word] = self.senti_score(code,word)
        return word_score

# sentence = "Stocks dip on earnings and growth worries; dollar rises"
# obj = stanford_nlp(sentence)
# tagged = obj.stan_tagger()
# pos_tagged = tagged[0]
# print pos_tagged
# #name_entries = obj.get_continuous_chunks()
# obj1 = sent_processing()
# word_scores = obj1.get_scores(pos_tagged)
# #relation = obj1.filter_news(name_entries,'jpm')

# print word_scores