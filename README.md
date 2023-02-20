This is basically a honeypot setup for `Linux`.

Here you can find a simple python script that use `stat` command to check if a file previously set has been accessed and notify you over an _Gmail_ account.

***
**OPTIONS**

  `--config FILE` Sets the specific config FILE. **Default:** ./setup.conf

  `--setup` Copy and replace honeypot files to specific folders

  `--auth` Start Google authentication process

  `--no-check` Run script without checking if any file has been accessed. Useful when running with `--setup`  

***
**CONFIG**

Default config file will look like this:

    [DEFAULT]
    server_name = your_server_name          # Custom name to identify your server in emails 
    gmail_sender = your_email@gmail.com     # The Gmail account that you use to send notifications
    receiver_email = notify_to@gmail.com    # Comma separated emails address to notify
    files_folder = /home/honeypot/files.d   # Folder where you store all your honeypot files in subfolders 
    
    [sample]                                # Honeypot subfolder name
    desired_path = /home/honeypot           # Path where you want to place your honeypots in this subfolder
    store_info = True                       # Flag used to store last accessed time or use birth date from file itself

** You can have multiple subfolders with multiple `[sections]` in your config file.

** Every `[section]` represent a subfolder that will be copied to the `desired_path` when you run the script with `--setup`

***
**GMAIL AUTHENTICATION**

**Gmail Requirements**

    pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

You must follow the steeps listed in [Enable the API](https://developers.google.com/gmail/api/quickstart/python#enable_the_api) and [Authorize credentials for a desktop application](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application) sections to get your `credentials.json` file.

You should put the `credentials.json` file in `./python_honeypot/gmail_credentials.` folder.

Once you have the `credentials.json` file you should give access to your _Gmail_ account using `--auth` param and use the provided _URL_ to authenticate your Google Account in a web browser.

This account will be used only as a sender mail for notifications.

***
**SET UP CRON**

You can set up a cron job for running the script avery some time and check if some file has been accessed.

Run `crontab -e` in a terminal to introduce tasks to be run by cron and add at the end of crontab file your cron job.

**Sample**

Cron to run the script every 4 hours.

    0 */4 * * * /usr/bin/python3 ~/python_honeypot/main.py --config ~/python_honeypot/setup.conf

