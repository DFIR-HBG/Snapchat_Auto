##
##DENNA FIL ÄR MODIFIERAD FÖR ATT FUNKA MED Snapchat_Auto, ANVÄND EN ANNAN VERSION AV ParseSnapchat IFALL DU VILL KÖRA ENBART DET SCRIPTET
##SCRIPTET ÄR BASERAT PÅ ParseSnapchat v1.1 MEN MED MÅNGA FÖRBÄTTRINGAR
##


import os
import glob
import sqlite3
import pandas as pd
import plistlib
import re
import shutil
import sys
from scripts.data.parse3 import *
import datetime
import ntpath
import filetype
from scripts.data import ccl_bplist
from pathlib import Path
from platform import system
from time import time
import numpy as np
import math
import blackboxprotobuf
import xml.etree as ET
import hashlib
from scripts import DecryptLocalMemories_iOS

def proto_to_msg(bin_file):
    messages_found = []
    messages = ParseProto(bin_file)
    #print(messages)

    res = find_string_in_dict(messages)
    for k, v in res:
        if "string" in k:
            messages_found.append(v)
            
    if messages_found == [] or len(messages_found) >= 2:
        message,typedef = blackboxprotobuf.decode_message(bin_file)
        try:
            messages_found = [(message['4']['4']['2']['1'].decode())]
        except:
            for i in messages_found:
                if '.1020' in i:
                    messages_found = i
            pass
    return messages_found


def find_string_in_dict(data):
    for k, v in data.items():
        if isinstance(v, dict):
            yield k, v
            yield from find_string_in_dict(v)
        else:
            yield k, v
            
            
def getHtml(final_df, friends_df, group_df):
    
    if getattr(sys, 'frozen', False):
        exe_path = sys._MEIPASS
        try:
            shutil.copytree(f"{exe_path}/css", f"{outputDir}/css")
        except:
            print("Could not copy the CSS folder, result might look a bit worse")
    else:
        exe_path = os.path.dirname(os.path.abspath(__file__))
        try:
            shutil.copytree(f"{exe_path}/data/css", f"{outputDir}/css")
        except:
            print("Could not copy the CSS folder, result might look a bit worse")
    
    print("Writing HTML report")
    for index, row in final_df.iterrows():
        final_df.loc[index, 'Message Content'] = path_to_image_html(row["Message Content"])
        
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
    for index, clientConversationID in final_df.groupby('Client Conversation ID'):
        html = html + template % clientConversationID.to_html(classes=["table table-bordered table-striped table-hover table-xl table-responsive text-break w-auto"], escape=False, index=False)
        
    html = html + template % friends_df.to_html(classes=["table table-bordered table-striped table-hover table-xl table-responsive text-wrap"], escape=False, index=False)
    html = html + template % group_df.to_html(classes=["table table-bordered table-striped table-hover table-xl table-responsive text-wrap"], escape=False, index=False)

    html = html.replace('<th>Creation Timestamp UTC+0</th>', '<th style="min-width: 200px;">Creation Timestamp UTC+0</th>')
    html = html.replace('<th>Read Timestamp UTC+0</th>', '<th style="min-width: 200px;">Read Timestamp UTC+0</th>')
    html = html.replace('<th>Server Message ID</th>', '<th style="min-width: 200px;">Server Message ID</th>')
    html = html.replace('<th>Client Conversation ID</th>', '<th style="min-width: 200px;">Client Conversation ID</th>')
    html = html.replace('<th>Content Type</th>', '<th style="min-width: 170px;">Content Type</th>')
    html = html.replace('<th>Sender ID</th>', '<th style="min-width: 150px;">Sender ID</th>')
    html = html.replace('<th>Message Content</th>', '<th style="min-width: 200px;">Message Content</th>')

    return html
    

def path_to_image_html(filename):
    global attachmentPath_relative
    global outputDir_name
    
    dots_regex = re.compile("^\.+$")
    
    try:
        path = Path(outputDir + "/cacheFiles/" + filename)
    except TypeError:
        return

    try:
        path = path.replace("\\", "/")
    except Exception:
        pass
        
    try:
        if os.path.exists(path):
            try:
                basename = ntpath.basename(path)
                realpath = os.path.abspath(path)
                kind = filetype.guess(path)
                if platform == "Windows":
                    relpath = realpath.split("\\")[-2:]
                else:
                    relpath = realpath.split("/")[-2:]
                relpath = str(Path(relpath[0] + "/" + relpath[1]))
                if kind.extension == "mp4":
                    return ('<video width="320" height="240" controls> <source src="' + (
                        relpath) + '" type="video/mp4"> Your browser does not support the video tag. </video> <a href="' + (
                                relpath) + '"><br>' + basename + '</a>')
                elif kind.extension == "png":
                    return ('<a href="' + (relpath) + '"><img src="' + (
                        relpath) + '" width="150" ><br>' + basename + '</a>')
                elif kind.extension == "jpg":
                    return ('<a href="' + (relpath) + '"><img src="' + (
                        relpath) + '" width="150" ><br>' + basename + '</a>')
                else:
                    return filename + " - Unknown extension: " + kind.extension
            except PermissionError as Error:
                if dots_regex.match(filename):
                    return filename
                else:
                    print(Error)
                    return filename + " missing attachment"
        else:
            return filename
    except:
        return


