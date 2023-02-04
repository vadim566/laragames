<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/17/2019
 * Time: 02:38 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';


class ContentSegment
{

    public $ContentSegmentID;
    public $ContentID;
    public $SegmentInL1;
    public $SegmentInL2;
    public $SegmentOrder;
    public $RecordingFileName;

    static function insertContentSegments($insertFile)
    {
        $insertQuery = "load data local infile '$insertFile' into table ContentSegments
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,SegmentInL1,SegmentInL2,SegmentOrder,RecordingFileName)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function updateContentSegments($contentFileName, $tmpTableName)
    {
        $updateQuery = "create temporary table " . $tmpTableName . "  LIKE ContentSegments";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "load data local infile '$contentFileName' into table $tmpTableName
                            fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentSegmentID,ContentID,SegmentInL1,SegmentInL2,SegmentOrder,RecordingFileName)";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "insert into ContentSegments
                            select * from " . $tmpTableName . " tmpTable
                                on duplicate key update SegmentInL1 = tmpTable.SegmentInL1";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "drop temporary table " . $tmpTableName ;
        PdoDataAccess::runquery($updateQuery);
        return true;
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentSegments", "ContentSegmentID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentSegments", $where, $whereParams);
    }

    static function SearchContentSegment($where = "", $whereParam = array(), $pageNo = -1)
    {
        $query = "select * from ContentSegments ";
        $query .= (!empty($where)) ? " where " . $where : "";
        if($pageNo != -1)
            $query .= " order by SegmentOrder limit " . ($pageNo - 1) * RowPerPage . "," . RowPerPage;

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function NumberOfPages($contentID)
    {
        $query = "select count(*) from ContentSegments where ContentID = :contentID";
        $whereParam[":contentID"] = $contentID;

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $totalRecord = $temp[0][0];
        $numberOfPages = ceil($totalRecord / RowPerPage);
        return $numberOfPages;
    }
}