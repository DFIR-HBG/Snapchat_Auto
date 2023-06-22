import os
import base64
import plistlib
from sqlite3.dbapi2 import DatabaseError
from Crypto.Cipher import AES
import sys
from binascii import unhexlify
from binascii import hexlify
from datetime import datetime
import calendar
import pandas as pd
import requests
import sqlite3
from scripts.data import ccl_bplist
from scripts.data import keychain as convert_keychain
import filetype
import subprocess
from PIL import Image
import shutil
import re
import ntpath
import numpy as np
os.environ["OPENCV_LOG_LEVEL"] = "OFF"
os.environ["OPENCV_FFMPEG_DEBUG"] = "0"
os.environ["OPENCV_VIDEOIO_DEBUG"] = "0"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "0"
os.environ["OPENCV_VIDEOCAPTURE_DEBUG"] = "0"
os.environ["OPENCV_OPENCL_RAISE_ERROR"] = "0"
import cv2
#from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT
import logging
import json
from platform import system

logger = logging.getLogger(__name__)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "loglevel;0"

header_size = 0x10
page_size = 0x400
salt_sz = 0x10
hmac_sz = 0x20
reserved_sz = salt_sz + hmac_sz


def decrypt_sqlcipher(db, egocipher):
    key = egocipher

    print(f"Dekrypterar {db}")#med nyckel {key}") 
    if platform == "Windows":
        if using_exe:
            try:
                subprocess.call([f"{exe_path}/scripts/data/sqlcipher3.exe", db,'pragma key="x\'' + key + '\'"', "PRAGMA cipher_compatibility = 3", ".output recovery.sql", ".dump"])
                print("Decrypted")
            except Exception as E:
                logger.error(E)
                sys.exit()
        else:
            try:
                subprocess.call([f"{exe_path}/data/sqlcipher3.exe", db,'pragma key="x\'' + key + '\'"', "PRAGMA cipher_compatibility = 3", ".output recovery.sql", ".dump"])
                print("Decrypted")
            except Exception as E:
                logger.error(E)
                sys.exit()
        recoveredFile = decryptedName
        if os.path.exists(recoveredFile):
            os.remove(recoveredFile)
        recoveredConn = None
        try:
            recoveredConn = sqlite3.connect(recoveredFile)
        except DatabaseError as e:
            logger.error(e)
        with open("recovery.sql", "r", encoding="utf-8") as recoverySql:
            recoveredConn.executescript(recoverySql.read())
            recoveredConn.close()
        #os.remove("recovery.sql")
        logger.info("Database Recovered!")

def decryptGalleryDB(db, egocipher, persisted):
    global header, max_page
    
    if os.path.exists(decryptedName):
        logger.info(f"Decrypted database {decryptedName} already exists, assuming database is already decrypted")
        return
    key = egocipher
    if persisted != "":
        with open("temp.plist", "wb") as f:
            f.write(persisted)
        with open("temp.plist", "rb") as f:
            MEOplist = ccl_bplist.load(f)
        os.remove("temp.plist")

        obj = ccl_bplist.deserialise_NsKeyedArchiver(MEOplist)
        MEOkey = obj["masterKey"]
        MEOiv = obj["initializationVector"]
    # logger.info(MEOkey)
    # logger.info(MEOiv)

    enc_db = open(db, "rb")
    enc_db_size = os.path.getsize(db)

    header = enc_db.read(header_size)
    max_page = int(enc_db_size / page_size)
    with open(decryptedName, 'wb') as decrypted:
        decrypted.write(b'SQLite format 3\x00')

        for page in range(0, max_page):
            decrypted.write(decrypt_page(page, enc_db, key))
            decrypted.write(b'\x00' * reserved_sz)
    logger.info(f"Database decrypted: {decryptedName}")


def decrypt_page(page_offset, enc_db, key):
    if page_offset == 0:
        page_data = enc_db.read(page_size - header_size)
    else:
        page_data = enc_db.read(page_size)

    iv = page_data[-reserved_sz:-reserved_sz + salt_sz]
    decryption_suite = AES.new(key[:32], AES.MODE_CBC, iv)
    plain_text = decryption_suite.decrypt(page_data[:-reserved_sz])

    return plain_text