def getUserID(userPlist):
    try:
        if os.path.exists(userPlist):
            print("Getting User ID from " + ntpath.basename(userPlist))
            with open(userPlist, "rb") as f:
                data = f.read()
                uuid = re.search('[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', str(data))
            print("")
            return (uuid.group(0))
        else:
            print("User.plist not found! User might be logged out from Snapchat. Data will likely be incomplete.")
            return ""
    except Exception as Error:
        print(Error)
        return ""
        
def getUserIDFromGroups(group_plist):
    print("Getting UserID from Groups plist")
    
    with open(group_plist, "rb") as f:
        data = plistlib.loads(f.read())

    lista = {"Userid": [], "Timestamp": []}

    for i in data:
        if "appLastUsedTimestamp" in i:
            uuid = re.search('[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', str(i))
            lista["Userid"].append(uuid.group(0))
            lista["Timestamp"].append(data[i])
            
    df = pd.DataFrame.from_dict(lista)
    df = df.sort_values(by="Timestamp", ascending=False)
    for i in df["Userid"]:
        print(f"User ID: {i}")
        return(i)

def getUserIDFromArroyo(arroyo):
    print("Getting UserID from arroyo")
    conn = sqlite3.connect(arroyo)
    messagesQuery = """select
    value
    from required_values where key = "USERID"
    """
    df = pd.read_sql_query(messagesQuery, conn)
    
    print(f"User ID: {df['value'][0]}")
    return df["value"][0]
    
def getFriendsAppGroupPlistStorage(app_group_plist_storage_list, arroyo):
    
    if len(app_group_plist_storage_list) == 0:
        raise KeyError
    
    app_group_plist_storage_user = ""
    app_group_plist_storage_friends_groups = ""
    
    print("Did not find friends in Groups plist, trying from app_group_plist_storage")
    
    if len(app_group_plist_storage_list) == 1:
        app_group_plist_storage_friends_groups = app_group_plist_storage_list[0]
    else:
        for i in app_group_plist_storage_list:
            if "User" in i:
                app_group_plist_storage_user = i
            else:
                app_group_plist_storage_friends_groups = i
    # else: #Sorts the files based on size, the biggest one should contain friends/groups. The smallest one should contain info about the logged in user
        # app_group_plist_storage_list = sorted(app_group_plist_storage_list, key = lambda x: os.stat(x).st_size)
        # app_group_plist_storage_friends_groups = app_group_plist_storage_list[-1]
        # app_group_plist_storage_user = app_group_plist_storage_list[0]
    
    print(f"Friends: {app_group_plist_storage_friends_groups}")
    print(f"Userdata: {app_group_plist_storage_user}")

    with open(app_group_plist_storage_friends_groups, "rb") as f:
        data = plistlib.loads(f.read())

    with open("test.plist", "wb") as test:
        try:
            test.write(data["snapchatter_repository"])
        except KeyError:
            try:
                test.write(data["share_user"])
                print("found share_user in app_group_plist_storage")
                friends_df, group_df = getFriendsPlist(app_group_plist_storage_friends_groups)
                return friends_df, group_df
            except KeyError:
                raise KeyError

    with open("test.plist", "rb") as test:
        plist = ccl_bplist.load(test)
        data1 = ccl_bplist.deserialise_NsKeyedArchiver(plist)    
    
    if app_group_plist_storage_user != "":
        with open(app_group_plist_storage_user, "rb") as f:
            userdata = plistlib.loads(f.read())
    
    display = []
    name = []
    conversation_id = []
    group_participants = []
    user_id = []
    group_name = ""
    groups = {"Group Name": [], "Participants": [], "Conversation ID": []}
    df_group = pd.DataFrame(columns=['Group Name', 'Participants', 'Conversation ID'])

    try:  #Gathers info on logged in user
        current_username = "<b>" + userdata["username"] + "</b>"
        current_userid = userdata["userId"]
        name.append(current_username)
        user_id.append(current_userid)
        conversation_id.append("")
        display.append("")
    except:
        print("Could not find logged in user info")
        
    for i in data1["FRIENDS"]["NS.objects"]: #Getting info in Friends
        try:
            user_id.append(i["USER_ID"])
        except:
            user_id.append("Unknown")

        try:
            tmp_display = i["NAME_TO_DISPLAY"].encode('cp1252', 'xmlcharrefreplace')
            tmp_display = tmp_display.decode('cp1252')
            display.append(tmp_display)
        except:
            display.append("Unknown")

        try:
            name.append(i["USERNAME"])
        except:
            name.append("Unknown")

        try:
            conversation_id.append(i["CONVERSATION_ID"])
        except:
            conversation_id.append("Unknown")

    resultat = {'Display name': display, 'Username': name, 'User ID': user_id, 'Conversation ID': conversation_id}
    try:
        friends_df = pd.DataFrame(resultat)
        friends_df = friends_df.drop_duplicates()
    except Exception as Error:
        print(f"Error creating Friends DataFrame: {Error}")    
    
    for i in data1["GROUPS"]["NS.objects"]: #Getting info on Chat groups
        try:
            group_name = i['GROUP_NAME'].encode('cp1252', 'xmlcharrefreplace').decode(
                'cp1252')
            group_id = i['GROUP_ID']
        except Exception as Error:
            print("Group ID/Name Error:", Error)
        group_participants = []
        try:
            if i['GROUP_PARTICIPANTS_USER_NAMES'] != "$null":
                for j in i['GROUP_PARTICIPANTS_USER_NAMES']['NS.objects']:
                    group_participants.append(str(j))
        except Exception as Error:
            print("Group participant username Error:", Error)

        groups["Conversation ID"].append(group_id)
        groups["Group Name"].append(group_name)
        groups["Participants"].append(group_participants)
        
    group_df = pd.DataFrame(groups)
    
    try: #Getting info on Chat groups that does not have a set name (Might not be needed, will need more testing)
        query = """select 
        client_conversation_id as "Conversation ID",
        group_concat(user_id) as "User ID"
        from user_conversation where conversation_type is 1
        group by client_conversation_id"""
        conn = sqlite3.connect(arroyo)
        df = pd.read_sql_query(query, conn)
        grupper = {"Group Name":[], "Participants": [], "Conversation ID": []}

        for index, row in df.iterrows():
            conv_id = row["Conversation ID"]
            users = []
            for i in row["User ID"].split(","):
                try:
                    username = friends_df["Username"].loc[friends_df['User ID']==i]
                    username = (username.item())
                    users.append(username)
                except:
                    users.append(i)
            grupper["Conversation ID"].append(conv_id)
            grupper["Participants"].append(users)
            grupper["Group Name"].append("No Group Name")
        #print(grupper)
    except Exception as E:
        print(f"Error getting chat groups with no name, this is not expected but will not break anything major: {E}")
        
    df_group_noname = pd.DataFrame(grupper)
    
    for index, row in df_group_noname.iterrows():
        try:
            if row["Conversation ID"] not in group_df["Conversation ID"].values:
                try:
                    group_df = group_df.append(row)
                except Exception as E:
                    raise Exception
        except Exception as E:
            print(f"Error appending chat groups with no name, this is not expected but will not break anything major: {E}")
            
    return friends_df, group_df

