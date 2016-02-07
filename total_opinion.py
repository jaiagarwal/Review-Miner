from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

paragraph = "It was one of the worst movies I've seen, despite good reviews. \
 Unbelievably bad acting!! Poor direction. VERY poor production. \
 The movie was bad. Very bad movie. VERY bad movie. VERY BAD movie. VERY BAD movie!"

sentences = tokenize.sent_tokenize(paragraph)
sid = SentimentIntensityAnalyzer()

opinion=[]
sum=[0.0,0.0,0.0,0.0]


for sentence in sentences:
	n=0
   	ss = sid.polarity_scores(sentence)
   	for k in sorted(ss):
   		sum[n]+=ss[k]
   		n=n+1

avg = [x / n for x in sum] 
print avg


