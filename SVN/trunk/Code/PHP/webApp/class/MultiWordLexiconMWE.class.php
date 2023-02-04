<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class MultiWordLexiconMWE
{
    public $MultiWordLexiconMWEID;
    public $LanguageID;
    public $MweHeader;
    public $MweName;
    public $MwePos;

    function insert()
    {
        PdoDataAccess::insert("MultiWordLexiconMWES", $this);
    }

    static function insertMultiWordLexiconMWES($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table MultiWordLexiconMWES
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (LanguageID,MweHeader,MweName,MwePos)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function updateMultiWordLexiconMWES($contentFileName, $tmpTableName)
    {
        $updateQuery = "create temporary table " . $tmpTableName . "  LIKE MultiWordLexiconMWES";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "load data local infile '$contentFileName' into table $tmpTableName
                            fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (MultiWordLexiconMWEID,LanguageID,MweHeader,MweName,MwePos)";
        PdoDataAccess::runquery($updateQuery);

        $onDuplicateUpdate = " MweName = tmpTable.MweName, MwePos = tmpTable.MwePos";
        $updateQuery = "insert into MultiWordLexiconMWES
                            select * from " . $tmpTableName . " tmpTable
                                on duplicate key update " . $onDuplicateUpdate;
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "drop temporary table " . $tmpTableName ;
        PdoDataAccess::runquery($updateQuery);
        return true;
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("MultiWordLexiconMWES", "MultiWordLexiconMWEID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("MultiWordLexiconMWES", $where, $whereParams);
    }

    static function SearchMultiWordLexiconMWE($where = "", $whereParam = array(), $pageNo = -1)
    {
        $query = "select * from MultiWordLexiconMWES ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if($pageNo != -1)
            $query .= " order by MweHeader limit " . ($pageNo - 1) * RowPerPage . "," . RowPerPage;

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function SelectForCSV($where = "", $whereParam = array())
    {
        $query = "select MweHeader, MweName, MwePos 
                    from MultiWordLexiconMWES ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function NumberOfPages($languageID)
    {
        $query = "select count(*) from MultiWordLexiconMWES where LanguageID = :languageID";
        $whereParam[":languageID"] = $languageID;

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $totalRecord = $temp[0][0];
        $numberOfPages = ceil($totalRecord / RowPerPage);
        return $numberOfPages;
    }
}
