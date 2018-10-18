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
##############################
# THERE WERE UPDATES TO GET THIS TO WORK ON HEROKU
# set up a heroku account
# set up a github account
# connected heroku to github
#############
# ADD THIS:
#####
# import os
# factivatoken = os.environ['FACTIVATOKEN']
# slacktokenvalue = os.environ['SLACKTOKEN']
# snippetvalue = os.environ['SNIPPETS']
# urlvalue = os.environ['URLS']
###
# create heroku config variables for:
# FACTIVATOKEN with the Factiva auth token
# SLACKTOKEN with the slack token
# SNIPPETS set to on
# URLS set to on
############
# create a file on GitHub called Profile that just says
# web: python slackfactiva.py
# this is what makes the Heroku dyno run, which makes the webserver work
# note -- this code will run once then crash, maybe because all it does is call a Slack API, and has nothing to do afterwards?
# so I am looking into scheduling a job for it
# I created a readme in github
# I created a requirements.txt file, which triggers heroku to know that it is a python thing, and just entered slackclient==1.3.0 -- so that it would import that requirement
# I changed the Python run time by creating a file called runtime.txt with just this in it: python-2.7.15
# github is set to automatically deploy to master
#
######
#
# now I am trying to schedule the job -- followed these steps:
# https://devcenter.heroku.com/articles/clock-processes-python
# 
# added Scheduler to heroku using command line:
# needed to add my credit card in web interface:
# https://dashboard.heroku.com/account/billing)
# 
# added this to requirements.txt
# APScheduler==3.0.0
#
####
# created clock.py:
# from apscheduler.schedulers.blocking import BlockingScheduler
#
# sched = BlockingScheduler()
# 
# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=9)
# def scheduled_job():
#    print('This job is run every weekday at 9am.')
#    slackfactiva.py

# sched.start()
###
#
# added this to the Procfile:
# clock: python clock.py
# 
# I am leaving off with heroku crashing, because the page needs something to be running, basically. Perhaps I'll have the page do a redirect after it loads, so it doesn't crash, using something to answer this issue: https://www.reddit.com/r/learnprogramming/comments/2ra2yd/what_makes_a_heroku_app_crash/
# 
# also I am starting to add things from here to try to get a webserver running https://devcenter.heroku.com/articles/django-app-configuration
# down the rabbit hole:
# https://devcenter.heroku.com/articles/getting-started-with-python
# https://docs.python-guide.org/starting/install3/osx/
# https://hathaway.cc/2008/06/how-to-edit-your-path-environment-variables-on-mac/ -- specifically used touch ~/.bash_profile; open ~/.bash_profile
# and in case you are curious: https://unix.stackexchange.com/questions/111550/what-is-path-on-a-mac-os
# # Do I have a Python 3 installed?
# $ python --version
# Python 3.6.4 # Success!
# If you still see 2.7 ensure in PATH /usr/local/bin/ takes 
# precedence over /usr/bin/
# but I still haven't gotten that to work, I enter
# python --version
# and still get 2.7.10
#########################


########################## slackfactiva.py
import slackclient
import json
import urllib
import time
from slackclient import SlackClient
import urllib2
import sys, getopt
##########################
# IF YOU RUN ON HEROKU THEN YOU WILL NEED TO:
# change the arguments below to use os instead, like it says above
#
whosealerts = "Here you go:"
factivatoken = sys.argv[1]
slacktokenvalue = sys.argv[2]
snippetvalue=sys.argv[3]
urlvalue = sys.argv[4]
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
			values = json.load(f)
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





