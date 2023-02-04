<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 10/7/2019
 * Time: 12:42 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';


class FlashcardsSet
{
    public $FlashcardsSetID;
    public $ContentID;
    public $TestCreatorID;
    public $TestDate;
    public $NumberOfTests;
    public $FlashcardType;
    public $FlashcardLevel;
    public $FlashcardWordType;


    function insert()
    {
        PdoDataAccess::insert("FlashcardsSets", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("FlashcardsSets", "FlashcardsSetID", $where, $whereParams);
    }

    static function selectContentWebAddress($where, $whereParam)
    {
        $query = "select WebAddress from FlashcardsSets f
                  left join Contents c on (f.ContentID = c.ContentID) ";

        $query .= (!empty($where)) ? " where " . $where : "";
        $query .= " order by TestDate desc limit 1";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        $homePageAddress = $temp[0]["WebAddress"];
        $url = explode('/', $homePageAddress);
        array_pop($url);
        return implode('/', $url) . "/multimedia/";
    }

    static function selectContextStatus($where, $whereParam)
    {
        $query = "select ShowTextContext, ShowMultimediaContext from FlashcardsSets f
                  left join Contents c on (f.ContentID = c.ContentID) ";

        $query .= (!empty($where)) ? " where " . $where : "";
        $query .= " order by TestDate desc limit 1";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp[0];
    }

    static function FlashcardContentDropBox($dropBoxName)
    {
        $retStr = "<select name = $dropBoxName id = $dropBoxName>";
        $retStr .= "<option value=-1>---</option>";

        $query = "select distinct f.ContentID, c.ContentName FROM FlashcardsSets f
                    left join Contents c on (f.ContentID = c.ContentID) 
                    where IsDeleted = 'NO' order by ContentName";
        $temp = PdoDataAccess::runquery($query);
        for($i = 0; $i < count($temp); $i++)
            $retStr .= "<option value='" . $temp[$i]["ContentID"] . "'>" . $temp[$i]["ContentName"] . "</option>";

        $retStr .= "</select>";
        return $retStr;
    }

    static function SearchFlashcardLogs($where = "", $whereParam = array())
    {
        $query = "SELECT FlashcardsSetID, TestDate, UserName FROM FlashcardsSets f 
                    left join Accounts a on (f.TestCreatorID = a.UserID) ";
        $query .= (!empty($where)) ?  $where : "";
        $query .= " order by UserName asc, FlashcardsSetID desc";
        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function GetLastFlashcardID($where = "", $whereParam = array())
    {
        $query = "SELECT max(FlashcardsSetID) FROM FlashcardsSets  ";
        $query .= (!empty($where)) ? $where : "";

        if (!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        if (count($temp) == 0)
            return -1;
        return $temp[0][0];
    }

    static function GetFlashcardType($setID = "")
    {
        $query = "SELECT FlashcardType FROM FlashcardsSets where setID = :setID";
        $whereParam = array(":setID" => $setID);
        $temp = PdoDataAccess::runquery($query, $whereParam);

        if(count($temp) == 0)
            return -1;
        return $temp[0][0];
    }
}