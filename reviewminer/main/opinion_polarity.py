from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

paragraph = "test!"

sentences = tokenize.sent_tokenize(paragraph)
sid = SentimentIntensityAnalyzer()

opinion=[]
sum1=[0.0,0.0,0.0,0.0]


for sentence in sentences:
	n=0
   	ss = sid.polarity_scores(sentence)
   	for k in sorted(ss):
   		sum1[n]+=ss[k]
   		n=n+1

avg = [x/n for x in sum1] 
print avg


