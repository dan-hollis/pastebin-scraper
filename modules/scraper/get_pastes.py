#!/usr/bin/env python3

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
		return paste_keys
	except json.decoder.JSONDecodeError:
		# No new paste data was retrieved
		return None
	except requests.exceptions.RequestException:
		# Abort on requests error
		return None
	except gaierror:
		raise
	except KeyboardInterrupt:
		raise
	except:
		print('{1}{2}[!] Unhandled error occured in modules.scraper.get_pastes.get_pastes{0}'.format(colors.RESET, colors.BOLD, colors.RED))
		raise
