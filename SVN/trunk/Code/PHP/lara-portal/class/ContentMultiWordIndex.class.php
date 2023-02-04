<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentMultiWordIndex
{
    public $ContentMWIndexID;
    public $ContentID;
    public $MultiWordOrder;
    public $MultiWordIndex;

    static function insertContentMultiWordIndexes($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table ContentMultiWordIndexes
                            fields optionally enclosed by '\"' 
                            terminated by '\t'                            
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,MultiWordOrder,MultiWordIndex)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentMultiWordIndexes", "ContentMWIndexID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentMultiWordIndexes", $where, $whereParams);
    }

    static function SearchMultiWordIndex($where = "", $whereParam = array())
    {
        $query = "select * from ContentMultiWordIndexes ";
        $query .= (!empty($where)) ? " where " . $where : "";
        $query .= " order by ContentMWIndexID " ;

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }
}
?>
