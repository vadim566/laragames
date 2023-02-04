<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentTypeExample
{
    public $ContentTypeExampleID;
    public $ContentID;
    public $TypeOrder;
    public $ExampleText;

    static function insertContentTypeExamples($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table ContentTypeExamples
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,TypeOrder,ExampleText)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentTypeExamples", "ContentTypeExampleID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentTypeExamples", $where, $whereParams);
    }
}
?>
