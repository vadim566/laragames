<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentLemmaExample
{
    public $ContentLemmaExampleID;
    public $ContentID;
    public $LemmaOrder;
    public $ExampleText;

    static function insertContentLemmaExamples($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table ContentLemmaExamples
                            fields optionally enclosed by '\"' 
                            terminated by '\t'                            
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,LemmaOrder,ExampleText)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentLemmaExamples", "ContentLemmaExampleID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentLemmaExamples", $where, $whereParams);
    }
}
?>
