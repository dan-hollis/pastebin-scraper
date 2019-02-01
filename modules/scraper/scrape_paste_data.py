#!/usr/bin/env python3

import re
import requests

from socket import gaierror

from modules.lib.colors import colors

def scrape_paste_data(project, additional_keywords, paste_key):
	""" Utilizes Pastebin API to scrape gathered pastes and search for keywords
	"""
	try:
		url = 'https://scrape.pastebin.com/api_scrape_item.php?i={0}'.format(paste_key)
		scrape_paste_request = requests.get(url)
		paste_data = scrape_paste_request.text
		current_finds = []
		checked_additional = False
		for keyword in project['keywords']:
			if keyword.endswith('(e)'):
				keyword_regex = r'\b{0}\b'.format(keyword[:-4])
			else:
				keyword_regex = keyword
			if re.findall(keyword_regex, paste_data, flags=re.IGNORECASE):
				current_finds.append(keyword)
				if additional_keywords and not checked_additional:
					for additional_keyword in additional_keywords:
						if additional_keyword.endswith('(e)'):
							additional_keyword_regex = r'\b{0}\b'.format(additional_keyword[:-4])
						else:
							additional_keyword_regex = additional_keyword
						if re.findall(additional_keyword_regex, paste_data, flags=re.IGNORECASE):
							current_finds.append(additional_keyword)
					checked_additional = True
		if current_finds:
			project['found_keywords'].append({'url': url, 'found': current_finds})
			return project
		else:
			return None
	except requests.exceptions.RequestException:
		# Abort on requests error
		return None
	except gaierror:
		raise
	except KeyboardInterrupt:
		raise
	except:
		print('{1}{2}[!] Unhandled error occured in modules.scraper.scrape_paste_data.scrape_paste_data{0}'.format(colors.RESET, colors.BOLD, colors.RED))
		raise
