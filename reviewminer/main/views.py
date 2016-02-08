from django.template import RequestContext
from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect,Http404,HttpResponse, JsonResponse
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import requests
from bs4 import BeautifulSoup
import difflib
import nltk
import random
from collections import defaultdict
from nltk.probability import FreqDist, DictionaryProbDist, ELEProbDist, sum_logs
from nltk.classify.api import ClassifierI
from nltk.corpus import product_reviews_1
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from main import classify, opinion_polarity
from nltk import NaiveBayesClassifier




def test(request):
	return HttpResponse('Gaussian server test')

@csrf_exempt
def review_func(request):
	if request.POST:
		if int(request.POST['website']) == 1:
			url= request.POST.get('url',False)
			r_ob = requests.get(url)
			gaussian = BeautifulSoup(r_ob.content)
			rev_list = gaussian.find_all("span", {"class": "MHRHead"})
			if not rev_list:
				rev_list= gaussian.find_all("div", {"class" : "a-section"})
			result= [i.text for i in rev_list]
			full= str(result)
		else:
			url= request.POST.get('url',False)
			r_ob = requests.get(url)
			gaussian = BeautifulSoup(r_ob.content)
			rev_list = gaussian.find_all("span", {"class": "review-text-full"})
			result= [i.text for i in rev_list]
			full= str(result)
	else:
		# url="http://www.amazon.com/Nokia-Lumia-900-Black-16GB/dp/B007P5NHJO"
		url="http://www.flipkart.com/nokia-lumia-630-dual-sim/p/itme7zdakdtxxmdy?pid=MOBDW52BQYEQNQHG&al=rr4jU3t8xiLfxoSVreiBF8ldugMWZuE7Qdj0IGOOVqtGps%2B5%2BbFNcBLbBYY0ImV%2FholPQluhdKA%3D&ref=L%3A-7980544905708093331&srno=b_1"
		r_ob = requests.get(url)
		gaussian = BeautifulSoup(r_ob.content)
		rev_list = gaussian.find_all("span", {"class": "review-text-full"})
		result= [i.text for i in rev_list]
		full= str(result)
	sentences = tokenize.sent_tokenize(full)
	sid = SentimentIntensityAnalyzer()

	opinion=[]
	sumz=[0.0,0.0,0.0,0.0]

	tot=0
	for sentence in sentences:
		n=0
		tot+=1
	   	ss = sid.polarity_scores(sentence)
	   	for k in sorted(ss):
	   		sumz[n]+=ss[k]
	   		n=n+1

	final= {} 
	avg = [x/tot for x in sumz] 
	final['senti'] = avg
	v= product_reviews_1.features('gauss_data_set.txt') 
	gauss=[]
	for k in v:
		if int(k[1])>0:
			ans = (k[0].split(), '1')
		elif int(k[1]) < 0:
			ans = (k[0].split(), '-1')
		gauss.append(ans)
	random.shuffle(gauss)

	all_words = nltk.FreqDist(w.lower() for w in full.split())
	word_features = all_words.keys()[:2000]

	def document_features(document):
		document_words = set(document)
		features = {}
		for word in word_features:
			features['%s' % word] = (word in document_words)
		return features

	featuresets = [(document_features(d), c) for (d,c) in gauss]
	train_set= featuresets
	classifier = NaiveBayesClassifier.train(train_set)

	data1=[]
	cpdist = classifier._feature_probdist
	for (fname, fval) in classifier.most_informative_features(10):
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
		if str(x[0]).upper() != 'PHONE' and str(x[0]).upper() != 'MOBILE' and str(x[0]).upper() != 'CUSTOMER':
			data1.append(x)
	if data1:
		data2=[]
		for p in data1:
			if p[0] not in [q[0] for q in data2]:
				data2.append(p)
		sol=[]
		# name_list= [q[0] for q in data1]
		for k in data2:
			resp={}
			resp['name'] = str(k[0])
			resp['val'] = k[1]
			resp['l'] = k[2]
			resp['ratio'] = k[3]
			sol.append(resp)
		final['feature'] = sol
		return JsonResponse(final, safe=False)
	else:
		return HttpResponse('0')



@csrf_exempt	
def register(request):
	if request.POST:
		username= str(request.POST['username'])
		email_id= str(request.POST['email'])
		password= str(request.POST['password'])
		try:
			user = User.objects.create_user(username=username, email=email_id, password=password)
			return HttpResponse('1')
		except:
			return HttpResponse('0')

@csrf_exempt
def login(request):
	if request.POST:
		username= str(request.POST['username'])
		password= str(request.POST['password'])
		user = authenticate(username=username, password=password)
		if user:
			return HttpResponse('1')
		else:
			return HttpResponse('0')		