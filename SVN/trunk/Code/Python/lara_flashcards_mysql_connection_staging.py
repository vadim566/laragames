# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 13:27:40 2021

@author: hsterikova
"""

import mysql.connector

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="laraportaluser",
    password="v8jfr3RmhY6Htapd",
    database="LARA-portal-stage"
    )

# print(mydb)

mycursor = mydb.cursor()
mycursor.execute("SELECT stu.UserName, c.ContentID, c.ContentName, l.LanguageName, r.FlashcardsSetID, r.FlashcardNo, fcs.FlashcardType, q.FlashcardContent question, a.FlashcardContent answer, " 
                 "IF(a.FlashcardPart = 'answer', 'correct', 'incorrect') AS answerStatus "
                 "FROM FlashcardsSets fcs "
                 "LEFT JOIN FlashcardResponses r ON (r.FlashcardsSetID = fcs.FlashcardsSetID) "                 
                 "LEFT JOIN FlashcardSetMembers q ON (q.FlashcardsSetID = r.FlashcardsSetID AND q.FlashcardNo = r.FlashcardNo AND q. FlashcardPart = 'question') "
                 "LEFT JOIN FlashcardSetMembers a ON (a.FlashcardSetMemberID = r.FlashcardSetMemberID) "
                 "LEFT JOIN Contents c ON (c.ContentID = fcs.ContentID) "
                 "LEFT JOIN Accounts stu ON (fcs.TestCreatorID = stu.UserID) "
                 "LEFT JOIN Languages l ON (c.L2ID = l.LanguageID) "
                 "WHERE a.FlashcardContent IS NOT null "
                 "ORDER BY r.FlashcardsSetID, r.FlashcardNo, FlashcardResponseID")
myresult = mycursor.fetchall()

# this function cleans the data from database 
def get_clean_data_from_mysql():
    data = list()
    for item_tuple in myresult:
        new_item = list(item_tuple)
        x = new_item[7].decode()
        new_item[7] = x
        y = new_item[8].decode()
        new_item[8] = y
        data.insert(-1, new_item)
    return(data)

mydb.close()

