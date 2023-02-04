<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 16.11.2020
 * Time: 10:50
 */


require_once '../SharedModules/PdoDataAccess.class.php';

$tmpTableName = "430_" . date("Ymd_His");
$updateQuery = "create temporary table " . $tmpTableName . "  LIKE ContentTypes";
PdoDataAccess::runquery($updateQuery);
$updateQuery = "load data local infile 'merged-csv.csv' into table $tmpTableName
                            fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentTypeID,ContentID,TypeOrder,EntryInL1,EntryInL2,Frequency,RecordingFileName)";
PdoDataAccess::runquery($updateQuery);
$updateQuery = "insert into ContentTypes
                            select * from " . $tmpTableName . " tmpTable
                                on duplicate key update EntryInL1 = tmpTable.EntryInL1";
PdoDataAccess::runquery($updateQuery);
$updateQuery = "drop temporary table " . $tmpTableName ;
PdoDataAccess::runquery($updateQuery);
return true;