#!/usr/bin/env python3

import os
import sys
import traceback

from socket import gaierror
from time import sleep
from time import time

from modules.lib.colors import colors
from modules.lib.database import Database
from modules.scraper.get_pastes import get_pastes
from modules.scraper.scrape_paste_data import scrape_paste_data

def scraper(projects, static_data, db, history_limit):
	additional_keywords = static_data[0]
	scrape_history = static_data[1]
	start_time = time()
	try:
		paste_keys = get_pastes(scrape_history)
		if paste_keys:
			if scrape_history:
				if len(scrape_history) <= history_limit:
					db.update_scrape_history(paste_keys + scrape_history)
				else:
					db.update_scrape_history(paste_keys)
			else:
				db.update_scrape_history(paste_keys, action='init')
			if projects:
				for project in projects:
					for paste_key in paste_keys:
						current_project = scrape_paste_data(project, additional_keywords, paste_key)
						if current_project:
							db.update_project(current_project)
						sleep(1)
		run_time = int(time() - start_time)
		if run_time < 60:
			# Must wait 60 seconds between fetching new pastes
			# Pauses 1 second between scraping pastes
			# run_time < 60 means less than 60 pastes scraped
			sleep(int(60 - run_time))
	except gaierror:
		print('{1}{2}[!] Timeout error occured. Possible loss of internet connection.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
		print('{1}{2}[!] Retrying in 60 seconds...{0}\n'.format(colors.RESET, colors.BOLD, colors.RED))
		sleep(60)
		return
	except KeyboardInterrupt:
		raise
	except:
		print('{1}{2}[!] Unhandled error occured in modules.scraper.core.scraper{0}'.format(colors.RESET, colors.BOLD, colors.RED))
		raise

def run_scraper(database_config, scraper_config):
	while True:
		try:
			db = Database(database_config)
			project_list = db.get_projects()
			static_data = db.get_static_data()
			projects = []
			history_limit = int(scraper_config['history_limit'])
			if project_list:
				for project_data in project_list:
					if project_data[4]:
						projects.append({'project_id': project_data[0], 'project_name': project_data[1], 
							'keywords': project_data[2], 'found_keywords': project_data[3]})
				scraper(projects, static_data, db, history_limit)
		except KeyboardInterrupt:
			raise
		except:
			print('{1}{2}[!] Error occurred in scraping thread. Scraper is no longer running.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			print(''.join(traceback.format_exception(*sys.exc_info())))
			print('{1}{2}[!] Web server may be running but scraper is not. No pastes new pastes will be fetched, and the database cannot be updated.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			sys.exit()
