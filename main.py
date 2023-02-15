# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys
import subprocess
import configparser
import re
import gmail_helper


# Setup some constants
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
FILES_PATH = SCRIPT_PATH + "/files.d/"
CONFIG_FILE = SCRIPT_PATH + "/setup.conf"

# Setup some variables
config = configparser.ConfigParser()
sections = []


def get_section_path(section, include_section=False):
    path = config[section]['desired_path']

    if not path.endswith("/"):
        path += "/"

    if not include_section:
        return path

    return path + section


def setup_files():
    for section in sections:
        path_from = FILES_PATH + section
        path_to = get_section_path(section)

        # Remove previous files/folders
        # Create directory structure
        # Copy files again
        command = f'rm -rf {path_to}*; mkdir -p {path_to}{section}; cp -r {path_from} {path_to}'
        subprocess.run(command, capture_output=False, shell=True)


def check_files():
    """
    This function checks every file and return true if some file has been accessed
    """
    for section in sections:
        path = get_section_path(section, True)
        output = subprocess.Popen(['find', path], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").splitlines()
        for file in output:
            if os.path.isdir(file):
                continue
            if check_file_accessed(file):
                return True


def check_file_accessed(path):
    output = subprocess.Popen(['stat', path], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").splitlines()
    access = re.sub(".*: ", "", output[4])
    birth = re.sub(".*: ", "", output[7])
    return access != birth


def send_alert():
    # subprocess.Popen(['stat', path], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").splitlines()
    print("some files have been accessed")
    send_email()


def send_email(test_message=False):
    sender = config['DEFAULT']['gmail_sender']
    receiver = config['DEFAULT']['receiver_email']
    subject = """Intruder alert"""
    message = """
        You have been hacked!!!!<br><br>    
        Some of your honeypot files have been accessed recently.
    """

    if test_message:
        subject = """Testing Python message"""
        message = """This message is sent from Python."""

    gmail_helper.send_message(sender, receiver, subject, message)


def read_config():
    config_path = CONFIG_FILE

    if sys.argv.__contains__("--config"):
        config_index = sys.argv.index('--config')+1
        config_path = sys.argv[config_index]

    if os.path.isdir(config_path) or not config_path.endswith(".conf"):
        config_path = CONFIG_FILE

    config.read(config_path)
    global sections
    sections = config.sections()


def run():
    if check_files():
        send_alert()

    # Setup files again after check old files
    if sys.argv.__contains__("--setup"):
        setup_files()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    read_config()

    # Authenticate Gmail
    if sys.argv.__contains__("--auth"):
        send_email(True)
    else:
        run()

