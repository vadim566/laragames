<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentType
{
    public $ContentTypeID;
    public $ContentID;
    public $TypeOrder;
    public $EntryInL1;
    public $EntryInL2;
    public $Frequency;
    public $RecordingFileName;

    static function insertContentTypes($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table ContentTypes
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,TypeOrder,EntryInL1,EntryInL2,Frequency,RecordingFileName)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function updateContentTypes($contentFileName, $tmpTableName)
    {
        $updateQuery = "create temporary table " . $tmpTableName . "  LIKE ContentTypes";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "load data local infile '$contentFileName' into table $tmpTableName
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
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentTypes", "ContentTypeID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentTypes", $where, $whereParams);
    }

    static function SearchContentType($where = "", $whereParam = array(), $pageNo = -1)
    {
        $query = "select ct.*, cte.examples 
                    from ContentTypes ct
                    left join(
                        select ContentID, TypeOrder, group_concat(ExampleText separator '\n') examples
	                      from ContentTypeExamples  group by ContentID , TypeOrder) cte 
                    on (cte.ContentID = ct.ContentID and ct.TypeOrder = cte.TypeOrder) ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if($pageNo != -1)
            $query .= " order by ct.Frequency desc limit " . ($pageNo - 1) * RowPerPage . "," . RowPerPage;

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function SelectForCSV($where = "", $whereParam = array())
    {
        $query = "select EntryInL2, EntryInL1 
                    from ContentTypes ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function NumberOfPages($contentID)
    {
        $query = "select count(*) from ContentTypes where ContentID = :contentID";
        $whereParam[":contentID"] = $contentID;

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $totalRecord = $temp[0][0];
        $numberOfPages = ceil($totalRecord / RowPerPage);
        return $numberOfPages;
    }
}