def getMemoryKey(db):
    conn = sqlite3.connect(db)
    query = """
	select
	snap_key_iv.snap_id as ID,
	snap_key_iv.KEY as KEY,
	snap_key_iv.IV as IV,
	snap_key_iv.ENCRYPTED as ENCRYPTED,
	snap_location_table.snap_id,
	snap_location_table.latitude as latitude,
	snap_location_table.longitude as longitude
	from snap_key_iv
	left join snap_location_table on ID = snap_location_table.snap_id"""

    df = pd.read_sql_query(query, conn)

    return df


def getSCDBInfo(db):
    conn = sqlite3.connect(db)
    query = """
	select
	ZSNAPID as ID,
	ZMEDIADOWNLOADURL,
	ZOVERLAYDOWNLOADURL
	from ZGALLERYSNAP
	"""
    # WHERE ZMEDIADOWNLOADURL IS NOT NULL
    df = pd.read_sql_query(query, conn)

    return df


def getFullSCDBInfo(db):
    conn = sqlite3.connect(db)
    query = """
	select
	ZSNAPID as ID,
	*
	from ZGALLERYSNAP
	"""
    # WHERE ZMEDIADOWNLOADURL IS NOT NULL
    df = pd.read_sql_query(query, conn)

    return df


def fixMEOkeys(persistedKey, df_merge):
    with open("temp.plist", "wb") as f:
        f.write(persistedKey)
    with open("temp.plist", "rb") as f:
        MEOplist = ccl_bplist.load(f)
    os.remove("temp.plist")

    obj = ccl_bplist.deserialise_NsKeyedArchiver(MEOplist)
    MEOkey = obj["masterKey"]
    MEOiv = obj["initializationVector"]

    for index, row in df_merge.iterrows():
        if row["ENCRYPTED"] == 1:
            enc_key = row["KEY"]
            enc_iv = row["IV"]
            aes = AES.new(MEOkey, AES.MODE_CBC, MEOiv)
            dec_key = hexlify(aes.decrypt(enc_key))[:64]
            aes = AES.new(MEOkey, AES.MODE_CBC, MEOiv)
            dec_iv = hexlify(aes.decrypt(enc_iv))[:32]
            df_merge.loc[index, "KEY"] = unhexlify(dec_key)
            df_merge.loc[index, "IV"] = unhexlify(dec_iv)

    return df_merge

def silent_error_handler(status, func_name, err_msg, file_name, line, userdata):
    pass

