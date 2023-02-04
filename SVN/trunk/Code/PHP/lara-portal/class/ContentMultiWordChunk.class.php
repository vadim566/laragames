<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentMultiWordChunk
{
    public $ContentMWChunkID;
    public $ContentID;
    public $MultiWordOrder;
    public $MultiWordChunk;
    public $MultiWordChunkPOS;

    static function insertContentMultiWordChunks($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table ContentMultiWordChunks
                            fields optionally enclosed by '\"' 
                            terminated by '\t'                            
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,MultiWordOrder,MultiWordChunk,MultiWordChunkPOS)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentMultiWordChunks", "ContentMWChunkID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentMultiWordChunks", $where, $whereParams);
    }

    static function SearchMultiWordChunk($where = "", $whereParam = array())
    {
        $query = "select * from ContentMultiWordChunks ";
        $query .= (!empty($where)) ? " where " . $where : "";
        $query .= " order by ContentMWChunkID " ;

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

}
?>
