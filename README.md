# pastebin-scraper

### Scrapes pastebin.com API for pastes containing supplied keywords. Utilizes postgresql and flask on the back end to store and present data on a per project basis. Tested with successful deployment to Apache.

#### *Info on Pastebin API scraping guidelines (See: https://pastebin.com/doc_scraping_api)*

**Request limits**:
Your whitelisted IP should not run into any issues as long as you don't abuse our service. We recommend not making more than 1 request per second, as there really is no need to do so. Going over 1 request per second won't get you blocked, but if we see excessive unnecessary scraping, we might take action.

**Recommended Scraping Logic**:
If you are trying to read ALL new public pastes, we recommend that you list 1x per minute the 100 most recent pastes. Store all those ID's/Keys locally somewhere, then fetch all those pastes and process the information however you like. 

We urge you not to re-fetch pastes unnecessarily, as the data doesn't change quickly. Having some kind of local database system, which prevents unnecessary re-fetches is highly recommended! It lowers the load on both your own and our servers.

## Usage

*Make sure your IP is whitelisted at https://pastebin.com/doc_scraping_api*

### 1. Run the setup script

- `./setup/setup.sh`

### 2. Run ps.py

- `python3 ps.py`

### 3. Settings

By default ps.py runs on localhost port 5005 and postgresql is configured to use port 5432 on localhost. These can be changed in config.ini. The flask secret key can also be changed here. By default the setup script gives it the value of `python3 -c "import os; print(os.urandom(24).hex())"`

The `history_limit` option of the [scraper] section in config.ini will control how many paste keys are stored in the history table of the database. This is done to prevent an infinite amount of paste key storage, which reduces database size.

## Deploying to Apache

Apache dependencies are installed through the setup script, and deployment has been tested using the following steps. If set up works properly and you have DNS set up correctly, you should be able to hit the scraper at pastebin-scraper.com.

**NOTE**: Deployment can also be attempted through the setup script.

### 1. Edit [flask] section of config.ini
*Location*: pastebin-scraper/config.ini

- Change the line `env=dev` to `env=prod`

- Enter your database password supplied during setup into the `password` option

**NOTE**: Password must be hardcoded because the getpass module used to read password input in a development environment will not read input when loaded through Apache. Looking for ways around this to avoid storing plaintext passwords.

### 2. Edit and copy ps.wsgi

*Location*: pastebin-scraper/setup/apache/ps.wsgi

The lines that have to be changed are noted in the file. After making necessary changes run the following command:

```
mkdir -p /var/www/pastebin-scraper
cp pastebin-scraper/setup/apache/ps.wsgi /var/www/pastebin-scraper
chown -R www-data:www-data /var/www/pastebin-scraper
```

### 3. Edit and copy pastebin-scraper.com.conf

*Location*: pastebin-scraper/setup/apache/pastebin-scraper.com.conf

The lines that have to be changed are noted in the file. After making necessary changes run the following commands:

```
cp pastebin-scraper/setup/apache/pastebin-scraper.com.conf /etc/apache2/sites-available
a2ensite pastebin-scraper.com
```

### 4. Reload Apache

- `systemctl reload apache2`

### 5. Run ps.py

When in `prod` mode only the scraper will run, without the flask app. Recommended to run in background or screen session. 

- `python3 ps.py`