def getFriendsPlist(group_plist):
    print("Getting friends and groups from " + ntpath.basename(group_plist))
    with open(group_plist, "rb") as f:
        data = plistlib.loads(f.read())

    with open("test.plist", "wb") as test:
        try:
            test.write(data["share_user"])
        except KeyError:
            print("Can not find key 'share_user' in Group plist")
            try:
                test.write(data["user"])
                print(
                    "Found key 'user' in plist, this is an older version of storing friends not yet supported by this script")
            except:
                raise Exception

    with open("test.plist", "rb") as test:
        plist = ccl_bplist.load(test)
        data1 = ccl_bplist.deserialise_NsKeyedArchiver(plist)

    display = []
    name = []
    conversation_id = []
    group_participants = []
    user_id = []
    group_name = ""
    groups = {"Group Name": [], "Participants": [], "Conversation ID": []}
    df_group = pd.DataFrame(columns=['Group Name', 'Participants', 'Conversation ID'])

    try:
        current_username = "<b>" + data1["USERNAME"] + "</b>"
        current_userid = data1["USER_ID"]
        name.append(current_username)
        user_id.append(current_userid)
        conversation_id.append("")
        display.append("")
    except:
        print("Could not find logged in user info")
        
    for i in data1["SECTIONS"]["NS.objects"]:
        friends = i["DESTINATIONS"]["NS.objects"]
        for i in friends:
            if i['CODED_SUBTYPE'] == "SUBTYPE_GROUP":
                try:
                    group_name = i['GROUP_GROUP_NAME']["NS.string"].encode('cp1252', 'xmlcharrefreplace').decode(
                        'cp1252')
                    group_id = i['GROUP_GROUP_ID']
                except:
                    try:
                        group_name = i['GROUP_GROUP_NAME'].encode('cp1252', 'xmlcharrefreplace').decode('cp1252')
                        group_id = i['GROUP_GROUP_ID']
                    except Exception as Error:
                        print(Error)
                group_participants = []
                try:
                    if i['GROUP_GROUP_PARTICIPANTS_USER_NAMES'] != "$null":
                        for j in i['GROUP_GROUP_PARTICIPANTS_USER_NAMES']['NS.objects']:
                            group_participants.append(str(j))

                except Exception as Error:
                    print(Error, "Error")

                if len(group_participants) >= 1:
                    groups["Conversation ID"].append(group_id)
                    groups["Group Name"].append(group_name)
                    groups["Participants"].append(group_participants)
                else:
                    pass
            elif i['CODED_SUBTYPE'] == "SUBTYPE_FRIEND":
                try:
                    user_id.append(i["FRIEND_BITMOJI_INFO"]["USER_ID"])
                except:
                    try:
                        user_id.append(i["FRIEND_USER_ID"])
                    except:
                        user_id.append("Unknown")

                try:
                    tmp_display = i["FRIEND_DISPLAY"].encode('cp1252', 'xmlcharrefreplace')
                    tmp_display = tmp_display.decode('cp1252')
                    display.append(tmp_display)
                except:
                    display.append("Unknown")

                try:
                    name.append(i["FRIEND_NAME"])
                except:
                    name.append("Unknown")

                try:
                    conversation_id.append(i["FRIEND_CONVERSATION_ID"]["NS.string"])
                except KeyError as Error:
                    conversation_id.append("Unknown")
            else:
                print(f"Unknown Contact Subtype: {i['CODED_SUBTYPE']}")

    resultat = {'Display name': display, 'Username': name, 'User ID': user_id, 'Conversation ID': conversation_id}
    try:
        df_friends = pd.DataFrame(resultat)
    except Exception as Error:
        print(Error)
    df_group = pd.DataFrame(groups)

    df_friends = df_friends.drop_duplicates()

    return df_friends, df_group


