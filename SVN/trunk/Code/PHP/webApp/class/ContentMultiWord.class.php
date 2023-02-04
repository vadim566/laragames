<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentMultiWord
{
    public $ContentMWID;
    public $ContentID;
    public $MultiWordOrder;
    public $MultiWordMatch;
    public $MultiWord;
    public $MultiWordStatus;
    public $MultiWordPOS;
    public $MultiWordSkipped;

    static function insertContentMultiWords($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table ContentMultiWords
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,MultiWordOrder,MultiWordMatch,MultiWord,MultiWordStatus,MultiWordPOS,MultiWordSkipped)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function updateContentMultiWords($contentFileName, $tmpTableName)
    {
        $updateQuery = "create temporary table " . $tmpTableName . "  LIKE ContentMultiWords";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "load data local infile '$contentFileName' into table $tmpTableName
                            fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentMWID,ContentID,MultiWordOrder,MultiWordMatch,MultiWord,MultiWordStatus,MultiWordPOS,MultiWordSkipped)";
        PdoDataAccess::runquery($updateQuery);

        $onDuplicateUpdate = " MultiWordStatus = tmpTable.MultiWordStatus";
        $updateQuery = "insert into ContentMultiWords
                            select * from " . $tmpTableName . " tmpTable
                                on duplicate key update " . $onDuplicateUpdate;
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "drop temporary table " . $tmpTableName ;
        PdoDataAccess::runquery($updateQuery);
        return true;
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentMultiWords", "ContentMWID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentMultiWords", $where, $whereParams);
    }

    static function SearchContentMultiWord($where = "", $whereParam = array(), $pageNo = -1)
    {
        $query = "select * from ContentMultiWords ";
        $query .= (!empty($where)) ? " where " . $where : "";
        $query .= " order by MultiWordOrder " ;
        $query .= ($pageNo != -1) ? " limit " . ($pageNo - 1) * RowPerPage . "," . RowPerPage : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function SearchContentMultiWordForRep($where = "", $whereParam = array())
    {
        $query = "select cmw.*, entryIndex, entryChunk
                    from ContentMultiWords cmw
                  left join 
                  (select ContentID, MultiWordOrder, group_concat(MultiWordIndex SEPARATOR '@*@') as entryIndex 
                  from ContentMultiWordIndexes group by ContentID, MultiWordOrder) mwIndexes 
                    on (mwIndexes.ContentID = cmw.ContentID and mwIndexes.MultiWordOrder = cmw.MultiWordOrder)
                  left join 
                  (select ContentID, MultiWordOrder, group_concat(Concat(MultiWordChunk, '::', MultiWordChunkPOS) SEPARATOR '@*@') as entryChunk 
                  from ContentMultiWordChunks group by ContentID, MultiWordOrder) mwChunks
                    on  (mwChunks.ContentID = cmw.ContentID and mwChunks.MultiWordOrder = cmw.MultiWordOrder)";
        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function NumberOfPages($contentID)
    {
        $query = "select count(*) from ContentMultiWords where ContentID = :contentID";
        $whereParam[":contentID"] = $contentID;

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $totalRecord = $temp[0][0];
        $numberOfPages = ceil($totalRecord / RowPerPage);
        return $numberOfPages;
    }
}
