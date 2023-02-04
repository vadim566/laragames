# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 13:27:40 2021

@author: hsterikova, mannyrayner
"""

import lara_utils

# The config file needs to be at the location defined by _database_config_file
# Its contents will depend on the machine and should look something like this:
#
# {   "host": "127.0.0.1",
#     "user": "laraportaluser",
#     "password": "v8jfr3RmhY6Htapd",
#     "database": "LARA-portal-stage"
#	}
#	
# If you aren't using a database, just omit the config file

_database_config_file = '$LARA/Code/Python/database_config.json'

# If there is no config file, or it contains bad data, this prints a warning and returns False
def read_database_config_file():
    try:
        if not lara_utils.file_exists(_database_config_file):
            lara_utils.print_and_flush(f'*** Warning: unable to find database config file {_database_config_file}')
            return False
        ConfigData = lara_utils.read_json_file(_database_config_file)
        if ConfigData == False:
            lara_utils.print_and_flush(f'*** Warning: unable to read database config file {_database_config_file} as JSON')
            return False
        else:
            return { 'host': ConfigData['host'],
                     'user': ConfigData['user'],
                     'password': ConfigData['password'],
                     'database': ConfigData['database']
                 }
    except Exception as e:
            lara_utils.print_and_flush(f'*** Warning: something went wrong when reading database config file {_database_config_file}')
            lara_utils.print_and_flush(str(e))
            return False

def get_all_flashcard_db_data(UserId, ContentId):
    try:
        return get_all_flashcard_db_data_main(UserId, ContentId)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: something went wrong when trying to read database information')
        lara_utils.print_and_flush(str(e))
        return []

def get_all_flashcard_db_data_main(UserId, ContentId):
    # Import mysql.connector inside this function so that we can recover in case it's not there
    import mysql.connector
    ConfigData = read_database_config_file()
    # If there is no config file, or it contains bad data, return an empty list
    if ConfigData == False:
        return []
    mydb = mysql.connector.connect(
        host=ConfigData['host'],
        user=ConfigData['user'],
        password=ConfigData['password'],
        database=ConfigData['database']
        )
    # print(mydb)
    mycursor = mydb.cursor()
    
    SQLcall = ("SELECT stu.UserID, c.ContentID, c.ContentName, l.LanguageName, r.FlashcardsSetID, r.FlashcardNo, fcs.FlashcardType, q.FlashcardContent question, a.FlashcardContent answer, " 
               + "IF(a.FlashcardPart = 'answer', 'correct', 'incorrect') AS answerStatus "
               + "FROM FlashcardsSets fcs "
               + "LEFT JOIN FlashcardResponses r ON (r.FlashcardsSetID = fcs.FlashcardsSetID) "                 
               + "LEFT JOIN FlashcardSetMembers q ON (q.FlashcardsSetID = r.FlashcardsSetID AND q.FlashcardNo = r.FlashcardNo AND q. FlashcardPart = 'question') "
               + "LEFT JOIN FlashcardSetMembers a ON (a.FlashcardSetMemberID = r.FlashcardSetMemberID) "
               + f"LEFT JOIN Contents c ON (c.ContentID = fcs.ContentID AND c.ContentID = {ContentId} ) "
               + "LEFT JOIN Accounts stu ON (fcs.TestCreatorID = stu.UserID) "
               + "LEFT JOIN Languages l ON (c.L2ID = l.LanguageID) "
               + "WHERE a.FlashcardContent IS NOT null "
               + f"AND stu.UserID = {UserId} "
               + "ORDER BY r.FlashcardsSetID, r.FlashcardNo, FlashcardResponseID")
    
    lara_utils.print_and_flush(f'*** DEBUG: database called with following parameters: ')
    lara_utils.print_and_flush(SQLcall)
    
    mycursor.execute(SQLcall)
    
    RawDBData = mycursor.fetchall()
    mydb.close()
    return clean_data_from_mysql(RawDBData)

# this function cleans the data from database 
def clean_data_from_mysql(RawDBData):
    data = list()
    for item_tuple in RawDBData:
        new_item = list(item_tuple)
        x = new_item[7].decode()
        new_item[7] = x
        y = new_item[8].decode()
        new_item[8] = y
        data.insert(-1, new_item)
    return(data)

# myresult = get_all_flashcard_db_data(UserId, ContentId)




