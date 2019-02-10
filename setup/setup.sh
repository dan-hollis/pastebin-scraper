#!/bin/bash

RED="\033[01;31m"
GREEN="\033[01;32m"
YELLOW="\033[01;33m"
BOLD="\033[01;01m"
RESET="\033[00m"

if [[ $EUID -ne 0 ]]; then
   echo -e "${BOLD}${RED}Setup script must be run as root.${RESET}"
   exit 1
fi

script_path="$(cd "$(dirname "$0")"; pwd -P)"

# Store postgresql database password
clear;echo -e "${BOLD}${RED}[!] Don't forget your database password!${RESET}"
echo -e "${BOLD}${YELLOW}[*] You will be prompted for it 3 times during setup while the database initializes, and every time you run ps.py${RESET}"
passwords_match=0
while [ $passwords_match -eq 0 ]; do
	read -s -p "Enter password to be used for database access: " password
	if [ -z "$password" ]; then
		clear;echo -e "${BOLD}${RED}[!] Don't forget your database password!${RESET}"
		echo -e "${BOLD}${YELLOW}[*] You will be prompted for it 3 times during setup while the database initializes, and every time you run ps.py${RESET}"
		echo;echo -e "${BOLD}${RED}[!] Password can't be blank.${RESET}"
		continue
	fi
	echo;read -s -p "Confirm password to be used for database access: " password_check
	if [ "$password" = "$password_check" ]; then
		passwords_match=1
		continue
	fi
	clear;echo -e "${BOLD}${RED}[!] Don't forget your database password!${RESET}"
	echo -e "${BOLD}${YELLOW}[*] You will be prompted for it 3 times during setup while the database initializes, and every time you run ps.py${RESET}"
	echo;echo -e "${BOLD}${RED}[!] Passwords didn't match.${RESET}"
done

# Make sure postgresql is installed and running
echo;echo;echo -e "${YELLOW}[*] Updating system...${RESET}"
apt-get update
apt-get install -y postgresql postgresql-contrib libpq-dev apache2-dev libapache2-mod-wsgi-py3 python3-dev python3-distutils-extra python3-dbus python-apt libsystemd-dev libglib2.0-dev libgirepository1.0-dev libcairo2-dev
service apache2 restart
a2enmod wsgi >/dev/null 2>&1
service postgresql start
echo -e "${GREEN}[*] Done${RESET}";echo

# Set up the database
echo -e "${YELLOW}[*] Setting up the database...${RESET}"
cd ~postgres/
check_database=$(sudo -u postgres psql -c "\\l" | grep pastebin_scraper)
continue_setup=""
if [ ! -z "$check_database" ]; then
	while [ -z "$continue_setup" ]; do
		echo;echo -e "${BOLD}${RED}[!] Database ${RESET}pastebin_scraper ${BOLD}${RED}already exists.${RESET}"
		echo -e "${BOLD}${YELLOW}[?] Do you want to wipe the database before continuing setup?${RESET}"
		read -p "(y/n): " continue_setup
		if [ "$continue_setup" = "y" ]; then
			sudo -u postgres psql -c "drop database pastebin_scraper" >/dev/null 2>&1
			sudo -u postgres psql -c "create database pastebin_scraper" >/dev/null 2>&1
			sudo -u postgres psql -c "drop user scraper" >/dev/null 2>&1
			sudo -u postgres psql -c "create user scraper with encrypted password '$password'" >/dev/null 2>&1
			sudo -u postgres psql -c "grant all privileges on database pastebin_scraper to scraper" >/dev/null 2>&1
		elif [ "$continue_setup" = "n" ]; then
			break
		else
			continue_setup=""
		fi
	done
else
	sudo -u postgres psql -c "drop database pastebin_scraper" >/dev/null 2>&1
	sudo -u postgres psql -c "create database pastebin_scraper" >/dev/null 2>&1
	sudo -u postgres psql -c "drop user scraper" >/dev/null 2>&1
	sudo -u postgres psql -c "create user scraper with encrypted password '$password'" >/dev/null 2>&1
	sudo -u postgres psql -c "grant all privileges on database pastebin_scraper to scraper" >/dev/null 2>&1
fi
echo -e "${GREEN}[*] Done${RESET}";echo

# Make sure pip is set up properly
echo -e "${YELLOW}[*] Setting up pip...${RESET}"
cd "$script_path/.."
wget -N https://bootstrap.pypa.io/get-pip.py
python3 -m pip install --upgrade setuptools wheel pip
echo -e "${GREEN}[*] Done${RESET}";echo

# autoenv setup
echo -e "${YELLOW}[*] Setting up python virtual environment...${RESET}"
apt-get install -y python3-venv
python3 -m pip install --upgrade autoenv
if [ -z "$(cat ~/.bashrc | grep "source.*activate.sh")" ] && [ ! -z "$(which activate.sh)" ]; then
	echo "source `which activate.sh`" >> ~/.bashrc
fi
rm -rf env
python3 -m venv env
wget -P env/bin https://raw.githubusercontent.com/pypa/virtualenv/master/virtualenv_embedded/activate_this.py
chmod +x env/bin/activate_this.py
chmod +x env/bin/activate
source env/bin/activate
echo -e "source env/bin/activate >/dev/null 2>&1" >.env
echo -e "${GREEN}[*] Done${RESET}";echo

