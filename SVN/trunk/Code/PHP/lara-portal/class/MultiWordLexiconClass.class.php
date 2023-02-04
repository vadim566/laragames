<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class MultiWordLexiconClass
{
    public $MultiWordLexiconClassID;
    public $LanguageID;
    public $ClassID;
    public $ClassHeader;
    public $ClassMember;

    static function insertMultiWordLexiconClasses($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table MultiWordLexiconClasses
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (LanguageID,ClassID,ClassHeader,ClassMember)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function updateMultiWordLexiconClasses($contentFileName, $tmpTableName)
    {
        $updateQuery = "create temporary table " . $tmpTableName . "  LIKE MultiWordLexiconClasses";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "load data local infile '$contentFileName' into table $tmpTableName
                            fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (MultiWordLexiconClassID,LanguageID,ClassID,ClassHeader,ClassMember)";
        PdoDataAccess::runquery($updateQuery);

        $onDuplicateUpdate = " ClassMember = tmpTable.ClassMember";
        $updateQuery = "insert into MultiWordLexiconClasses
                            select * from " . $tmpTableName . " tmpTable
                                on duplicate key update " . $onDuplicateUpdate;
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "drop temporary table " . $tmpTableName ;
        PdoDataAccess::runquery($updateQuery);
        return true;
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("MultiWordLexiconClasses", "MultiWordLexiconClassID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("MultiWordLexiconClasses", $where, $whereParams);
    }

    static function SearchMultiWordLexiconClass($where = "", $whereParam = array(), $pageNo = -1)
    {
        $query = "select LanguageID, ClassID, ClassHeader, 
                            group_concat(MultiWordLexiconClassID separator '**') MembersIDs,
                            group_concat(ClassMember separator '**') MembersValues from MultiWordLexiconClasses ";
        $query .= (!empty($where)) ? " where " . $where : "";
        $query .= " group by  LanguageID, ClassID, ClassHeader";

        if($pageNo != -1)
            $query .= " order by ClassID limit " . ($pageNo - 1) * RowPerPage . "," . RowPerPage;

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function SelectForCSV($where = "", $whereParam = array())
    {
        $query = "select ClassID, ClassHeader, ClassMember 
                    from MultiWordLexiconClasses ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function NumberOfPages($languageID)
    {
        $query = "select count(distinct(ClassID)) from MultiWordLexiconClasses where LanguageID = :languageID";
        $whereParam[":languageID"] = $languageID;

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $totalRecord = $temp[0][0];
        $numberOfPages = ceil($totalRecord / RowPerPage);
        return $numberOfPages;
    }
}
