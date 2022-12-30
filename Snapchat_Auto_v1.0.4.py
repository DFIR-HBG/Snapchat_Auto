import sys
import PySimpleGUI as sg
from scripts import ParseSnapchat_iOS
from scripts import getCacheAndroid
from scripts.data import extract_zip
from scripts import parseSnapvideos_PREFETCH
import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "loglevel;0"

if getattr(sys, 'frozen', False):
    app_path = sys._MEIPASS
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

print(app_path)


def main(args):


    layout = [
        [sg.Text("Select Settings")],
        [sg.Radio('IOS', 'OS', default=True), sg.Radio('Android', 'OS')],
        [sg.Text('Extraction zip')], [sg.In(key="zip"), sg.FileBrowse(file_types=(("All Files", "*"),), target="zip", initial_folder=".")],
        [sg.Text('Keychain (iOS Only)')], [sg.In(key="keychain"), sg.FileBrowse(file_types=(("Plist", ".plist"),), target="keychain", initial_folder=".")],
        [sg.Button('Ok'), sg.Button('Cancel')]]

    window = sg.Window('Snapchat Auto', layout)
    event, values = window.read()
    window.close()

    if event == "Cancel":
        sys.exit()
    if values[0]:
        print("You chose iOS")
        extracted_files_dir = extract_zip.extract(values['zip'], 'ios')
        parseSnapvideos_PREFETCH.main(extracted_files_dir[0])
        ParseSnapchat_iOS.main(extracted_files_dir[0], extracted_files_dir[1], values["keychain"])
    elif values[1]:
        print("You chose Android")
        #extracted_files_dir = "com.snapchat.android"
        extracted_files_dir = extract_zip.extract(values['zip'], 'android')
        getCacheAndroid.main(extracted_files_dir)

if __name__ == '__main__':
    main(sys.argv[1:])