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


def get_files_folder():
    files_folder = config['DEFAULT']['files_folder']
    if not files_folder.endswith("/"):
        files_folder += "/"

    return files_folder


def setup_files():
    files_folder = get_files_folder()
    for section in sections:
        path_from = files_folder + section
        path_to = get_section_path(section)

        # Create directory structure
        # Copy/replace files again
        command = f'mkdir -p {path_to}{section}; cp -rf --remove-destination {path_from} {path_to}'
        subprocess.run(command, capture_output=False, shell=True)


def check_files():
    """
    This function checks every file and return true if some file has been accessed
    """
    for section in sections:
        # Get the original files lists
        section_folder_path = get_files_folder() + section
        section_files_path = subprocess.Popen(
            ['find', section_folder_path], stdout=subprocess.PIPE
        ).communicate()[0].decode("utf-8").replace(section_folder_path, "").splitlines()

        path = get_section_path(section, True)
        output = subprocess.Popen(['find', path], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").splitlines()

        accessed_files = []
        for file in output:
            # Ignore any file that isnt in original files path
            if file.replace(path, "") not in section_files_path:
                continue
            # Ignore directories
            if os.path.isdir(file):
                continue
            # Check if file has been accessed
            accessed_time = check_file_accessed(file)
            if accessed_time:
                accessed_files.append((file, accessed_time))

        return accessed_files


def check_file_accessed(path):
    output = subprocess.Popen(['stat', path], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").splitlines()
    access = re.sub(".*: ", "", output[4])
    birth = re.sub(".*: ", "", output[7])
    return access if access != birth else ""


def send_alert(accessed_files=None):
    print("some files have been accessed")
    send_email(accessed_files)


def send_email(accessed_files=None, test_message=False):
    sender = config['DEFAULT']['gmail_sender']
    receiver = config['DEFAULT']['receiver_email']

    if test_message:
        subject = """Testing Python message"""
        message = """This message is sent from Python."""
    else:
        subject = """Intruder alert"""
        message = get_body_message(accessed_files)

    gmail_helper.send_message(sender, receiver, subject, message)


def get_body_message(accessed_files=None):
    if accessed_files is None:
        return """
            Ops!!! Something went wrong, but keep alert ;)
        """

    body = """
        <h2>You have been hacked!!!</h2>
        <br>The next honeypots files has been accessed:<br><br>
        <table style="font-family: arial, sans-serif; border-collapse: collapse;">
          <tr>
            <th style="border: 1px solid #dddddd; text-align: left; padding: 8px;" width="40%">Timestamp</th>
            <th style="border: 1px solid #dddddd; text-align: left; padding: 8px;" width="60%">File Path</th>
          </tr>
    """

    styled_row = True
    for (path, accessed) in accessed_files:
        if styled_row:
            body += """<tr style="background-color: #dddddd;">"""
        else:
            body += "<tr>"

        body += f"""
            <td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{accessed}</td>
            <td style="border: 1px solid #dddddd; text-align: left; padding: 8px;">{path}</td></tr>
        """
        styled_row = not styled_row

    body += "</table>"

    return body


def read_config():
    config_path = CONFIG_FILE

    if sys.argv.__contains__("--config"):
        config_index = sys.argv.index('--config')+1
        config_path = sys.argv[config_index]

    if not (os.path.isfile(config_path) and config_path.endswith(".conf")):
        config_path = CONFIG_FILE

    config.read(config_path)
    global sections
    sections = config.sections()


def run():
    accessed_files = check_files()
    if len(accessed_files) != 0:
        send_alert(accessed_files)

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

