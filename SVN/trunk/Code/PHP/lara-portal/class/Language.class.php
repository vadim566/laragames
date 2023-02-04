<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/17/2019
 * Time: 02:38 PM
 */

require_once __DIR__ . '/../SharedModules/PdoDataAccess.class.php';


class Language
{

    public $LanguageID;
    public $LanguageName;
    public $TreeTagger;

    static function LanguageDropBox($dropBoxName, $hasExtraRow, $selectedID = -1)
    {
        $retStr = "<select name=$dropBoxName id=$dropBoxName>";
        if($hasExtraRow)
        {
            $retStr .= "<option value=-1 ";
            if($selectedID == -1)
                $retStr .= " selected ";
            $retStr .= ">---</option>";
        }

        $query = "select * from Languages order by LanguageName";
        $temp = PdoDataAccess::runquery($query);
        for($i=0; $i<count($temp); $i++)
        {
            $retStr .= "<option value='" . $temp[$i]["LanguageID"] . "'" ;
            if($temp[$i]["LanguageID"] == $selectedID)
                $retStr .= " selected ";
            $retStr .= " >";
            $retStr .= $temp[$i]["LanguageName"];
            $retStr .= "</option>";
        }

        $retStr .= "</select>";
        return $retStr;
    }

    static function hasTreeTagger($langID = "")
    {
        $query = "select TreeTagger from Languages where LanguageID = :langID";
        $whereParam = array(":langID" => $langID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp[0]["TreeTagger"];
    }

    static function getLanguageName($langID = "")
    {
        $query = "select lower(LanguageName) from Languages where LanguageID = :langID";
        $whereParam = array(":langID" => $langID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp[0][0];
    }

    static function getLanguageID($langName = "")
    {
        $query = "select LanguageID from Languages where LanguageName = :langName";
        $whereParam = array(":langName" => $langName);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp[0][0];
    }

    static function getListOfLanguages()
    {
        $query = "select LanguageID, LanguageName from Languages where HasMweLexicon = 'YES' order by LanguageName";
        $temp = PdoDataAccess::runquery($query);
        return $temp;
    }

    static function UpdateMweLexiconStatus($languageID)
    {
        $query = "update Languages set HasMweLexicon = 'YES' where LanguageID = :id";
        $whereParam = array(":id" => $languageID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp;
    }

    static function isRightToLeft($langID = "")
    {
        $query = "select IsRightToLeft from Languages where LanguageID = :langID";
        $whereParam = array(":langID" => $langID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp[0]["IsRightToLeft"];
    }
}
?>