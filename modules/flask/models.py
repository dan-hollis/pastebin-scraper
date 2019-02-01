#!/usr/bin/env python3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class Projects(db.Model):
	__tablename__ = 'projects'

	project_id = db.Column(db.Integer, primary_key=True)
	project_name = db.Column(db.String())
	keywords = db.Column(ARRAY(db.String()))
	found_keywords = db.Column(JSON)
	active = db.Column(db.Boolean, default=True)

	def __init__(self, project_name, keywords, found_keywords, active):
		self.project_name = project_name
		self.keywords = keywords
		self.found_keywords = found_keywords
		self.active = active

	def __repr__(self):
		return str(self.project_id)

class AdditionalKeywords(db.Model):
	__tablename__ = 'additional_keywords'

	additional_keyword_id = db.Column(db.Integer, primary_key=True)
	additional_keywords = db.Column(ARRAY(db.String()))

	def __init__(self, additional_keywords):
		self.additional_keywords = additional_keywords

	def __repr__(self):
		return str(self.additional_keyword_id)

class ScrapeHistory(db.Model):
	__tablename__ = 'scrape_history'

	scrape_history_id = db.Column(db.Integer, primary_key=True)
	scrape_history = db.Column(ARRAY(db.String()))

	def __init__(self, scrape_history):
		self.scrape_history = scrape_history

	def __repr__(self):
		return str(self.scrape_history_id)