def decryptMemoriesLocal(egocipherKey, persistedKey, df_merge, df_cache):
    logger.info("Preparing for decryption of cached Memories")
    if not isinstance(egocipherKey, bytes):
        try:
            egocipherKey = unhexlify(egocipherKey)
            persistedKey = unhexlify(persistedKey)
        except:
            try:
                egocipherKey = base64.b64decode(egocipherKey)
                persistedKey = base64.b64decode(persistedKey)
            except Exception as E:
                logger.info("Could not decode keys", E)

    if persistedKey != "" and persistedKey != b'':
        df_merge = fixMEOkeys(persistedKey, df_merge)
    
    regex = re.compile("[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}")
    
    df_merge["filename"] = ""
    df_merge["overlayFilename"] = ""
    logger.info("Copying merged media files to cache folder")
    for file in os.listdir("SnapFixedVideos"):
        source = f"SnapFixedVideos/{file}"
        destination = f"{SCContentFolder_path}/{file.split('.')[0]}"
        if os.path.isfile(source) and not os.path.isfile(destination):
            shutil.copy(source, destination)
        else:
            continue
            #logger.info(f"Could not copy merged file {source}")
    
    logger.info("Decrypting cached Memories")
    uuid_counter = 0
    temp_dict = {'ID':[], 'CACHE_KEY':[]}
    for cache_index, cache_row in df_cache.iterrows():
        try:
            UUID = regex.findall(cache_row["EXTERNAL_KEY"])
            if UUID != []:
                UUID = str(UUID[0])
                uuid_counter += 1
                temp_dict['ID'].append(UUID)
                temp_dict['CACHE_KEY'].append(cache_row["CACHE_KEY"])
            else:
                continue
        except Exception as error:
            logger.error(f"Error finding memory ID {cache_row['EXTERNAL_KEY']} {error}")

    memory_df = pd.DataFrame(data=temp_dict)
    df_merge = pd.merge(df_merge, memory_df, on=["ID"], how = 'outer')
    df_merge = df_merge.dropna(axis=0, subset=["ZSNAPID"])
    #con = sqlite3.connect("test.db")
    #df_merge.to_sql("df_merge", con)
    
    os.environ["OPENCV_LOG_LEVEL"] = "OFF"
    os.environ["OPENCV_FFMPEG_DEBUG"] = "0"
    os.environ["OPENCV_VIDEOIO_DEBUG"] = "0"
    os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "0"
    os.environ["OPENCV_VIDEOCAPTURE_DEBUG"] = "0"
    os.environ["OPENCV_OPENCL_RAISE_ERROR"] = "0"
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "loglevel;panic"
    for merge_index, merge_row in df_merge.iterrows():
        decryptedfile = False
        try:
            file = f"{SCContentFolder_path}{merge_row['CACHE_KEY']}"
            filename = merge_row['CACHE_KEY']
            if filetype.guess(file) == None or filetype.guess(file).extension in ['ps']: #Encrypted file or some random filetype
                aes = AES.new(merge_row["KEY"], AES.MODE_CBC, merge_row["IV"])
                with open(file, "rb") as f:
                    enc_data = f.read()
                dec_data = aes.decrypt(enc_data)
                if filetype.guess(dec_data) == None: #Is the original decrypted data not valid?
                    if filetype.guess(dec_data[8:]) == None: #Is the decrypted data without the first 8 bytes not valid?
                        logger.error(f"Error decrypting {file}")
                        continue
                    else:
                        dec_data = dec_data[8:]
                        
                fileTypeMime = filetype.guess(dec_data)
                if fileTypeMime != None:
                    with open(f"{outputDir}/DecryptedMemories/{merge_row['CACHE_KEY']}.{fileTypeMime.extension}", "wb") as f:
                        f.write(dec_data)
                    decryptedfile = True
                else:
                    logger.error(f"could not find file extension of {file}")
                    shutil.copy(file, f"{outputDir}/DecryptedMemories/{filename}.{unknownFile}")
                    df_merge.loc[merge_index, "filename"] = f"{filename}.unknownFile"
                    continue
                    
            else: #Not encrypted file
                fileTypeMime = filetype.guess(file)
                if fileTypeMime != None:
                    shutil.copy(file, f"{outputDir}/DecryptedMemories/{filename}.{fileTypeMime.extension}")
                else:
                    logger.error(f"could not find file extension of {file}")
                    shutil.copy(file, f"{outputDir}/DecryptedMemories/{filename}.{unknownFile}")
                    df_merge.loc[merge_index, "filename"] = f"{filename}.unknownFile"
                    continue
                    
            if fileTypeMime.extension != "webp" and fileTypeMime.extension != "png":
                if decryptedfile == True:
                    df_merge.loc[merge_index, "filename"] = f"{filename}.{fileTypeMime.extension}"
                else:
                    if df_merge.loc[(df_merge["ID"] == merge_row['ID']) & (df_merge["filename"] != "")].empty:
                        df_merge.loc[merge_index, "filename"] = f"{filename}.{fileTypeMime.extension}"
            else:
                if decryptedfile == True:
                    df_merge.loc[merge_index, "overlayFilename"] = f"{filename}.{fileTypeMime.extension}"
                else:
                    if df_merge.loc[(df_merge["ID"] == merge_row['ID']) & (df_merge["overlayFilename"] != "")].empty:
                        df_merge.loc[merge_index, "overlayFilename"] = f"{filename}.{fileTypeMime.extension}"
            resultfile = f"{outputDir}/DecryptedMemories/{filename}.{fileTypeMime.extension}"
            
            if fileTypeMime.extension == "mp4": #Check if video has any frames, removes it if its 0
                try:
                    cv2video = cv2.VideoCapture(resultfile)
                    framecount = cv2video.get(cv2.CAP_PROP_FRAME_COUNT)
                    if int(framecount) == 0:
                        df_merge.loc[merge_index, "filename"] = "FrameCountError"
                        os.remove(resultfile)
                except Exception as Error:
                    logger.error(f"Error checking if {filename} is playable, {Error}")
            
            # if fileTypeMime is not None:
                # with open(outputDir + "/DecryptedMemories/" + filename + "." + fileTypeMime.extension, "wb") as f:
                    # f.write(dec_data)
                # with open(file, "wb") as f:
                    # f.write(dec_data)
                # if fileTypeMime.extension != "webp":
                    # df_merge.loc[merge_index, "filename"] = filename + "." + fileTypeMime.extension
                # else:
                    # df_merge.loc[merge_index, "overlayFilename"] = filename + "." + fileTypeMime.extension
            # else:
                # try:
                    # fileTypeMime = filetype.guess(dec_data[8:])
                    # if fileTypeMime is not None:
                        # with open(outputDir + "/DecryptedMemories/" + filename + "." + fileTypeMime.extension, "wb") as f:
                            # f.write(dec_data[8:])
                        # with open(file, "wb") as f:
                            # f.write(dec_data)
                        # if fileTypeMime.extension != "webp":
                            # df_merge.loc[merge_index, "filename"] = filename + "." + fileTypeMime.extension
                        # else:
                            # df_merge.loc[merge_index, "overlayFilename"] = filename + "." + fileTypeMime.extension
                # except:
                    # logger.info(f"could not find file extension of {file}")
                    # with open(outputDir + "/DecryptedMemories/" + filename + "." + "nokind", "wb") as f:
                        # f.write(dec_data)
                        # df_merge.loc[merge_index, "filename"] = filename + "." + "nokind"
                        
        except FileNotFoundError as fnfe:
            continue
        except Exception as error:
            logger.error(f"Error decrypting snap ID {merge_row['ID']} {error}")
        
        # for filename in os.listdir(SCContentFolder_path):
            # try:
                # if cache_row["CACHE_KEY"] in filename:
                    # file = SCContentFolder_path + filename
                    # kind_temp = filetype.guess(file)
                    # if kind_temp == None:
                        # UUID = regex.findall(cache_row["EXTERNAL_KEY"])
                        # if UUID != []:
                            # UUID = str(UUID[0])
                            # for merge_index, merge_row in df_merge.iterrows():
                                # if str(merge_row["ID"]) == UUID:
                                    # try:
                                        # aes = AES.new(merge_row["KEY"], AES.MODE_CBC, merge_row["IV"])
                                        # filename = cache_row["CACHE_KEY"]
                                        # with open(file, "rb") as f:
                                            # enc_data = f.read()
                                        # dec_data = aes.decrypt(enc_data)

                                        # fileTypeMime = filetype.guess(dec_data)
                                        # if fileTypeMime is not None:
                                            # with open(outputDir + "/DecryptedMemories/" + filename + "." + fileTypeMime.extension, "wb") as f:
                                                # f.write(dec_data)
                                            # with open(file, "wb") as f:
                                                # f.write(dec_data)
                                            # if fileTypeMime.extension != "webp":
                                                # df_merge.loc[merge_index, "filename"] = filename + "." + fileTypeMime.extension
                                            # else:
                                                # df_merge.loc[merge_index, "overlayFilename"] = filename + "." + fileTypeMime.extension
                                        # else:
                                            # try:
                                                # fileTypeMime = filetype.guess(dec_data[8:])
                                                # if fileTypeMime is not None:
                                                    # with open(outputDir + "/DecryptedMemories/" + filename + "." + fileTypeMime.extension, "wb") as f:
                                                        # f.write(dec_data[8:])
                                                    # with open(file, "wb") as f:
                                                        # f.write(dec_data)
                                                    # if fileTypeMime.extension != "webp":
                                                        # df_merge.loc[merge_index, "filename"] = filename + "." + fileTypeMime.extension
                                                    # else:
                                                        # df_merge.loc[merge_index, "overlayFilename"] = filename + "." + fileTypeMime.extension
                                            # except:
                                                # logger.info(f"could not find file extension of {file}")
                                                # with open(outputDir + "/DecryptedMemories/" + filename + "." + "nokind", "wb") as f:
                                                    # f.write(dec_data)
                                                    # df_merge.loc[merge_index, "filename"] = filename + "." + "nokind"
                                                    
                                    # except FileNotFoundError as fnfe:
                                        # continue
                                    # except Exception as error:
                                        # logger.info(f"Error decryption snap ID {merge_row['ID']} {error}")
            # except Exception as error:
                # logger.info(f"Error decryption snap ID {merge_row['ID']} {error}")
    
    logger.info("Done decrypting Memories")
    return df_merge