def getFriendsPrimary_DisplayMetadata(primary, arroyo):
    print(f"Could not get friends from default location, trying from third location {ntpath.basename(primary)} and {ntpath.basename(arroyo)} (EXPERIMENTAL)")
    #print("Gathering friends from " + ntpath.basename(primary))
    print("WARNING - MIGHT contain users that are not friends")
    conn = sqlite3.connect(primary)
    messagesQuery = """select
    userId as 'User ID',
    p as Username
    from snapchatters__displaymetadata
    """
    df_friends = pd.read_sql_query(messagesQuery, conn)

    for index, row in df_friends.iterrows():
        try:
            data = row["Username"]
            counter = 0
            for i in data[56:]:
                if i == 0:
                    break
                else:
                    counter += 1
            slut = 56 + counter
            namn = data[56:slut]
            namn = namn.decode()
            namn = namn.encode('cp1252', 'xmlcharrefreplace')  # Display Emojis
            namn = namn.decode('cp1252')
            df_friends.loc[index, "Username"] = namn
        except Exception as Error:
            df_friends.loc[index, "Username"] = ""
            print(f"Could not find Display name for user {row['User ID']}, {Error}")

    conn = sqlite3.connect(arroyo)
    messagesQuery = """select
    user_id as 'User ID',
    client_conversation_id as 'Conversation ID',
    CASE 
        WHEN conversation_type is 0 THEN 'Private'
        WHEN conversation_type is 1 THEN 'Group'
        ELSE conversation_type
        END "Conversation Type"
    from user_conversation
    """

    df_conversations = pd.read_sql_query(messagesQuery, conn)

    private_conv = df_conversations[df_conversations["Conversation Type"] == "Private"].drop(columns=["Conversation Type"])
    array = []
    for index, row in private_conv.iterrows():
        lista = [row["User ID"], row["Conversation ID"]]
        array.append(lista)

    for index, row in df_friends.iterrows():
        user = row["User ID"]
        for item in array:
            if user == item[0]:
                df_friends.loc[index, "Conversation ID"] = item[1]

    query = """select 
    client_conversation_id as "Conversation ID",
    group_concat(user_id) as "User ID"
    from user_conversation where conversation_type is 1
    group by client_conversation_id"""
    conn = sqlite3.connect(arroyo)
    df = pd.read_sql_query(query, conn)
    grupper = {"Conversation ID": [], "Participants": []}

    for index, row in df.iterrows():
        conv_id = []
        conv_id.append(row["Conversation ID"])
        users = []
        for i in row["User ID"].split(","):
            try:
                username = df_friends["Username"].loc[df_friends['User ID']==i]
                username = (username.item())
                users.append(username)
            except:
                users.append(i)
                pass
        grupper["Conversation ID"].append(conv_id)
        grupper["Participants"].append(users)

    df_group = pd.DataFrame(grupper)
    
    conn = sqlite3.connect(primary)
    messagesQuery = """select
    snapchatter.userId as 'User ID',
    snapchatter.rowid,
    index_snapchatterusername.username as 'Username'
    from snapchatter
    inner join index_snapchatterusername ON snapchatter.rowid=index_snapchatterusername.rowid
    """
    
    df_snapchatter = pd.read_sql_query(messagesQuery, conn)
    
    return df_friends, df_group, df_snapchatter
    
    
