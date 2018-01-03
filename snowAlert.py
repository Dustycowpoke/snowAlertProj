# !python 3
# snowAlert.py - scrapes Royal Oak Website to chack for snow emergency
# then texts info to phone

import bs4
import requests
import json
from twilio.rest import Client
import time
import datetime
import re
from snowAlert_pass import *

# set static URLs
URL = 'https://www.romi.gov' # URL to check for snow emergency declarations
LOCATION = '4990729' # Royal Oak city ID for openweathermap
WEATHER_KEY = GITHUB_WEATHER_KEY
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/forecast?id=%s&appid=%s' % (LOCATION, WEATHER_KEY)

# Set Twilio static variables
account_SID = github_account_SID
auth_token = github_auth_token
twilio_number = github_twilio_number
call_to = github_call_to

# Add while loop here to handle connection errors
def check_weather():
	
	print('Checking weather...')
	response = requests.get(WEATHER_URL)
		
	# Make sure download was successful
	if response.status_code == 200:
		print('Weather info downloaded successfully.')
	else:
		print('Weather data could not be downloaded.')
		
	weather_data = json.loads(response.text)
	
	# Parse JSON and check for snow
	# if no snow, wait 1 hour and request again
	today_weather = weather_data['list'][0]['weather'][0]['main']
	
	if today_weather == "Snow":
		snow_emergency_check()
	else:
		print('No snow detected at %s. Sleeping for 1 hour...' % datetime.datetime.now().strftime('%H:%M'))
		time.sleep(60 * 60) # sleep for 1 hr until update 

# this section needs cleanup
# Logic could be better - needs to check for snow and not just for any alert
def snow_emergency_check():
	# create object of site's code
	site = requests.get(URL)
	
	# Make sure results are downloaded successfully
	if site.status_code == 200:
		print('Site info downloaded successfully.')
	else:
		print('Site not contacted')
		
	# create doc of site's code
	site_html_doc = site.text
	
	# create soup object
	soup = bs4.BeautifulSoup(site_html_doc, 'html.parser')
		
	try:
		warning_msg = soup.find('span', attrs={'id':'1_spnAlertContainer'})
		warning_msg_doc = warning_msg.text
		match = re.search(r'[Ss]now.+[Ee]mergency', warning_msg_doc)
		
		if match:
			print('Snow emergency declared. Texting %s...' % call_to)
			texter()
		else:
			print('No emergency declared. Checking weather in 15...')
			time.sleep(60 * 15)
			check_weather()
	
	except:
		print('No emergency declared. Back to checking weather...')
		check_weather()
		
def texter():
	print('Texting %s' % twilio_number)
	
	client = Client(account_SID, auth_token)
	
	client.api.account.messages.create(
	to = call_to,
	from_ = twilio_number,
	body = 'Snow alert! Move your car!')
	
	print('Snow alerts last for 24 hours. Sleeping until then...')
	time.sleep(60 * 24) 
	check_weather()

check_weather()

	
