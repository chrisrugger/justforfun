# TO SET THIS UP ON A NEW MACHINE
# First get pip here: https://pip.pypa.io/en/stable/installing/
# then download slackclient https://github.com/slackhq/python-slackclient
# Open Terminal on your Mac
# use cd to get to the right directory:
# then run these commands -- sudo uses admin rights, so you'll need to put in your Mac password 
# sudo python get-pip.py
# sudo pip install requests[security]
# or just
# sudo -H pip install requests
# sudo -H pip install websocket
# cd python-slackclient-master
# sudo -H pip install slackclient
# and then run this command line -- you need to get a Factiva access token from http://api.dowjones.com/api/3.0/swagger/ui/index#!/
# python factivaslack.py <accesstoken>
# then make sure you're signed into Slack wherever you specify the Slack access token to go to

########################## factivaslack.py
import slackclient
import json
import urllib
import time
from slackclient import SlackClient
import urllib2
import sys, getopt
import os
##########################
whosealerts = "Here you go:"
factivatoken = os.environ['FACTIVATOKEN']
slacktokenvalue = os.environ['SLACKTOKEN']
snippetvalue = os.environ['SNIPPETS']
urlvalue = os.environ['URLS']
#factivatoken = sys.argv[1]
#slacktokenvalue = sys.argv[2]
#snippetvalue=sys.argv[3]
#urlvalue = sys.argv[4]
def sendSlackMyNewHeadlines(accesstokenvar,slacktokenvar,snippetvar,urlvar):
	accesstoken=accesstokenvar
	slacktoken=slacktokenvar
	snippets=snippetvar
	urls=urlvar
	alertlist ='http://api.dowjones.com:80/api/3.0/alerts?filter.product_type=Factiva&parts=NewArticlesCount&access_token='+accesstoken
	al= urllib.urlopen(alertlist)
	alj=json.load(al)
	al.close()
	aname=""
	articlelist = ""
	numnew = ""
	h=""
	numalerts = alj['meta']['count']
	numalertswithnew = 0
	sc = SlackClient(slacktoken)
	# get headlines for each alert
	for q in range (0, numalerts):
		if alj['data'][q]['attributes']['new_hits_count'] !=0:
			numalertswithnew = numalertswithnew + 1
			aname = '\n*' + alj['data'][q]['attributes']['name'] + '*\n'
			# get articles for the alert
			articlelist='http://api.dowjones.com:80/api/3.0/alerts/' + alj['data'][q]['id'] + '/articles?filter.view_type=New&deduplication_level=Similar&access_token='+accesstoken
			f = urllib.urlopen(articlelist)   
 			values=json.load(f)
			f.close()
			# get only the number of articles for the alert that there are new-hits-count, and then only show up to 10
			numnew = alj['data'][q]['attributes']['new_hits_count']
			if numnew > 10:
				numnew = 10
			else:
				numnew = numnew
			h = h + aname + ' _' + str(numnew) +' new headline'
			if numnew > 1:
				h = h + '(s)_\n'
			else:
				h = h + '_\n'
			# also want to count number of headlines since numnew seems wrong - like we get too many hits in the hit counter, not matching number of headlines returned - new_hits_count is consistently one too large
			numnew2 = len(values['data'])
			numnew = numnew2
			for x in range (0, numnew):
				if x==numnew:
					break
				else:
					# what I want to do is say if it is an entity reference, then find the next text as well and add it
					lenarr = len(values['data'][x]['attributes']['headline']['items'])
					for hh in range (0, lenarr):
						# build the headline, could include multiple objects
						if lenarr > 1:
							if 'text' in values['data'][x]['attributes']['headline']['items'][hh]['text'][0]:
								h = h + '_' + values['data'][x]['attributes']['headline']['items'][hh]['text'][0]['text']
							else:
								h = h + '_' + values['data'][x]['attributes']['headline']['items'][hh]['text']
						else:
							h = h + '_' + values['data'][x]['attributes']['headline']['items'][hh]['text']
					h = h + '_\n'
					if snippets == "on":
						h = h + ' ' + values['data'][x]['attributes']['snippet']['items'][0]['text'] + '\n'
					if urls == "on":
						h = h + ' ' + values['data'][x]['links']['share'] + '\n'
					h = h +'\n'
			else:
				h = h + '\n:tada:\n'
	if numalertswithnew==0:
		h = h + '\n:no_mouth:'
	else:
		h = h + '\n:wave:'
	h = whosealerts + '\n' + h
	sc.api_call("chat.postMessage", channel="C0UUP7PT5", text= h, username='Gowanus_Bot', icon_url='https://modernmythologies.files.wordpress.com/2014/08/swampthing.png')

sendSlackMyNewHeadlines(factivatoken,slacktokenvalue,snippetvalue,urlvalue)