def getFriendsPrimary(primary, arroyo):
    print("Gathering friends from " + ntpath.basename(primary))
    print("WARNING - WILL contain users that are not friends")
    try:
        conn = sqlite3.connect(primary)
        messagesQuery = """select
        snapchatter.userId as 'User ID',
        snapchatter.rowid,
        index_snapchatterusername.username as 'Username'
        from snapchatter
        inner join index_snapchatterusername ON snapchatter.rowid=index_snapchatterusername.rowid
        """
        df = pd.read_sql_query(messagesQuery, conn)
        df = df.rename(columns={"userId" : "User ID", "username" : "Username"})

        df_group = pd.DataFrame(columns=['Group Name', 'Participants', 'Conversation ID'])
        if len(df) == 0:
            raise Exception

        print("")
        return df, df_group
    except:
        raise Exception


def fixSenders(df_messages, df_friends, df_snapchatter):
    print("Replacing user ID with username in chats")
    try:
        array = []
        array2 = []
        for index, row in df_friends.iterrows():
            lista = [row["User ID"], row["Username"]]
            array.append(lista)
        for index, row in df_snapchatter.iterrows():
            lista = [row["User ID"], row["Username"]]
            array2.append(lista)

        for index, row in df_messages.iterrows():
            sender = row["sender_id"]
            found = False
            for item in array:
                if sender == item[0]:
                    df_messages.loc[index, "sender_id"] = item[1]
                    #print(item)
                    found = True    
            if not found:
                for i in array2:
                    if sender in i:
                        df_messages.loc[index, "sender_id"] = i[1]
    except Exception as E:
        print(E)
        pass

    print("")
    return df_messages


def getCacheArroyo(arroyo, cache_df):
    cache_df = cache_df.reset_index()
    print("Getting cache files from " + ntpath.basename(arroyo))
    conn = sqlite3.connect(arroyo)
    messagesQuery = """select
            client_conversation_id,
            server_message_id,
            local_message_references,
            content_type
            from conversation_message where local_message_references is not NULL
            order by client_conversation_id, server_message_id
            """

    df_arroyo = pd.read_sql_query(messagesQuery, conn)
    # uuid_pattern = re.compile("[A-F0-9-]{36}")
    df_arroyo['message_content'] = np.nan
    # print(df_arroyo['local_message_references'])
    # os.system("pause")

    for index, row in df_arroyo.iterrows():
        data = row['local_message_references']

        with open("temp.plist", 'wb') as temp:
            temp.write(data[8:])
        try:
            with open('temp.plist', 'rb') as data:
                plist = ccl_bplist.load(data)
                data1 = ccl_bplist.deserialise_NsKeyedArchiver(plist)
            data = re.search(".*[A-F0-9-]{36}", data1['MEDIA_ID'])
            # print(data)
            # print(row['client_conversation_id'])
            # print(row['server_message_id'])
            try:
                index1 = cache_df.index[cache_df['EXTERNAL_KEY'] == data.group()].values[0]
                index1 = int(index1)
                #print(index1)
                cache_key = cache_df.iloc[index1]['CACHE_KEY']
                # print(cache_key)
                df_arroyo.loc[index, 'message_content'] = cache_key
            except Exception as Error:
                # print(Error)
                pass

            # print(data.group())
        except Exception as error:
            print(error, index)
    
    if os.path.exists("temp.plist"):
        os.remove("temp.plist")
    # os.system("pause")
    #print(df_arroyo)
    #os.system("pause")

    return df_arroyo


def getCache(cachecontroller):
    print(f"Getting cache files from {ntpath.basename(cachecontroller)} and {SCContentFolder.split('/')[-2]}")
    conn = sqlite3.connect(cachecontroller)
    if uuid != "":
        messagesQuery = f"""select
        *
        from CACHE_FILE_CLAIM where USER_ID is '{uuid}' and MEDIA_CONTEXT_TYPE in (3,19) and DELETED_TIMESTAMP_MILLIS is 0"""
    else:
        messagesQuery = f"""select
        *
        from CACHE_FILE_CLAIM where MEDIA_CONTEXT_TYPE in (3,19) and DELETED_TIMESTAMP_MILLIS is 0"""
    df_cache = pd.read_sql_query(messagesQuery, conn)   
    foundFiles = glob.glob(SCContentFolder + '*')
    tmp = []
    for item in foundFiles:
        item = item.replace("\\", "/")
        tmp.append(item)
    foundFiles = tmp

    if keychain_file is not "":
        df_merge = DecryptLocalMemories_iOS.main(galleryEncrypteddb, scdb, keychain_file, df_cache, SCContentFolder)
        print("")
        print("Getting cache files again")
    
    for index, row in df_cache.iterrows():
        try:
            file = SCContentFolder + row["CACHE_KEY"]
            file = file.replace("\\", "/")
            if file in foundFiles:
                fileIndex = foundFiles.index(file)
                kind = filetype.guess(foundFiles[fileIndex])
                if os.stat(foundFiles[fileIndex]).st_size != 0 and kind is not None:
                    if kind.extension == "mp4" or kind.extension == "jpg" or kind.extension == "png":
                        shutil.copy(foundFiles[fileIndex], outputDir + '//cacheFiles')
                    else:
                        df_cache = df_cache.drop(index)  # ("dropping because of invalid type")
                else:
                    df_cache = df_cache.drop(index)  # ("dropping because of 0 size")
            else:
                df_cache = df_cache.drop(index)  # ("dropping because of file not found")
        except Exception as E:
            print("Error copying cache files", E)

    print("")
    return (df_cache)