def timestampsconv(cocoaCore):
    if pd.isna(cocoaCore) or cocoaCore == "":
        return ""
    unix_timestamp = cocoaCore + 978307200
    finaltime = datetime.utcfromtimestamp(unix_timestamp)
    return (finaltime)


def recoverWithSqlite():
    if os.path.exists("gallery_decrypted.sqlite_r"):
        return True
    logger.info("Recovering Database")
    subprocess.call(["sqlite3", decryptedName, ".output recovery.sql", ".dump"])
    recoveredFile = decryptedName + "_r"
    if os.path.exists(recoveredFile):
        os.remove(recoveredFile)
    recoveredConn = None
    try:
        recoveredConn = sqlite3.connect(recoveredFile)
    except DatabaseError as e:
        logger.error(e)
    with open("recovery.sql", "r", encoding='utf-8') as recoverySql:
        recoveredConn.executescript(recoverySql.read())
        recoveredConn.close()
    os.remove("recovery.sql")
    logger.info("Database Recovered!")
    if checkDatabase(recoveredFile):
        logger.info("checkdatabase after decryption == True")
        return True
    else:
        logger.info("checkdatabase after decryption == False")
        return False


def recoverWithTool():
    logger.info(
        "OPEN UP THE GALLERY_DECRYPTED.DB IN FORENSIC SQLITE BROWSER - Make sure recovered database is named  GALLERY_DECRYPTED.DB_r")
    os.system("pause")


