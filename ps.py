#!/usr/bin/env python3

__version__ = '0.2'
__author__ = 'Dan Hollis'

import os
import sys
import traceback

from datetime import datetime
from flask import Flask
from flask import render_template
from flask import request
from getpass import getpass
from sqlalchemy import func
from threading import Thread

from modules.flask.models import AdditionalKeywords
from modules.flask.models import Projects
from modules.flask.models import ScrapeHistory
from modules.flask.models import db
from modules.lib.colors import colors
from modules.lib.config import Config
from modules.lib.output import Output
from modules.scraper.core import run_scraper

# Load configs
config_file = Config(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.ini'))
scraper_config = config_file.scraper_config()
flask_config = config_file.flask_config()
if flask_config['env'] == 'dev':
	password = getpass('Enter database password: ')
elif flask_config['env'] == 'prod':
	password = flask_config['password']
else:
	print('{1}{2}[!] Invalid value {3} given to env setting in [flask] section of config.ini.{0}\n'.format(colors.RESET, colors.BOLD, colors.RED, flask_config['env']))
	sys.exit('{1}{2}[*] Must be either prod or dev. If using prod the database password must be hardcoded in the password option of the [flask] section.{0}'.format(colors.RESET, colors.BOLD, colors.YELLOW))
database_config = config_file.database_config(password)

app = Flask(__name__, template_folder="modules/flask/templates")
app.config['SECRET_KEY'] = flask_config['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{0}:{1}@{2}/{3}'.format('scraper', password, database_config['host'], 'pastebin_scraper')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		try:
			if 'searchProject' in request.form:
				project_name = request.form['searchProject']
				if not project_name:
					project_query_all = db.session.query(Projects).all()
					if project_query_all:
						return render_template('index.html', messages=['Currently exisiting project names:<br>'] + 
							[pa.project_name for pa in project_query_all if pa.active] + 
							['{0} (inactive)'.format(pi.project_name) for pi in project_query_all if not pi.active])
					return render_template('index.html', messages=['No projects currently exist.'])
				project_query = db.session.query(Projects).filter(func.lower(Projects.project_name) == project_name.lower()).first()
				if not project_query:
					return render_template('index.html', messages=['No data found for project {0}'.format(project_name), 'Project does not exist.'])
				results = [project_query.project_name, project_query.keywords, project_query.found_keywords, project_query.active]
				return render_template('index.html', results=results)
			elif 'outputProject' in request.form:
				if not request.form['outputProject'] or not request.form['outputType']:
					return render_template('index.html', messages=['All fields required'])
				project_name = request.form['outputProject']
				project_query = db.session.query(Projects).filter(func.lower(Projects.project_name) == project_name.lower()).first()
				# Validate project name input
				if not project_query:
					return render_template('index.html', messages=['No data found for project {0}'.format(project_name), 'Project does not exist.'])
				output_types = [ot.strip().lower() for ot in request.form['outputType'].split(',')]
				# Validate output type input
				if not set(output_types).issubset({'csv', 'json'}):
					return render_template('index.html', messages=['Invalid output type given<br>Accepts csv and json'])
				if '' in output_types:
					return render_template('index.html', messages=['No blanks allowed in output types'])
				try:
					if flask_config['env'] == 'prod':
						output_dir = ('/var/www/pastebin-scraper/outputs/{0}'.format(project_name))
					else:
						if request.form['outputDir']:
							output_dir = os.path.abspath(request.form['outputDir'])
						else:
							output_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'outputs')
					if not os.path.exists(output_dir):
						os.makedirs(output_dir)
					outputs = []
					for output_type in output_types:
						output_file_path = '{0}/{1}_{2}.{3}'.format(output_dir, project_name, datetime.now().strftime('%m%d%Y'), output_type)
						output_file = Output(output_file_path, project_query)
						if output_type == 'csv':
							output_file.csv_output()
						elif output_type == 'json':
							output_file.json_output()
						outputs.append(output_file_path)
				except PermissionError:
					return render_template('index.html', messages=['You don\'t have permission to access directory<br>{0}'.format(output_dir)])
				except Exception:
					return render_template('error.html', errors=traceback.format_exception(*sys.exc_info()))
				return render_template('index.html', messages=['Output saved to<br>{0}<br>'.format('<br>'.join(outputs))])
			elif 'createProject' in request.form:
				project_name = request.form['createProject']
				keywords = [kw.strip() for kw in request.form['keywords'].split(',')]
				if not project_name or not request.form['keywords']:
					return render_template('index.html', messages=['All fields required'])
				if '' in keywords:
					return render_template('index.html', messages=['No blanks allowed in keywords<br>e.g. word1, ,word2'])
				project_query = db.session.query(Projects).filter(func.lower(Projects.project_name) == project_name.lower()).first()
				if project_query:
					results = [project_query.project_name, project_query.keywords, project_query.found_keywords]
					return render_template('index.html', results=results, messages=['Project {0} already exists'.format(results[0])])
				project = Projects(project_name, keywords, [], active=True)
				db.session.add(project)
				db.session.commit()
				return render_template('index.html', messages=['Created project {0}'.format(project_name)])
			elif 'updateProject' in request.form:
				if not request.form['addKeywords'] and not request.form['removeKeywords']:
					return render_template('index.html', messages=['No keywords supplied'])
				add_keywords = ''
				remove_keywords = ''
				if request.form['addKeywords']:
					add_keywords = [add_kw.strip() for add_kw in request.form['addKeywords'].split(',')]
					if '' in add_keywords:
						return render_template('index.html', messages=['No blanks allowed in keywords<br>e.g. word1, ,word2'])
				if request.form['removeKeywords']:
					remove_keywords = [remove_kw.strip() for remove_kw in request.form['removeKeywords'].split(',')]
					if '' in remove_keywords:
						return render_template('index.html', messages=['No blanks allowed in keywords<br>e.g. word1, ,word2'])
				project_name = request.form['updateProject']
				if (add_keywords or remove_keywords) and not project_name:
					return render_template('index.html', messages=['All fields required'])
				project_query = db.session.query(Projects).filter(func.lower(Projects.project_name) == project_name.lower()).first()
				if not project_query:
					return render_template('index.html', messages=['No data found for project {0}'.format(project_name), 'Project does not exist.'])
				current_keywords = project_query.keywords
				if add_keywords:
					current_keywords = current_keywords + [add_kw for add_kw in add_keywords if add_kw not in current_keywords]
					project_query.keywords = current_keywords
					db.session.commit()
				if remove_keywords:
					if not set(remove_keywords).issubset(current_keywords):
						return render_template('index.html', messages=['Keywords were entered to be removed that do not exist for project. Search for the project to check it\'s keywords.'])
					new_keywords = [new_kw for new_kw in current_keywords if new_kw not in remove_keywords]
					project_query.keywords = new_keywords
					db.session.commit()
				return render_template('index.html', messages=['Updated project {0}'.format(project_name)])
			elif 'deleteProject' in request.form or 'deactivateProject' in request.form:
				if request.form['deleteProject']:
					project_name = request.form['deleteProject']
				else:
					project_name = request.form['deactivateProject']
				if not project_name:
					return render_template('index.html', messages=['No project name given.'])
				project_query = db.session.query(Projects).filter(func.lower(Projects.project_name) == project_name.lower()).first()
				if not project_query:
					return render_template('index.html', messages=['No data found for project {0}'.format(project_name), 'Project does not exist.'])
				if request.form['deleteProject']:
					project_id = project_query.project_id
					Projects.query.filter_by(project_id=project_id).delete()
					db.session.commit()
					return render_template('index.html', messages=['Deleted project {0}'.format(project_name)])
				else:
					project_query.active = False
					db.session.commit()
					return render_template('index.html', messages=['Deactivated project {0}'.format(project_name)])
			elif 'reactivateProject' in request.form:
				project_name = request.form['reactivateProject']
				if not project_name:
					return render_template('index.html', messages=['No project name given.'])
				project_query = db.session.query(Projects).filter(func.lower(Projects.project_name) == project_name.lower()).first()
				if not project_query:
					return render_template('index.html', messages=['No data found for project {0}'.format(project_name), 'Project does not exist.'])
				project_query.active = True
				db.session.commit()
				return render_template('index.html', messages=['Reactivated project {0}'.format(project_name)])
			elif 'addCrossProjectKeywords' in request.form:
				keywords = [kw.strip() for kw in request.form['addCrossProjectKeywords'].split(',')]
				cross_project_query = db.session.query(AdditionalKeywords).filter(AdditionalKeywords.additional_keyword_id == 1).first()
				if not cross_project_query:
					if '' in keywords:
						return render_template('index.html', messages=['No blanks allowed in keywords<br>e.g. word1, ,word2'])
					additional_keywords = AdditionalKeywords(keywords)
					db.session.add(additional_keywords)
					db.session.commit()
					return render_template('index.html', messages=['Updated cross project keywords'])
				current_additional_keywords = cross_project_query.additional_keywords
				if not request.form['addCrossProjectKeywords']:
					if current_additional_keywords:
						return render_template('index.html', additional_keywords=current_additional_keywords)
					else:
						return render_template('index.html', messages=['All fields required'])
				if '' in keywords:
					return render_template('index.html', messages=['No blanks allowed in keywords<br>e.g. word1, ,word2'])
				current_additional_keywords = current_additional_keywords + [new_add_kw for new_add_kw in keywords if new_add_kw not in current_additional_keywords]
				cross_project_query.additional_keywords = current_additional_keywords
				db.session.commit()
				return render_template('index.html', messages=['Updated cross project keywords'])
			elif 'removeCrossProjectKeywords' in request.form:
				keywords = [kw.strip() for kw in request.form['removeCrossProjectKeywords'].split(',')]
				cross_project_query = db.session.query(AdditionalKeywords).filter(AdditionalKeywords.additional_keyword_id == 1).first()
				current_additional_keywords = cross_project_query.additional_keywords
				if not cross_project_query or not current_additional_keywords:
					return render_template('index.html', messages=['No cross project keywords found.'])
				if not request.form['removeCrossProjectKeywords']:
					if current_additional_keywords:
						return render_template('index.html', additional_keywords=current_additional_keywords)
					else:
						return render_template('index.html', messages=['All fields required'])
				if not set(keywords).issubset(current_additional_keywords):
					return render_template('index.html', messages=['Cross project keywords were entered to be removed that do not exist in the database'])
				current_additional_keywords = [new_add_kw for new_add_kw in current_additional_keywords if new_add_kw not in keywords]
				cross_project_query.additional_keywords = current_additional_keywords
				db.session.commit()
				return render_template('index.html', messages=['Updated cross project keywords'])
		except Exception:
			return render_template('error.html', errors=traceback.format_exception(*sys.exc_info()))
	return render_template('index.html')

if __name__ == '__main__':
	try:
		print('Starting scraper...')
		scrape_thread = Thread(target=run_scraper, args=(database_config, scraper_config))
		scrape_thread.daemon = True
		scrape_thread.start()
		if flask_config['env'] == 'dev':
			app.run(debug=False, host=flask_config['host'], port=flask_config['port'])
		scrape_thread.join()
		sys.exit('\nExiting...')
	except KeyboardInterrupt:
		sys.exit('\nExiting...')
	except Exception:
		sys.exit(''.join(traceback.format_exception(*sys.exc_info())))