def getChats(database):
    print("Getting chats from " + ntpath.basename(database))
    conn = sqlite3.connect(database)

    messagesQuery = """select
    client_conversation_id,
    server_message_id,
    message_content,
    datetime(creation_timestamp/1000, 'unixepoch') as 'Creation Timestamp',
    CASE 
        datetime(read_timestamp/1000, 'unixepoch') when '1970-01-01 00:00:00' then "" 
        else datetime(read_timestamp/1000, 'unixepoch')
        end as 'Read Timestamp',
    content_type,
    sender_id
    from conversation_message
    order by client_conversation_id, creation_timestamp
    """

    df = pd.read_sql_query(messagesQuery, conn)

    for index, row in df.iterrows():
        message = (row["message_content"])
        messages = proto_to_msg(message)
        meddelande = ""
        try:
            if len(messages) >= 2:
                for i in messages:
                    tmp = i.encode('cp1252', 'xmlcharrefreplace')  # Display Emojis
                    tmp = tmp.decode('cp1252')
                    meddelande = meddelande + tmp

            else:
                i = messages[0].encode('cp1252', 'xmlcharrefreplace')
                meddelande = i.decode('cp1252')
            
            #if meddelande is "None":
            #print(meddelande)
            df.loc[index, "message_content"] = meddelande

        except Exception as e:
            df.loc[
                index, "message_content"] = """ERROR - Something went wrong when parsing this message. \n Manually verify the message with Client Conversation ID and Server Message ID in arroyo.db"""

    print("")
    return df