def isSqliteInstalled() -> bool:
    try:
        subprocess.call(["sqlite3", "-version"], stdout=subprocess.DEVNULL)
    except FileNotFoundError as e:
        logger.warning("SQLite3 not installed")
        return False
    return True


def checkDatabase(db) -> bool:
    logger.info("Checkdatabase " + db)
    try:
        conn = sqlite3.connect(db)
        # query = """
		# SELECT name FROM sqlite_schema
		# WHERE type='table'
		# ORDER BY name"""
        query = """
        SELECT count(*) FROM sqlite_master
        """

        df = conn.execute(query)
    except sqlite3.DatabaseError as e:
        return False
    return True


def recoverDatabase():
    databaseValid = checkDatabase(decryptedName)
    logger.info(f"checkdatabase == {databaseValid}")
    if databaseValid:
        return
    else:
        if isSqliteInstalled():
            sucess = recoverWithSqlite()
            return sucess
        else:
            recoverWithTool()


def createFullSnapImages(df_merge):
    pattern = '_overlay'
    filePath = f"{outputDir}/DecryptedMemories/"
    os.makedirs(f"{outputDir}/DecryptedMemories/FullSnap", exist_ok=True)
    for index, row in df_merge.iterrows():
        try:
            filename = row['filename']
            if filename != "":
                file = filePath + filename
                # need to detect videos
                fileTypeMime = filetype.guess(file).mime
                if fileTypeMime != "video/mp4" and fileTypeMime != "video/quicktime":
                    background = Image.open(file)
                    if row['overlayFilename'] != "":
                        foreground = Image.open(filePath + row['overlayFilename'])
                        background.paste(foreground, (0, 0), foreground)
                    background.save(filePath + 'FullSnap/' + filename)
        except FileNotFoundError:
            pass
        except Exception as error:
            logger.error(f"Error creating FullSnapImage of snap ID: {row['ID']} | Filename: {row['filename']} | Error: {error}")


