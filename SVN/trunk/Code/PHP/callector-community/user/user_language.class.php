<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */

require_once '../shared-modules/PdoDataAccess.class.php';

class user_language
{
    public $UserLanguageID;
    public $UserID;
    public $LanguageID;
    public $LanguageLevel;

    function insert()
    {
        PdoDataAccess::insert("UserLanguages", $this);
    }

    function update()
    {
        $whereParams[":userLangID"] = $this->UserLanguageID;
        PdoDataAccess::update("UserLanguages", $this, "UserLanguageID=:userLangID", $whereParams);
    }

    static function search_user_languages($where = "", $whereParam = array())
    {
        $query = "select * from UserLanguages ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }
}