def mergeCacheChats(cache_df, chats_df, persistent_df, cache_arroyo_df):
    print("Merging chats with cache files")
    # print(chats_df['server_message_id'])
    for index_arroyo, row_arroyo in cache_arroyo_df.iterrows():
        for index_chat, row_chat in chats_df.iterrows():
            if row_chat['client_conversation_id'] == row_arroyo['client_conversation_id'] and \
                    row_chat['server_message_id'] == row_arroyo['server_message_id']:
                if not isinstance(row_arroyo['message_content'], float):
                    #print(row_arroyo['message_content'])
                    #print(type(row_arroyo['message_content']))
                    chats_df.loc[index_chat, 'message_content'] = row_arroyo['message_content']
                    chats_df.loc[index_chat, 'content_type'] = 'local_message_reference'
                else:
                    continue
    
    #Ändrar external_key i message_content till cache_key för att kunna ersätta med fil
    test = cache_df.to_dict(orient='list')
    for index, row in chats_df.iterrows():
        dict_index = 0
        for i in test['EXTERNAL_KEY']:
            if row["message_content"] == i:
                chats_df.loc[index, 'message_content'] = test['CACHE_KEY'][dict_index]
                chats_df.loc[index, 'content_type'] = 'Unknown .1020'
            dict_index += 1

    cache_df_v2 = pd.DataFrame(columns=['CACHE_KEY', 'TYPE', 'client_conversation_id', 'server_message_id'])
    # print(cache_df_v2)
    for index, row in cache_df.iterrows():
        try:
            data = row["EXTERNAL_KEY"]
            data = data.split(":")
            try:
                tmp_dict = {'CACHE_KEY': row["CACHE_KEY"], 'TYPE': data[0], 'client_conversation_id': data[1],
                            'server_message_id': data[2], 'SERVER_MESSAGE_ID_PART': data[3]}

                cache_df_v2 = cache_df_v2.append(tmp_dict, ignore_index=True)
            except IndexError as Error:
                pass
        except Exception as Error:
            print(Error)
    frames = [cache_df_v2, persistent_df]
    cache_df_v2 = pd.concat(frames, ignore_index=True)
    chats_df['server_message_id'] = chats_df.server_message_id.astype(str)

    merge_df = chats_df.merge(cache_df_v2, on=["client_conversation_id", 'server_message_id'], how="left")
    merged_cache_keys = merge_df['CACHE_KEY'].tolist()
    # print(type(merged_cache_keys))
    # print(cache_df_v2['CACHE_KEY'])

    for index, row in cache_df_v2.iterrows():
        if row['CACHE_KEY'] not in merged_cache_keys:
            tmp_dict = {'client_conversation_id': row["client_conversation_id"], 'message_content': row["CACHE_KEY"],
                        'Creation Timestamp': 'Unknown',
                        'Read Timestamp': 'Unknown', 'content_type': row["TYPE"], 'sender_id': 'Unknown',
                        'server_message_id': str(row["server_message_id"]) + "." + str(row['SERVER_MESSAGE_ID_PART'])}
            merge_df = merge_df.append(tmp_dict, ignore_index=True)

    

    for index, row in merge_df.iterrows():
        try:
            if type((row['CACHE_KEY'])) == str:
                merge_df.loc[index, 'message_content'] = row['CACHE_KEY']
            try:
                if str(row['SERVER_MESSAGE_ID_PART']) == "nan":
                    merge_df.loc[index, 'server_message_id'] = str(row["server_message_id"])
                else:
                    merge_df.loc[index, 'server_message_id'] = str(row["server_message_id"]) + "." + str(
                        row['SERVER_MESSAGE_ID_PART'])
            except:
                pass
                
            if row['content_type'] == 1:
                merge_df.loc[index, 'content_type'] = "Text"
            else:
                if row['content_type'] == 'local_message_reference' or row['content_type'] == 'Unknown .1020':
                    continue
                elif type(row["TYPE"]) != str:
                    merge_df = merge_df.drop(index=index)
                else:
                    if row["TYPE"] == "cm-chat-media-video-1":
                        merge_df.loc[index, 'content_type'] = "Media saved in chat"
                    elif row["TYPE"] == "1":
                        merge_df.loc[index, 'content_type'] = "Temporarily stored media"
                    elif row["TYPE"] == "thumbnail~1":
                        merge_df.loc[index, 'content_type'] = "Thumbnail"
                    else:
                        merge_df.loc[index, 'content_type'] = row["TYPE"]
        except Exception as error:
            print(error)
            pass
    merge_df.server_message_id = pd.to_numeric(merge_df.server_message_id)
    final_df = merge_df.rename(
        columns={'client_conversation_id': 'Client Conversation ID', 'server_message_id': 'Server Message ID',
                 'message_content': 'Message Content', 'content_type': 'Content Type', 'sender_id': 'Sender ID'})
    try:
        final_df = final_df.drop(columns=['CACHE_KEY', 'SERVER_MESSAGE_ID_PART', 'TYPE'])
    except:
        final_df = final_df.drop(columns=['CACHE_KEY', 'TYPE'])
    print("")
    return final_df


def getSCPersistentMedia():
    persistent_df = pd.DataFrame(columns=['CACHE_KEY', 'TYPE', 'client_conversation_id', 'server_message_id'])
    path = snapchatFolder + "/Library/Caches/SCPersistentMedia/"
    if os.path.isdir(path):
        pass
    else:
        print("Could not find SCPersistentMedia folder, this could be due to no manually saved media in chats")
        return
    files = os.listdir(Path(path))
    for file in files:
        file_path = path + file
        if os.stat(Path(file_path)).st_size != 0:
            outPutCache = Path(outputDir + '/cacheFiles/')
            shutil.copy(file_path, outPutCache)
        else:
            pass
        file_split = file.split("_")
        try:
            tmp_dict = {'CACHE_KEY': file, 'TYPE': file_split[0], 'client_conversation_id': file_split[1],
                        'server_message_id': file_split[2], 'SERVER_MESSAGE_ID_PART': file_split[3]}
            persistent_df = persistent_df.append(tmp_dict, ignore_index=True)
        except:
            pass

    return persistent_df


