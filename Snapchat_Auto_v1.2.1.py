import sys
import PySimpleGUI as sg
from scripts import ParseSnapchat_iOS
from scripts import getCacheAndroid
from scripts.data import extract_zip
from scripts import parseSnapvideos_PREFETCH
import os
import logging
import datetime

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "loglevel;0"

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()
fileHandler = logging.FileHandler(f"SnapchatAuto_{datetime.datetime.today().strftime('%Y%m%d_%H%M%S')}.log")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


if getattr(sys, 'frozen', False):
    app_path = sys._MEIPASS
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

logger.info(app_path)


def main(args):

    logger.info("Snapchat Auto v1.2.1")
    
    layout = [
        [sg.Text("Select Settings")],
        [sg.Radio('IOS', 'OS', default=True), sg.Radio('Android', 'OS')],
        [sg.Text('Extraction zip')], [sg.In(key="zip"), sg.FileBrowse(file_types=(("All Files", "*"),), target="zip", initial_folder=".")],
        [sg.Text('Keychain (iOS Only)')], [sg.In(key="keychain"), sg.FileBrowse(file_types=(("Plist", [".plist", ".json"]),), target="keychain", initial_folder=".")],
        [sg.Button('Ok'), sg.Button('Cancel')]]

    window = sg.Window('Snapchat Auto', layout)
    event, values = window.read()
    window.close()

    if event == "Cancel":
        sys.exit()
    if values[0]:
        logger.info("You chose iOS")
        extracted_files_dir = extract_zip.extract(values['zip'], 'ios')
        if not os.path.exists("SnapFixedVideos"):
            parseSnapvideos_PREFETCH.main(extracted_files_dir[0])
        else:
            logger.info("Found SnapFixedVideos folder, skipping that step")
        ParseSnapchat_iOS.main(extracted_files_dir[0], extracted_files_dir[1], values["keychain"])
    elif values[1]:
        logger.info("You chose Android")
        extracted_files_dir = extract_zip.extract(values['zip'], 'android')
        getCacheAndroid.main(extracted_files_dir)

if __name__ == '__main__':
    main(sys.argv[1:])