def generateReport(df_merge):
    logger.info("Generating report file")
    if getattr(sys, 'frozen', False):
        exe_path = sys._MEIPASS
        try:
            shutil.copytree(f"{exe_path}/css", f"{outputDir}/css")
        except:
            logger.error("Could not copy the CSS folder, result might look a bit worse")
    else:
        exe_path = os.path.dirname(os.path.abspath(__file__))
        try:
            shutil.copytree(f"{exe_path}/data/css", f"{outputDir}/css")
        except:
            logger.error("Could not copy the CSS folder, result might look a bit worse")

    filePath = f"./DecryptedMemories/"
    createFullSnapImages(df_merge)
    df_report = pd.DataFrame(columns=['ID', 'Image', 'Overlay'])
    for index, row in df_merge.iterrows():
        if row["ENCRYPTED"] == 1:
            memoryType = "My Eyes Only"
        else:
            memoryType = "Memory"
        id = row['ZSNAPID']
        format = int(row['ZMEDIATYPE'])
        columns = ['ID', 'Memory Type', 'Image', 'Overlay', 'Create Time (UTC)', 'Capture Time (UTC)', 'Duration', 'Camera', 'latitude', 'longitude']
        createTime = timestampsconv(row['ZCREATETIMEUTC'])
        captureTime = timestampsconv(row['ZCAPTURETIMEUTC'])
        duration = row['ZDURATION']
        camera = "Front" if row['ZCAMERAFRONTFACING'] == 1 else "Back"
        if row['overlayFilename'] != "":
            if format == 0:
                rowData = [id,
                           memoryType,
                           makeImg(filePath + "FullSnap/" + row['filename']),
                           makeImg(filePath + row['overlayFilename']),
                           createTime,
                           captureTime,
                           duration,
                           camera,
                           row['latitude'],
                           row['longitude']
                           ]
            else:
                rowData = [id,
                           memoryType,
                           makeVideo(filePath + row['filename']),
                           makeImg(filePath + row['overlayFilename']),
                           createTime,
                           captureTime,
                           duration,
                           camera,
                           row['latitude'],
                           row['longitude']
                           ]
        else:
            if format == 0:
                rowData = [id,
                           memoryType,
                           makeImg(filePath + "FullSnap/" +
                                   row['filename']),
                           "",
                           createTime,
                           captureTime,
                           duration,
                           camera,
                           row['latitude'],
                           row['longitude']
                           ]
            else:
                rowData = [id,
                           memoryType,
                           makeVideo(filePath + row['filename']),
                           "",
                           createTime,
                           captureTime,
                           duration,
                           camera,
                           row['latitude'],
                           row['longitude']
                           ]
        df_row = pd.DataFrame([rowData], columns=columns)
        df_report = pd.concat([df_report, df_row])
        df_report.sort_values(by=["Create Time (UTC)"], ascending=True, inplace=True)
        #logger.info(f'Records Added to Report: {len(df_report)}')

    template = """
    <body>%s
    </body>
    """

    html = """
    <link href="./css/bootstrap.min.css" rel="stylesheet">
    <style>
    th {
        background: #2d2d71;
        color: white;
        text-align: left;
    }
    </style>
        """
    html = html + template % df_report.to_html(classes=["table table-bordered table-striped table-hover table-xl "
                                                        "table-responsive text-wrap"], escape=False, index=False)
    html = html.replace('<a href="./DecryptedMemories/FullSnap/"><img src="./DecryptedMemories/FullSnap/" width="150"><br>Open </a>', "Could not be found or decrypted, "
                                                                             "usually because the Memory/MEO was " 
                                                                             "not locally stored")
    html = html.replace('<video width="320" height="240" controls> <source src="./DecryptedMemories/FrameCountError" type="video/mp4"> Your browser does not support the video tag. </video> <a href="./DecryptedMemories/FrameCountError" open><br>Open FrameCountError</a>',
        "Video is cached on device but not playable")
    html = html.replace('<video width="320" height="240" controls> <source src="./DecryptedMemories/" type="video/mp4"> Your browser does not support the video tag. </video> <a href="./DecryptedMemories/" open><br>Open </a>', "Could not be found or decrypted, "
                                                                             "usually because the Memory/MEO was " 
                                                                             "not locally stored")
    with open(f'{outputDir}/Report.html', 'w') as f:
        f.write(html)
    logger.info(f'Decrypted {len(df_report)} Memories/MEO and added them to report')


