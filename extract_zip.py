from zipfile import ZipFile
import sys
import glob
import os
import shutil

def extract(file_name, mode):

    ios_files = ['Documents/user_scoped',  ### Filer som behövs från iOS
                 'Documents/global_scoped',
                 'Documents/com.snap.file_manager_3_SCContent_',
                 'Documents/user.plist',
                 'Library/Caches/SCPersistentMedia',
                 'group.snapchat.picaboo',
                 'gallery_data_object',
                 'gallery_encrypted_db',
                 'app_group_plist_storage']

    android_files = ['com.snapchat.android/databases',  #### Filer som behövs från Android
                     'com.snapchat.android/files/file_manager/chat_snap',
                     'com.snapchat.android/files/file_manager/snap']
                     
    if mode == "ios":
        if os.path.isdir("Application") or os.path.isdir("AppGroup"):
            print("""
##################################################################################################################
Application or AppGroup folder already found, assuming files are already extracted. 
Rename the folders and run again to extract Snapchat data from zip
##################################################################################################################""")
            return os.path.realpath("Application").replace("\\", "/"), os.path.realpath("AppGroup").replace("\\", "/")
    elif mode == "android":
        if os.path.isdir("com.snapchat.android"):
            print("""
##################################################################################################################
com.snapchat.android folder already found, assuming files are already extracted. 
Rename the folder and run again to extract Snapchat data from zip
##################################################################################################################""")
            return os.path.realpath("com.snapchat.android").replace("\\", "/")
            
    snapchat_found = False        
    print(f"Reading contents of zip {file_name}")
    with ZipFile(file_name, 'r') as zip1:
        files_in_zip = zip1.namelist()
        print(f"{len(files_in_zip)} files found in zip")
        print("Extracting relevant Snapchat files from zip") 
        if mode == "ios":
            files_to_extract = ios_files
        elif mode == "android":
            files_to_extract = android_files
        else:
            print("Invalid OS when extracting files from zip")
            
        if mode == "android":
            try:
                for i in files_in_zip:  
                    if any(int_file in i for int_file in files_to_extract):
                        try:
                            index = i.find("com.snapchat.android")
                            if index == -1:
                                continue
                            else:
                                snapchat_found = True
                                data = zip1.read(i)
                                if not os.path.exists(os.path.dirname(i[index:])):
                                    os.makedirs(os.path.dirname(i[index:]))
                                try:
                                    with open(i[index:], "wb") as file:
                                        file.write(data)
                                except PermissionError:
                                    pass
                        except Exception as err:
                            pass
                            #print(err)
            except Exception as err:
                pass
                #print(err)
            if snapchat_found:
                print("Snapchat files extracted to com.snapchat.android folder")
                return os.path.realpath("com.snapchat.android").replace("\\", "/")
            else:
                print("Snapchat not found in extraction")
                os.system("pause")
                        
        if mode == 'ios':
            try:
                for i in files_in_zip:  
                    if any(int_file in i for int_file in files_to_extract):
                        try:
                            try:
                                index = i.find("Application")
                                if index == -1:
                                    raise Exception
                            except:
                                index = i.find("AppGroup")
                            data = zip1.read(i)
                            if not os.path.exists(os.path.dirname(i[index:])):
                                os.makedirs(os.path.dirname(i[index:]))
                            try:
                                filename = (i[index:].replace(":","_"))
                                with open(filename, "wb") as file:
                                    file.write(data)
                            except PermissionError:
                                pass
                        except Exception as err:
                            pass
                            #print(err)
            except Exception as err:
                pass
                #print(err)
            if not os.path.exists("Application"):
                print("Can't find any Snapchat-files in extraction. Snapchat is probably not installed")
                os.system("pause")
                sys.exit()
            if not os.path.exists("AppGroup"):
                print("Snapchat files extracted to Application folder - Could not find files located in AppGroup")
                return os.path.realpath("Application").replace("\\", "/"), ""
            else:
                print("Snapchat files extracted to Application and AppGroup folders")
                return os.path.realpath("Application").replace("\\", "/"), os.path.realpath("AppGroup").replace("\\", "/")
            

if __name__ == "__main__":
    main(sys.argv[1:])