def main(Application, AppGroup, keychain):
    global snapchatFolder
    global groupPlist
    global outputDir
    global SCContentFolder
    global uuid
    global platform
    global final_df
    global scdb
    global galleryEncrypteddb
    global keychain_file

    platform = system()
    print(f"Running on {platform}")

    if platform != "Windows" and platform != "Linux":
        print(f"WARNING! Your platform {platform} might not be supported")

    uuid_pattern = re.compile("[A-F0-9-]{36}")
    previous = ""
    #counter = 0
    for root, dirs, files in os.walk(Application):
        if uuid_pattern.match(dirs[0]):
            base_folder_data = dirs[0]
            break
    
    for root, dirs, files in os.walk(AppGroup):
        if uuid_pattern.match(dirs[0]):
            base_folder_share = dirs[0]
            break

    snapchatFolder = Application + "/" + base_folder_data
    base_folder_share = AppGroup + "/" + base_folder_share
    print(snapchatFolder)
    print(base_folder_share)
    df_snapchatter = pd.DataFrame({})

    try:
        userPlist = Path(snapchatFolder + "/Documents/user.plist")
        uuid = getUserID(userPlist)
        uuid_sha256 = hashlib.sha256(uuid.encode("utf-8")).hexdigest()
        arroyo = glob.glob(snapchatFolder + "/Documents/user_scoped/**/*arroyo.db", recursive=True)
        user_scoped_id = arroyo[0].replace("\\", "/").split("/")[-3]
        primaryDoc = glob.glob(snapchatFolder + "/Documents/user_scoped/**/*primary.docobjects", recursive=True)
        cacheController = glob.glob(snapchatFolder + "/Documents/global_scoped/cachecontroller/*cache_controller.db",
                                    recursive=True)
        groupPlist = glob.glob(base_folder_share + "/**/group.snapchat.picaboo.plist", recursive=True)[0]
        app_group_plist_storage = glob.glob(base_folder_share + "/**/app_group_plist_storage", recursive=True)
        outputDir = "./Snapchat_iOS_report_" + datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
        os.makedirs(outputDir + "//cacheFiles", exist_ok=True)
        try:
            galleryEncrypteddb = glob.glob(snapchatFolder + f"/Documents/**/{uuid_sha256}/gallery.encrypteddb", recursive = True)[0]
        except:
            try:
                galleryEncrypteddb = glob.glob(snapchatFolder + f"/Documents/**/{user_scoped_id}/gallery.encrypteddb", recursive = True)[0]
            except:
                galleryEncrypteddb = ""
        try:
            scdb = glob.glob(snapchatFolder + f"/Documents/**/{uuid_sha256}/scdb-27.sqlite3", recursive = True)[0]
        except:
            try:
                scdb = glob.glob(snapchatFolder + f"/Documents/**/{user_scoped_id}/scdb-27.sqlite3", recursive = True)[0]
            except:
                scdb = ""
        keychain_file = keychain
        if uuid != "":
            SCContentFolder = snapchatFolder + "/Documents/com.snap.file_manager_3_SCContent_" + uuid + "/"
        else:
            SCContentFolder = glob.glob(snapchatFolder + "/Documents/com.snap.file_manager_3_SCContent_*")
            if len(SCContentFolder) == 1:
                SCContentFolder = SCContentFolder[0] + "/"
            else:
                try:
                    uuid = getUserIDFromGroups(groupPlist)
                except:
                    uuid = getUserIDFromArroyo(arroyo[0])
                SCContentFolder = snapchatFolder + "/Documents/com.snap.file_manager_3_SCContent_" + uuid + "/"
        

    except Exception as Error:
        print(Error)

    if os.path.exists(groupPlist) and os.path.exists(snapchatFolder):
        pass
    else:
        print("Group plist does not exist, cannot find Display Name")
        print("Using primary.docobjects instead")
        print("")
        groupPlist = ""

    if groupPlist != "":
        try:
            friends_df, group_df = getFriendsPlist(groupPlist)
        except Exception as Error:
            try:
                friends_df, group_df = getFriendsAppGroupPlistStorage(app_group_plist_storage, arroyo[0])
            except KeyError:
                print(f"Could not find friends in {app_group_plist_storage}")
                try:
                    friends_df, group_df, df_snapchatter = getFriendsPrimary_DisplayMetadata(Path(primaryDoc[0]), Path(arroyo[0]))
                except:
                    print("Could not get friends from DisplayMetadata, using last resort")
                    try:
                        friends_df, group_df, df_snapchatter = getFriendsPrimary(Path(primaryDoc[0]), Path(arroyo[0]))
                    except:
                        print("Could not find friends info anywhere! This is unexpected, please contact the author")
                        friends_df, group_df = pd.DataFrame({}), pd.DataFrame({})
    
    if os.path.exists("test.plist"):
       os.remove("test.plist")
    chats_df = getChats(arroyo[0])
    chats_df = fixSenders(chats_df, friends_df, df_snapchatter)
    cache_df = getCache(cacheController[0])
    cache_arroyo_df = getCacheArroyo(arroyo[0], cache_df)
    persistent_df = getSCPersistentMedia()
    final_df = mergeCacheChats(cache_df, chats_df, persistent_df, cache_arroyo_df)
    final_df = final_df.drop_duplicates()
    final_df = final_df.sort_values(by=['Client Conversation ID', 'Server Message ID'])
    final_df = final_df.rename(
        columns={'Creation Timestamp': 'Creation Timestamp UTC+0', 'Read Timestamp': 'Read Timestamp UTC+0'})
    final_df = final_df[["Client Conversation ID", "Sender ID", "Message Content", "Content Type", 
                            "Creation Timestamp UTC+0", "Read Timestamp UTC+0", "Server Message ID"]]

    html = getHtml(final_df, friends_df, group_df)   
    text_file = open(outputDir + "/Snapchat_report.html", "w", encoding="cp1252")
    text_file.write(html)
    text_file.close()
    print("Success, report can be found in " + os.path.abspath(outputDir))
    return user_scoped_id


if __name__ == "__main__":
    main()
