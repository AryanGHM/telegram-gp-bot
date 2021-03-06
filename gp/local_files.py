"""
Read and write to local temporary and persistence files, such as group preferences
or credential configuration files.
Author: Aryan Gholizadeh:aryghm@gmail.com
Project's github link: https://github.com/AryanGHM/telegram-gp-bot

"""
import pysqlite3 as sql
import configparser
import os

#Load credential configureation file
credentials = configparser.ConfigParser()
if len(credentials.read('credentials.ini')) < 1:
    raise RuntimeError("No credential configuration file found, visit https://github.com/AryanGHM/telegram-gp-bot for more information.")

#Create preferences directory and DB directory
if "GroupPrefs" not in os.listdir():
    os.mkdir("GroupPrefs")
    os.mkdir("GroupPrefs/DB")
elif "DB" not in os.listdir("GroupPrefs"):
    os.mkdir("GroupPrefs/DB")


"""
GroupPrefs class,
This class is a handle to a .grprf file.This reads/writes all parameters in a group
preferences file.
The constructor creates or opens a grprf file.The file is created in 
%project_root%/GroupPrefs in case it should be created.If the file is created some 
values are set to a default, A new DB is created for warning database.Database names 
are set to the group name + db and the sqlite file extension.Databases are stored in
%project_root%/GroupPrefs/DB/.

"""
class GroupPrefs:
    """
    Filter names in the group preferences files
    
    """
    locklink = "LOCK_LINK"
    lockfwd = "LOCK_FORWARD"
    
    def __init__(self, groupname):
        if groupname.endswith(".grprf"):
            self.file_name = groupname
        else:
            self.file_name = groupname + '.grprf'
        self.file_name = "GroupPrefs/" + self.file_name
        
        #Open a file handle and store it in a field
        if (self.file_name + '.grprf') in os.listdir('GroupPrefs/'):
            #if file exists just open it up
            self.config = configparser.ConfigParser()
            self.config.read(self.file_name)
        else:
            #create the file in a config format 
            self.config = configparser.ConfigParser()
            #Set warning values
            self.config["WARNINGS"] = {}
            self.config["WARNINGS"]["MAX_WARN"] = "4"
            #create a db file for the group and store it's path in grprf file.
            #paths are stored relative
            db_name = groupname.replace('.grprf', '') + "db" + ".db"
            db_path = "GroupPrefs/DB/" + db_name 
            connection = sql.connect(db_path) 
            
            self.config["WARNINGS"]["WARN_DB"] = db_path
            
            #Set group names values
            self.config["GROUP_NAMES"] = {"NAME": groupname}
            
            #Set filters config values
            self.config["FILTERS"] = {self.lockfwd: "1",# enabled by default
                                      self.locklink: "1"# enabled by default
                                      }
            
            #write the configs to file
            with open(self.file_name, "w") as configfile:
                self.config.write(configfile)
    
    #Read the config file and update the self.config field with
    #that.
    def read(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.file_name)
    
    #Fetch the group's name
    def get_gp_name(self):
        self.read() #update to latest
        return self.config["GROUP_NAMES"]["NAME"]
    
    #Return warnings database
    def get_warn_db_path(self):
        self.read() #get latest updates
        return self.config["WARNINGS"]["WARN_DB"]
    
    #Return max warning count in int
    def get_max_warn(self):
        self.read() #get latest updates
        return int(self.config["WARNINGS"]["MAX_WARN"])
    
    #Set maximum warning count
    def set_max_warn(self, max_warn):
        try:
            max_warn = str(max_warn)
        except ValueError:
            #wrong max_warn value, probably a str
            return False
        
        if max_warn:
            self.config["WARNINGS"]["MAX_WARN"] = max_warn
        else:
            #value is 0 and it's wrong
            return False
    
        return True
    
    """
    Filters getter and setter methods.
    
    """
    def get_filter(self, filter_name):
        self.read() #get latest updates
        try:
            return self.config["FILTERS"][filter_name] 
        except IndexError:
            return #just a wrong key
    
    #set a boolean value to a filter
    def set_filter(self, filter_name, value):
        try:
            if value:
                self.config["FILTERS"][filter_name] = "1"
            else:
                self.config["FILTERS"][filter_name] = "0"
            
            #write to config file
            with open(self.file_name, 'w') as f:
                self.config.write(f)
            
            self.read() #update the config object
        except IndexError:
            return #just a wrong key
             
             
"""
Get api id from credentials.ini file

"""
def get_api_id():
    try:
        return int(credentials['API_CREDS']['API_ID'])
    except IndexError:
        raise RuntimeError("Invalid credential configuration file, visit https://github.com/AryanGHM/telegram-gp-bot for more information.")

"""
Get api hash from credentials.ini file

"""
def get_api_hash():
    try:
        return credentials['API_CREDS']['API_HASH']
    except IndexError:
        raise RuntimeError("Invalid credential configuration file, visit https://github.com/AryanGHM/telegram-gp-bot for more information.")

"""
Get bot token from credentials.ini file

"""
def get_bot_token():
    try:
        return credentials['BOT_CREDS']['BOT_TOKEN']
    except IndexError:
        raise RuntimeError("Invalid credential configuration file, visit https://github.com/AryanGHM/telegram-gp-bot for more information.")

"""
Read the GroupPrefs folder for any group preferences 
Designed to only be called from "main.py" file in the
project's root directory.

Returns a list of tuples each of which 

"""
def recover_sess():
    CHATS = []
    
    #crawl the whole GroupPrefs directory
    for f in os.listdir('GroupPrefs'):
        if f.endswith('.grprf'):
            #create a tuple with it's name and a GroupPrefs object of it
            f = f.replace('.grprf', '')
            prefs = GroupPrefs(f)
            #create a list of all group preferences and names
            CHATS.append((f, prefs))
    
    return CHATS