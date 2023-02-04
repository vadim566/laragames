<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentLemma
{
    public $ContentLemmaID;
    public $ContentID;
    public $LemmaOrder;
    public $EntryInL1;
    public $EntryInL2;
    public $Frequency;
    public $Notes;

    static function insertContentLemmas($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table ContentLemmas
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,LemmaOrder,EntryInL1,EntryInL2,Frequency,Notes)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function updateContentLemmas($contentFileName, $tmpTableName, $justNote)
    {
        $updateQuery = "create temporary table " . $tmpTableName . "  LIKE ContentLemmas";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "load data local infile '$contentFileName' into table $tmpTableName
                            fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentLemmaID,ContentID,LemmaOrder,EntryInL1,EntryInL2,Frequency,Notes)";
        PdoDataAccess::runquery($updateQuery);

        $onDuplicateUpdate = $justNote ? " Notes = tmpTable.Notes" : " EntryInL1 = tmpTable.EntryInL1, Notes = tmpTable.Notes";
        $updateQuery = "insert into ContentLemmas
                            select * from " . $tmpTableName . " tmpTable
                                on duplicate key update " . $onDuplicateUpdate;
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "drop temporary table " . $tmpTableName ;
        PdoDataAccess::runquery($updateQuery);
        return true;
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentLemmas", "ContentLemmaID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentLemmas", $where, $whereParams);
    }

    static function SearchContentLemma($where = "", $whereParam = array(), $pageNo = -1)
    {
        $query = "select cl.*, cle.examples 
                    from ContentLemmas cl
                    left join(
                        select ContentID, LemmaOrder, group_concat(ExampleText separator '\n') examples
	                      from ContentLemmaExamples  group by ContentID , LemmaOrder) cle 
                    on (cle.ContentID = cl.ContentID and cl.LemmaOrder = cle.LemmaOrder) ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if($pageNo != -1)
            $query .= " order by cl.EntryInL2 limit " . ($pageNo - 1) * RowPerPage . "," . RowPerPage;

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function SelectForCSV($where = "", $whereParam = array())
    {
        $query = "select EntryInL2, EntryInL1, Notes 
                    from ContentLemmas ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function NumberOfPages($contentID)
    {
        $query = "select count(*) from ContentLemmas where ContentID = :contentID";
        $whereParam[":contentID"] = $contentID;

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $totalRecord = $temp[0][0];
        $numberOfPages = ceil($totalRecord / RowPerPage);
        return $numberOfPages;
    }
}