# pip installs
echo -e "${YELLOW}[*] Setting up python dependencies...${RESET}"
python3 get-pip.py
rm -f get-pip.py
python3 -m pip install --upgrade setuptools wheel pip
python3 -m pip install pycairo
python3 -m pip install -r requirements.txt
echo -e "${GREEN}[*] Done${RESET}";echo

# Initialize the database
echo -e "${YELLOW}[*] Initializing the database...${RESET}"
if [ "$continue_setup" = "y" ] || [ -z "$check_database" ]; then
	cd modules/flask/
	rm -rf migrations
	python3 manage.py db init
	initialized=0
	migrated=0
	while [ $initialized -eq 0 ]; do
		if [ $migrated -eq 0 ]; then
			echo;python3 manage.py db migrate
			ret_code=$?
			if [ $ret_code -ne 0 ]; then
				echo;echo -e "${RED}[!] Error initializing the database.${RESET}"
				echo -e "${YELLOW}[!] If you see ${RESET}'FATAL:  password authentication failed for user \"scraper\"'${YELLOW} above, you entered your password wrong.${RESET}"
				echo -e "${YELLOW}[!] Anything else is an unhandled error. Restarting database initialization...${RESET}";echo
				continue
			fi
			migrated=1
		fi
		echo;python3 manage.py db upgrade
		ret_code=$?
		if [ $ret_code -ne 0 ]; then
			echo;echo -e "${RED}[!] Error initializing the database.${RESET}"
			echo -e "${YELLOW}[!] If you see ${RESET}'FATAL:  password authentication failed for user \"scraper\"'${YELLOW} above, you entered your password wrong.${RESET}"
			echo -e "${YELLOW}[!] Anything else is an unhandled error. Restarting database initialization...${RESET}";echo
			continue
		fi
		initialized=1
	done
fi
echo -e "${GREEN}[*] Done${RESET}";echo

# Store the flask secret key
echo -e "${YELLOW}[*] Generating flask secret key in config.ini...${RESET}"
cd "$script_path/.."
secret_key=$(python3 -c "import os; print(os.urandom(24).hex())")
sed -i "8s/.*/secret_key=$secret_key/" config.ini
echo -e "${GREEN}[*] Done${RESET}";echo

apache_setup=""
while [ -z "$apache_setup" ]; do
	echo -e "${BOLD}${YELLOW}[?] Attempt deployment to Apache?${RESET}"
	read -p "(y/n): " apache_setup
	if [ "$apache_setup" = "y" ]; then
		echo -e "${YELLOW}[*] Attempting deployment to Apache...\n${RESET}"
		cd "$script_path/apache"
		pastebin_scraper_dir="$(cd "$script_path/.."; pwd -P)"
		# Setup ps.wsgi
		echo -e "${YELLOW}[*] Editing and copying setup/apache/ps.wsgi to /var/www/pastebin-scraper...${RESET}"
		mkdir -p /var/www/pastebin-scraper
		activate_this="'$pastebin_scraper_dir/env/bin/activate_this.py'"
		cp ps.wsgi ps.wsgi.tmp
		sed -i "8s@.*@sys.path.append('$pastebin_scraper_dir')@" ps.wsgi.tmp
		sed -i "12s@.*@activate_this = $activate_this@" ps.wsgi.tmp
		mv ps.wsgi.tmp /var/www/pastebin-scraper/ps.wsgi
		chown -R www-data:www-data /var/www/pastebin-scraper/
		echo -e "${GREEN}[*] Done${RESET}"
		# Setup pastebin-scraper.com.conf
		echo -e "${YELLOW}[*] Editing and copying setup/apache/pastebin-scraper.com.conf to /etc/apache2/sites-available...${RESET}"
		wsgi_daemon_process="WSGIDaemonProcess ps user=www-data group=www-data threads=5 home=/var/www/pastebin-scraper python-path=$pastebin_scraper_dir:$pastebin_scraper_dir/env/lib64/python3.6/site-packages:$pastebin_scraper_dir/env/lib/python3.6/site-packages"
		cp pastebin-scraper.com.conf pastebin-scraper.com.conf.tmp
		sed -i "7s@.*@$wsgi_daemon_process@" pastebin-scraper.com.conf.tmp
		mv pastebin-scraper.com.conf.tmp /etc/apache2/sites-available/pastebin-scraper.com.conf
		echo -e "${GREEN}[*] Done${RESET}"
		echo -e "${YELLOW}[*] Enabling site pastebin-scraper.com...${RESET}"
		a2ensite pastebin-scraper.com >/dev/null 2>&1
		systemctl reload apache2
		echo -e "${GREEN}[*] Done\n${RESET}"
		echo -e "${GREEN}[*] Completed deployment attempt. Site should be available at pastebin-scraper.com${RESET}"
		echo -e "${YELLOW}[*] Check /var/log/apache2/error.log for error info.${RESET}"
	elif [ "$apache_setup" = "n" ]; then
		break
	else
		apache_setup=""
	fi
done

echo -e "\n${GREEN}[*] Setup has completed.${RESET}"
echo -e "${YELLOW}[*] The python virtual environment must be activated before running ps.py${RESET}"
echo -e "${YELLOW}[*] Run the command below from the pastebin-scraper root directory to activate the virtual environment:${RESET}"
echo -e "\tsource env/bin/activate"
echo -e "${YELLOW}[*]${RESET} (env) ${YELLOW}will appear next to your command line when the virtual environment is active.${RESET}"
