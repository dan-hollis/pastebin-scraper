#!/usr/bin/env python3

# Directories labeled /PASTEBIN-SCRAPER/ should be changed to the root directory of pastebin-scraper
# e.g. /opt/pastebin-scraper

import sys
# Change directory below to root directory of pastebin-scraper
sys.path.append('/PASTEBIN-SCRAPER/')

# Change directory below to location of activate_this.py
# This will be located in the env/bin directory of pastebin-scraper root
activate_this = '/PASTEBIN-SCRAPER/env/bin/activate_this.py'
with open(activate_this) as file_:
	exec(file_.read(), dict(__file__=activate_this))

from ps import app as application