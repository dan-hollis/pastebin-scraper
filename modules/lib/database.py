#!/usr/bin/env python3

import json
import psycopg2

from psycopg2.extras import DictCursor
from psycopg2.extras import Json

from modules.lib.colors import colors

class Database:

	_have_conn = False
	_have_cur = False

	def __init__(self, db_config):
		self.db_config = db_config

	def get_projects(self):
		try:
			conn = psycopg2.connect(**self.db_config)
			self._have_conn = True
			cur = conn.cursor()
			self._have_cur = True
			cur.execute('SELECT * FROM projects')
			return cur.fetchall()
		except psycopg2.DatabaseError as ps_error:
			if 'password authentication failed for user' in str(ps_error):
				print('{1}{2}[!] Invalid database password entered.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			elif 'could not connect to server: Connection refused' in str(ps_error):
				print('{1}{2}[!] Could not connect to postgres. Make sure it is running and config.ini has correct settings.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			else:
				print('{1}{2}[!] Unhandled database error occurred in modules.lib.database.Database.get_clients: {0}{3}'.format(colors.RESET, colors.BOLD, colors.RED, ps_error.__doc__))
			raise
		except Exception as error:
			print('{1}{2}[!] Unhandled error occured in modules.lib.database.Database.get_clients: {0}{3}'.format(colors.RESET, colors.BOLD, colors.RED, error.__doc__))
			raise
		finally:
			if self._have_cur:
				cur.close()
			if self._have_conn:
				conn.close()

	def update_project(self, project):
		try:
			conn = psycopg2.connect(**self.db_config)
			self._have_conn = True
			cur = conn.cursor()
			self._have_cur = True
			cur.execute('UPDATE projects SET found_keywords = %s WHERE project_id = %s', (json.dumps(project['found_keywords']), project['project_id']))
			conn.commit()
		except psycopg2.DatabaseError as ps_error:
			if 'password authentication failed for user' in str(ps_error):
				print('{1}{2}[!] Invalid database password entered.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			elif 'could not connect to server: Connection refused' in str(ps_error):
				print('{1}{2}[!] Could not connect to postgres. Make sure it is running and config.ini has correct settings.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			else:
				print('{1}{2}[!] Unhandled database error occurred in modules.lib.database.Database.update_client: {0}{3}'.format(colors.RESET, colors.BOLD, colors.RED, ps_error.__doc__))
			raise
		except Exception as error:
			print('{1}{2}[!] Unhandled error occured in modules.lib.database.Database.update_client: {0}{3}'.format(colors.RESET, colors.BOLD, colors.RED, error.__doc__))
			raise
		finally:
			if self._have_cur:
				cur.close()
			if self._have_conn:
				conn.close()

	def get_static_data(self):
		try:
			conn = psycopg2.connect(**self.db_config)
			self._have_conn = True
			cur = conn.cursor()
			self._have_cur = True
			cur.execute('SELECT additional_keywords from additional_keywords')
			try:
				keywords = cur.fetchone()[0]
			except TypeError:
				keywords = []
			cur.execute('SELECT scrape_history from scrape_history')
			try:
				scrape_history = cur.fetchone()[0]
			except TypeError:
				scrape_history = []
			return [keywords, scrape_history]
		except psycopg2.DatabaseError as ps_error:
			if 'password authentication failed for user' in str(ps_error):
				print('{1}{2}[!] Invalid database password entered.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			elif 'could not connect to server: Connection refused' in str(ps_error):
				print('{1}{2}[!] Could not connect to postgres. Make sure it is running and config.ini has correct settings.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			else:
				print('{1}{2}[!] Unhandled database error occurred in modules.lib.database.Database.get_static_data: {0}{3}'.format(colors.RESET, colors.BOLD, colors.RED, ps_error.__doc__))
			raise
		except Exception as error:
			print('{1}{2}[!] Unhandled error occured in modules.lib.database.Database.get_static_data: {0}{3}'.format(colors.RESET, colors.BOLD, colors.RED, error.__doc__))
			raise
		finally:
			if self._have_cur:
				cur.close()
			if self._have_conn:
				conn.close()

	def update_scrape_history(self, paste_keys, action=None):
		try:
			conn = psycopg2.connect(**self.db_config)
			self._have_conn = True
			cur = conn.cursor()
			self._have_cur = True
			if not action:
				cur.execute('UPDATE scrape_history SET scrape_history = %s WHERE scrape_history_id = 1', (paste_keys,))
			elif action == 'init':
				cur.execute('INSERT INTO scrape_history (scrape_history) VALUES (%s)', (paste_keys,))
			conn.commit()
		except psycopg2.DatabaseError as ps_error:
			if 'password authentication failed for user' in str(ps_error):
				print('{1}{2}[!] Invalid database password entered.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			elif 'could not connect to server: Connection refused' in str(ps_error):
				print('{1}{2}[!] Could not connect to postgres. Make sure it is running and config.ini has correct settings.{0}'.format(colors.RESET, colors.BOLD, colors.RED))
			else:
				print('{1}{2}[!] Unhandled database error occurred in modules.lib.database.Database.update_scrape_history: {0}{3}'.format(colors.RESET, colors.BOLD, colors.RED, ps_error.__doc__))
			raise
		except Exception as error:
			print('{1}{2}[!] Unhandled error occured in modules.lib.database.Database.update_scrape_history: {0}{3}'.format(colors.RESET, colors.BOLD, colors.RED, error.__doc__))
			raise
		finally:
			if self._have_cur:
				cur.close()
			if self._have_conn:
				conn.close()
