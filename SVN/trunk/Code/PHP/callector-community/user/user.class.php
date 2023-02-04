<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */

require_once '../shared-modules/PdoDataAccess.class.php';

class user
{
    public $UserID;
    public $FirstName;
    public $MiddleName;
    public $LastName;
    public $DisplayName;
    public $GenderID;
    public $CountryID;
    public $BirthDate;
    public $WebsiteAddress;
    public $Interests;
    public $AboutMe;
    public $CoverPictureExtension;
    public $ProfilePictureExtension;
    public $EmailNotification;

    function insert()
    {
        return PdoDataAccess::insert("Users", $this);
    }

    function update()
    {
        $whereParams[":userID"] = $this->UserID;
        return PdoDataAccess::update("Users", $this, "UserID=:userID", $whereParams);
    }

    static function search_user($where = "", $whereParam = array())
    {
        $query = "select * from Users ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp[0];
    }

    static function user_has_profile_info($where = "", $whereParam = array())
    {
        $query = "select count(*) from Users ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        if($temp[0][0] == 0)
            return false;
        return true;
    }

}