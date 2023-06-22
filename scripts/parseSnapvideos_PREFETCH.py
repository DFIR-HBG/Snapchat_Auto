import glob
import datetime
import sys
import os
import re
from shutil import copy2
import logging

logger = logging.getLogger(__name__)

def mergeFiles(files, directory):
    with open("./SnapFixedVideos/"+files[0].split("_")[0]+".mp4", "ab") as full_file:
        for f in files:
            #logger.info(directory +"/" + f)
            with open(directory + "/" + f, "rb") as part_file:
                full_file.write(part_file.read())

def getCache(folder):
    foundDir = glob.glob(folder+'/Documents/com.snap.file_manager_3_SCContent_*')
    for dir in foundDir:
        fileList = list(filter(pattern.match, os.listdir(dir)))
        for file in fileList:
            if file.endswith("PREFETCH"):
                os.rename(dir + '/' + file, dir + '/' + file.split('_')[0] + '_0-1')
                #logger.info("Renaming file")
        fileList = list(filter(pattern.match, os.listdir(dir)))
        fileList.sort()
        prev = []
        for j in range(len(fileList)):
            header = fileList[j]
            pat = re.compile(header.split("_")[0])
            file = list(filter(pat.match,fileList))
            try:
                file.sort(key=lambda x: int(x.split("_")[1].split("-")[0]))
            except Exception as Error:
                #logger.info(file)
                #logger.info(Error)
                os.system("pause")
            if file != prev:
                #logger.info(file)
                if len(file) > 1:
                    mergeFiles(file, dir)
                else:
                    copy2(dir + "/" + file[0], "./SnapFixedVideos/"+file[0].split("_")[0]+".mp4")
            prev = file
def main(Application):
    global pattern
    
    logger.info("Merging split media files")
    uuid_pattern = re.compile("[A-F0-9-]{36}")
    for root, dirs, files in os.walk(Application):
        if uuid_pattern.match(dirs[0]):
            base_folder_data = dirs[0]
            break
    snapchatFolder = Application + "/" + base_folder_data
    pattern = re.compile("[a-f0-9]{32}_[\dP]")
    os.makedirs("./SnapFixedVideos",exist_ok=True)
    getCache(snapchatFolder)
    logger.info("Done merging media files")




if __name__ == "__main__":
    main()
