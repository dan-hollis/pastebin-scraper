#!/usr/bin/env python3

import os

from configparser import ConfigParser

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	def __init__(self, filename):
		self.parser = ConfigParser()
		self.parser.read(filename)

	def database_config(self, password, section='postgresql'):
		params = self.parser.items(section)
		config_dict = {'password': password, 'user': 'scraper', 'dbname': 'pastebin_scraper'}
		for param in params:
			config_dict[param[0]] = param[1]
		return config_dict

	def flask_config(self, section='flask'):
		params = self.parser.items(section)
		config_dict = {}
		for param in params:
			config_dict[param[0]] = param[1]
		return config_dict

	def scraper_config(self, section='scraper'):
		params = self.parser.items(section)
		config_dict = {}
		for param in params:
			config_dict[param[0]] = param[1]
		return config_dict
