#!/usr/bin/env python3

# Convert pastebin timestamp to readable date
# Below print 2019-01-07 23:35:55
#from datetime import datetime
#ts = int('1546904155')
#print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))


import json
import requests

from socket import gaierror

from modules.lib.colors import colors

def get_pastes(scrape_history):
	""" Utilizes Pastebin API to search for and gather recent pastes
	"""
	paste_keys = []
	try:
		get_paste_request = requests.get('https://scrape.pastebin.com/api_scraping.php?limit=250')
		paste_list = get_paste_request.json()
		for paste in paste_list:
			paste_key = paste['key']
			user = paste['user']
			date = paste['date']
			if paste_key not in paste_keys and paste_key not in scrape_history:
				paste_keys.append(paste_key)
				"""
				if paste_key not in scrape_history_keys:
					scrape_history_keys.append(paste_key)
					paste_data.append([paste_key, user, date])
				else:
					scrape_history_index = scrape_history_keys.index(paste_key)
					if date > scrape_history[scrape_history_index][2]:
						scrape_history.pop(scrape_history_index)
						scrape_history_keys.pop(scrape_history_index)
						paste_data.append([paste_key, user, date])
				"""
		return paste_keys
	except json.decoder.JSONDecodeError:
		# No new paste data was retrieved
		return None
	except requests.exceptions.RequestException:
		# Abort on requests error
		return None
	except gaierror:
		raise
	except:
		print('{1}{2}[!] Unhandled error occured in modules.scraper.get_pastes.get_pastes{0}'.format(colors.RESET, colors.BOLD, colors.RED))
		raise
