#!/usr/bin/env python3

import csv
import json

class Output:

	def __init__(self, output_file, project):
		self.output_file = output_file
		self.project_name = project.project_name
		self.project_id = project.project_id
		self.found_keywords = project.found_keywords

	def csv_output(self):
		try:
			csv_data = [['URL', 'Found Keywords']]
			for result in self.found_keywords:
				url = result['url']
				if len(result['found']) > 1:
					found_keywords = '{0}'.format(', '.join(str(kw).strip() for kw in result['found']))
				else:
					found_keywords = str(result['found'][0]).strip()
				csv_data.append([url, found_keywords])
			with open(self.output_file, 'w') as write_output:
				output_writer = csv.writer(write_output)
				output_writer.writerows(csv_data)
		except:
			raise

	def json_output(self):
		try:
			json_data = {'project_name': self.project_name, 'project_id': self.project_id, 'found_keywords': self.found_keywords}
			with open(self.output_file, 'w') as write_output:
				json.dump(json_data, write_output, indent=2)
				write_output.write('\n')
		except:
			raise