def makeImg(src):
    basename = ntpath.basename(src)
    return f'<a href="{src}"><img src="{src}" width="150"><br>Open {basename}</a>'
    #return f'<img src="{src}" width="200"/>'


def makeVideo(src):
    basename = ntpath.basename(src)
    return f'<video width="320" height="240" controls> <source src="{src}" type="video/mp4"> Your browser does not support the video tag. </video> <a href="{src}" open><br>Open {basename}</a>'
    #return f'<video width="200" controls><source src="{src}" type="video/mp4">Your browser does not ' \
    #       f'support the video tag.</video>'


def promptDate(type):
    date_entry = input(f'Enter {type} date in YYYY-MM-DD format. Leave blank to skip\n')

    if date_entry == "":
        return None

    year, month, day = map(int, date_entry.split('-'))
    if type == "end":
        day = day + 1
    dt = datetime(year, month, day)

    return getCocoaCoreTime(dt)


def getCocoaCoreTime(dt):
    unix_timestamp = calendar.timegm(dt.timetuple())
    cocoaCore = unix_timestamp - 978307200
    return (cocoaCore)


def filterDfByDates(df_merge, start_date, end_date):
    if start_date is not None and end_date is not None:
        return df_merge[(df_merge['ZCREATETIMEUTC'] >= start_date) & (df_merge['ZCREATETIMEUTC'] < end_date)]
    elif start_date is not None:
        return df_merge[(df_merge['ZCREATETIMEUTC'] >= start_date)]
    elif end_date is not None:
        return df_merge[(df_merge['ZCREATETIMEUTC'] < end_date)]
    else:
        return df_merge


def readKeychain(keychain):
    egocipher = ""
    persisted = ""
    try:  # GK Keychain
        with open(keychain, "rb") as f:
            keychain_plist = plistlib.load(f)
        for x in keychain_plist.values():
            for y in x:
                if 'agrp' in y.keys():
                    if b'3MY7A92V5W.com.toyopagroup.picaboo' == y['agrp']:
                        # logger.info("snapchat")
                        if 'gena' in y.keys():
                            if b'com.snapchat.keyservice.persistedkey' == y['gena']:
                                # logger.info("persisted")
                                # logger.info(y['v_Data'])
                                persisted = y['v_Data']
                            elif b'egocipher.key.avoidkeyderivation' == y['gena']:
                                egocipher = y['v_Data']
    except:
        try:  # Premium Keychain
            with open(keychain, "rb") as f:
                keychain_plist = plistlib.load(f)
            if "keychainEntries" in keychain_plist.keys():
                logger.info("Decrypting UFED keychain")
                convert_keychain.main(keychain, "decrypted_keychain.plist")
                with open("decrypted_keychain.plist", "rb") as f:
                    keychain_plist = plistlib.load(f)
                for y in keychain_plist:
                    if 'agrp' in y.keys():
                        if y['agrp'] == "3MY7A92V5W.com.toyopagroup.picaboo" and 'gena' in y.keys():
                            if y['gena'] == b'com.snapchat.keyservice.persistedkey':
                                persisted = y['v_Data']
                                logger.info(f"Persisted key for MEO found")
                            elif y['gena'] == b'egocipher.key.avoidkeyderivation':
                                egocipher = y['v_Data']
                                logger.info(f"Egocipher key for Memories found")
        except:
            try: #Objection keychain dump
                with open(keychain, 'rb') as f:
                    json_data = json.load(f)
                for i in json_data:
                    if i['account'] == "egocipher.key.avoidkeyderivation":
                        egocipher = i['dataHex']
                    elif i['account'] == "com.snapchat.keyservice.persistedkey":
                        persisted = i['dataHex']
            except Exception as error:
                logger.error("Could not read keychain, this is unexpected, contact author", error)
                
    if egocipher == "" or egocipher == b'':
        logger.info("Could not find correct key (egocipher) in keychain, please verify manually and contact the author if "
              "it is present")
    
    if isinstance(egocipher, bytes):
        egocipher = egocipher.hex()
    if isinstance(persisted, bytes):
        persisted = persisted.hex()
              
    return egocipher, persisted


