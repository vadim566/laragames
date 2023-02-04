<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class MultiWordLexiconTransform
{
    public $MultiWordLexiconTransformID;
    public $LanguageID;
    public $TransformMember;

    static function insertMultiWordLexiconTransforms($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table MultiWordLexiconTransforms
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (LanguageID,TransformMember)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function updateMultiWordLexiconTransforms($contentFileName, $tmpTableName)
    {
        $updateQuery = "create temporary table " . $tmpTableName . "  LIKE MultiWordLexiconTransforms";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "load data local infile '$contentFileName' into table $tmpTableName
                            fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (MultiWordLexiconTransformID,LanguageID,TransformMember)";
        PdoDataAccess::runquery($updateQuery);

        $onDuplicateUpdate = " TransformMember = tmpTable.TransformMember";
        $updateQuery = "insert into MultiWordLexiconTransforms
                            select * from " . $tmpTableName . " tmpTable
                                on duplicate key update " . $onDuplicateUpdate;
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "drop temporary table " . $tmpTableName ;
        PdoDataAccess::runquery($updateQuery);
        return true;
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("MultiWordLexiconTransforms", "MultiWordLexiconTransformID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("MultiWordLexiconTransforms", $where, $whereParams);
    }

    static function SearchMultiWordLexiconTransform($where = "", $whereParam = array(), $pageNo = -1)
    {
        $query = "select * from MultiWordLexiconTransforms ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if($pageNo != -1)
            $query .= " order by MultiWordLexiconTransformID limit " . ($pageNo - 1) * RowPerPage . "," . RowPerPage;

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function SelectForCSV($where = "", $whereParam = array())
    {
        $query = "select TransformMember
                    from MultiWordLexiconTransforms ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function NumberOfPages($languageID)
    {
        $query = "select count(*) from MultiWordLexiconTransforms where LanguageID = :languageID";
        $whereParam[":languageID"] = $languageID;

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $totalRecord = $temp[0][0];
        $numberOfPages = ceil($totalRecord / RowPerPage);
        return $numberOfPages;
    }
}
