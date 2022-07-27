
import lara_utils
import sqlite3
from contextlib import closing
import time

_real_db_file = "dbtest.db"

_json_file = "$LARA/tmp/dbtest.json"

_memory_db_file = ":memory:"

def do_db_json_test(N, NTimes):
    lara_utils.print_and_flush(f'\n--- Using SQL table in file\n')
    do_db_test(N, NTimes, _real_db_file)
    lara_utils.print_and_flush(f'\n--- Using SQL table in memory\n')
    do_db_test(N, NTimes, _memory_db_file)
    lara_utils.print_and_flush(f'\n--- Using dict in plain JSON file\n')
    do_json_file_test(N, NTimes, _json_file)

def do_db_test(N, NTimes, DBFile):
    Dict = make_test_dict(N)
    with closing(sqlite3.connect(DBFile)) as connection:
        with closing(connection.cursor()) as cursor:
            delete_test_table(cursor)
            make_test_table(cursor)
            insert_dict_in_db(Dict, cursor)
            update_dict_in_db(Dict, cursor, NTimes)
            read_data_from_db_single_operation(cursor, NTimes)
            read_data_from_db_multiple_operations(cursor, Dict, NTimes)
            delete_test_table(cursor)

def do_json_file_test(N, NTimes, JSONFile):
    Dict = make_test_dict(N)
    insert_dict_in_json_file(Dict, JSONFile)
    update_dict_in_json_file(Dict, JSONFile, NTimes)
    read_data_from_json_file_single_operation(JSONFile, NTimes)
    read_data_from_json_file_multiple_operations(JSONFile, Dict, NTimes)

## Make a dict with N entries
def make_test_dict(N):
    Dict = {}
    for I in range(0, N):
        Key = f'key_{I}'
        Value = f'value_{I}'
        Dict[Key] = Value
    return Dict

## Add a SQL table called 'test'
def make_test_table(cursor):
    StartTime = time.time()
    cursor.execute("CREATE TABLE test (key TEXT PRIMARY KEY, value TEXT)")
    lara_utils.print_and_flush_with_elapsed_time(f'Created DB table', StartTime)

## Delete the SQL table called 'test'
def delete_test_table(cursor):
    StartTime = time.time()
    try:
        cursor.execute("DROP TABLE test")
        lara_utils.print_and_flush_with_elapsed_time(f'Deleted DB table', StartTime)
    except Exception as e:
        lara_utils.print_and_flush(f'Unable to delete test table, probably it wasn\'t there')

## Insert all the key/value pairs in Dict into the SQL table
def insert_dict_in_db(Dict, cursor):
    StartTime = time.time()
    for Key in Dict:
        Value = Dict[Key]
        cursor.execute("INSERT INTO test VALUES (?, ?)",
                       ( Key, Value ))
    lara_utils.print_and_flush_with_elapsed_time(f'Added dict to DB ({len(Dict)} rows)', StartTime)

## Write out the Dict to a JSON file
def insert_dict_in_json_file(Dict, JSONFile):
    StartTime = time.time()
    lara_utils.write_json_to_file(Dict, JSONFile)
    lara_utils.print_and_flush_with_elapsed_time(f'Written dict to JSON file ({len(Dict)} rows)', StartTime)

## Update all the values in the SQL table from Dict
def update_dict_in_db(Dict, cursor, NTimes):
    StartTime = time.time()
    for I in range(0, NTimes):
        for Key in Dict:
            Value = Dict[Key]
            cursor.execute("UPDATE test SET value = ? WHERE key = ?",
                           ( Value, Key ))
    print_and_flush_with_average_elapsed_time(f'Updated dict in DB ({len(Dict)} rows)', StartTime, NTimes)

## Update all the values in the JSON file from the Dict
def update_dict_in_json_file(Dict, JSONFile, NTimes):
    StartTime = time.time()
    for I in range(0, NTimes):
        OldDict = lara_utils.read_json_file(JSONFile)
        for Key in Dict:
            Value = Dict[Key]
            OldDict[Key] = Value
        lara_utils.write_json_to_file(OldDict, JSONFile)
    print_and_flush_with_average_elapsed_time(f'Updated dict in DB ({len(Dict)} rows)', StartTime, NTimes)

## Fetch all the records from the SQL table in one operation
def read_data_from_db_single_operation(cursor, NTimes):
    StartTime = time.time()
    for I in range(0, NTimes):
        rows = cursor.execute("SELECT key, value FROM test").fetchall()
    print_and_flush_with_average_elapsed_time(f'Read dict from DB in single operation ({len(rows)} rows)', StartTime, NTimes)

## Read in the JSON file
def read_data_from_json_file_single_operation(JSONFile, NTimes):
    StartTime = time.time()
    for I in range(0, NTimes):
        Dict = lara_utils.read_json_file(JSONFile)
    print_and_flush_with_average_elapsed_time(f'Read dict from JSON file in single operation ({len(Dict)} rows)', StartTime, NTimes)

## Read all the data from the SQL table in multiple operations (i.e. one per key)
def read_data_from_db_multiple_operations(cursor, Dict, NTimes):
    StartTime = time.time()
    for I in range(0, NTimes):
        list_of_rows = [ cursor.execute("SELECT key, value FROM test WHERE key = ?",
                                        (Key,),
                                        ).fetchall() for
                         Key in Dict ]
    print_and_flush_with_average_elapsed_time(f'Read dict from DB in multiple operations ({len(Dict)} rows)', StartTime, NTimes)

## Read all the data from JSON file in multiple operations (i.e. one per key)
def read_data_from_json_file_multiple_operations(JSONFile, Dict, NTimes):
    StartTime = time.time()
    for I in range(0, NTimes):
        NewDict = lara_utils.read_json_file(JSONFile)
        ReadContent = { Key: NewDict[Key] for Key in Dict }
    print_and_flush_with_average_elapsed_time(f'Read dict from JSON file in multiple operations ({len(Dict)} rows)', StartTime, NTimes)
    return ReadContent

_encodingError = '(... unable to write out message ...)'

def print_and_flush_with_average_elapsed_time(Message, StartTime, NTimes):
    try:
        AverageElapsedTime = ( time.time() - StartTime ) / NTimes
        MessageWithTiming = f'{Message} ({AverageElapsedTime:.3} secs over {NTimes} results)'
        print(MessageWithTiming, flush=True)
    except:
        print(_encodingError)

