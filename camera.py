
import nltk
import random
from collections import defaultdict
from nltk.probability import FreqDist, DictionaryProbDist, ELEProbDist, sum_logs
from nltk.classify.api import ClassifierI
from nltk.corpus import product_reviews_1

v= product_reviews_1.features('Canon_G3.txt')
res=[]
for k in v:
	if int(k[1])>0:
		ans = (k[0].split(), '1')
	elif int(k[1]) < 0:
		ans = (k[0].split(), '-1')
	res.append(ans)
random.shuffle(res)

all_words = nltk.FreqDist(w.lower() for w in product_reviews_1.words('Canon_G3.txt'))
word_features = all_words.keys()[:2000]

def document_features(document):
	document_words = set(document)
	features = {}
	for word in word_features:
		features['%s' % word] = (word in document_words)
	return features

featuresets = [(document_features(d), c) for (d,c) in res]
train_set, test_set = featuresets[50:], featuresets[:50]
classifier = nltk.NaiveBayesClassifier.train(train_set)

data1=[]
cpdist = classifier._feature_probdist
for (fname, fval) in classifier.most_informative_features(5):
	def labelprob(l):
		return cpdist[l, fname].prob(fval)
	labels = sorted([l for l in classifier._labels
					 if fval in cpdist[l, fname].samples()],
					key=labelprob)
	if len(labels) == 1:
		continue
	l0 = labels[0]
	l1 = labels[-1]
	if cpdist[l0, fname].prob(fval) == 0:
		ratio = 'INF'
	else:
		ratio = '%8.1f' % (cpdist[l1, fname].prob(fval) /
						   cpdist[l0, fname].prob(fval))
	x = (fname, fval, l1, ratio.strip())
	data1.append(x)
print data1