def main(enc_db, scdb, keychain, cache_df, SCContentFolder):
    global decryptedName
    global outputDir
    global SCContentFolder_path
    global exe_path
    global platform
    global using_exe
    
    platform = system()
    
    if getattr(sys, 'frozen', False):
        exe_path = sys._MEIPASS
        using_exe = True
    else:
        exe_path = os.path.dirname(os.path.abspath(__file__))
        using_exe = False
        
    logger.info("Decrypting locally stored Memories and MEO")

    outputDir = "./Snapchat_LocalMemories_report_" + datetime.today().strftime('%Y%m%d_%H%M%S')
    os.makedirs(outputDir + "//DecryptedMemories", exist_ok=True)

    #enc_db = sys.argv[1]
    #scdb = sys.argv[2]
    #keychain = sys.argv[3]
    #cache_df = sys.argv[4]

    SCContentFolder_path = SCContentFolder
    
    decryptedName = "gallery_decrypted.sqlite"

    start_date = None
    end_date = None

    if not isSqliteInstalled():
        return cache_df
        
    try:
        egocipher, persisted = readKeychain(keychain)
        if egocipher == "" or egocipher == b'':
            logger.info("Could not find keys for memories in keychain, skipping this step")
            shutil.rmtree(outputDir)
            return cache_df
        if not checkDatabase(enc_db):
            decrypt_sqlcipher(enc_db, egocipher)
            # decryptGalleryDB(enc_db, egocipher, persisted)
            # success = recoverDatabase()
            # if not success:
                # logger.info(f"{os.path.basename(enc_db)} is empty or not decrypted, cannot decrypt memories")
                # return cache_df
            df_MemoryKey = getMemoryKey(decryptedName)
        else:
            logger.info("Gallery database is already decrypted")
            decryptedName = enc_db
            df_MemoryKey = getMemoryKey(decryptedName)
        
        if len(df_MemoryKey) == 0:
            logger.info(f"No keys for memories could be found in {decryptedName} - Aborting")
            return
    
        df_SCDBInfo = getFullSCDBInfo(scdb)
        df_merge = pd.merge(df_MemoryKey, df_SCDBInfo, on=["ID"])

        df_merge = filterDfByDates(df_merge, start_date, end_date)

        df_merge = decryptMemoriesLocal(egocipher, persisted, df_merge, cache_df)
        df_merge = df_merge.replace("", np.nan)
        df_merge = df_merge.groupby("ID").first().reset_index()
        df_merge = df_merge.replace(np.nan, "")
        generateReport(df_merge)
        logger.info(f"Report can be found in {outputDir}")
        logger.info(f"Decrypted memories can be found in {outputDir}/DecryptedMemories")
        return df_merge
    except Exception as Error:
        logger.info(f"Error: {Error}")
        logger.info("Something went wrong, contact author if you have any questions")


if __name__ == "__main__":
    main(sys.argv)
