<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */

require_once '../shared-modules/PdoDataAccess.class.php';

class account
{

    public $UserID;
    public $UserName;
    public $Email;
    public $Password;
    public $PasswordSalt;

    function insert()
    {
        PdoDataAccess::insert("Accounts", $this);
    }

    function update()
    {
        $whereParams[":userID"] = $this->UserID;
        PdoDataAccess::update("Accounts", $this, "UserID=:userID", $whereParams);
    }

    function check_duplication()
    {
        $query = "select count(*) from Accounts where UserName = :uname";
        $whereParam = array(":uname" => $this->UserName);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        if($temp[0][0] != 0){
            return "DuplicateUsername";
        }
        $query = "select count(*) from Accounts where lower(Email) = lower(:email)";
        $whereParam = array(":email" => $this->Email);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        if($temp[0][0] != 0){
            return "DuplicateEmail";
        }

        return "NoDuplication";
    }

    function update_password()
    {
        $whereParams[":email"] = $this->Email;
        return PdoDataAccess::update("Accounts", $this, "Email=:email", $whereParams);
    }

    static function email_exists($email)
    {
        $query = "select count(*) from Accounts where lower(Email) = lower(:email)";
        $whereParam[":email"] = $email;
        $temp = PdoDataAccess::runquery($query, $whereParam);
        if($temp[0][0] == 0){
            return false;
        }
        return true;
    }

    static function search_account($where = "", $whereParam = array())
    {
        $query = "select * from Accounts ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }
}