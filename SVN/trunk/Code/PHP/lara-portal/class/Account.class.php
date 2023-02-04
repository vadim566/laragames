<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */

require_once '../SharedModules/PdoDataAccess.class.php';

class Account
{

    public $UserID;
    public $UserName;
    public $Email;
    public $Password;
    public $PasswordSalt;

    static function LdtUserDropBox($headerInfo, $dropBoxName, $selectedID = -1)
    {
        $url = 'https://regulus.unige.ch/litedevtools/server/api/account/allUsers';

        $header = [
            "Authorization: " . $headerInfo
        ];

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
        curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
        curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
        curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
        curl_setopt($ch, CURLOPT_TIMEOUT, 100);

        $result = curl_exec ($ch);

        if ($result === FALSE) {
            curl_close($ch);
            return "something wrong here";
        }

        $ldtUsers = json_decode($result, true);
        asort($ldtUsers, SORT_STRING | SORT_FLAG_CASE | SORT_NATURAL);
        $ldtUsersKeys = array_keys($ldtUsers);

        $retStr = "<select name=$dropBoxName id=$dropBoxName>";
        $retStr .= "<option value=-1";
        if($selectedID == -1)
            $retStr .= " selected ";
        $retStr .= ">Anonymous</option>";

        for ($i = 0; $i < count($ldtUsers); $i++) {
            $retStr .= "<option value='" . $ldtUsersKeys[$i] . "'";
            if($ldtUsersKeys[$i] == $selectedID)
                $retStr .= " selected ";
            $retStr .= " >";
            $retStr .= $ldtUsers[$ldtUsersKeys[$i]];
            $retStr .= "</option>";
        }

        $retStr .= "</select>";
        curl_close($ch);
        return $retStr;
    }

    static function GetLdtUserName($headerInfo, $userID)
    {

        $url = 'https://regulus.unige.ch/litedevtools/server/api/account/userName/' . $userID;


        $header = [
            "Authorization: " . $headerInfo
        ];

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
        curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
        curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
        curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
        curl_setopt($ch, CURLOPT_TIMEOUT, 100);

        $result = curl_exec ($ch);


        if ($result === FALSE) {
            curl_close($ch);
            return "something wrong here";
        }
        else
        {
            curl_close($ch);
            return substr($result, 1, strlen($result)-2);
        }
    }

    static function GetLdtUserID($headerInfo, $userName)
    {
        $ch = curl_init();

        $uName = curl_escape($ch, $userName);

        $url = 'https://regulus.unige.ch/litedevtools/server/api/account/userId/' . $uName;
        $header = [
            "Authorization: " . $headerInfo
        ];

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
        curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
        curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
        curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
        curl_setopt($ch, CURLOPT_TIMEOUT, 100);

        $result = curl_exec ($ch);

        if ($result === FALSE) {
            curl_close($ch);
            return "something wrong here";
        }
        else
        {
            curl_close($ch);
            return substr($result, 1, strlen($result)-2);
        }
    }

    static function UserLogin($where, $whereParam)
    {
        $query = "select * from Accounts where " . $where;
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp;
    }

    function insert()
    {
        PdoDataAccess::insert("Accounts", $this);
    }

    function update()
    {
        $whereParams[":userID"] = $this->UserID;
        PdoDataAccess::update("Accounts", $this, "UserID=:userID", $whereParams);
    }

    function checkDuplication()
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

    static function GetUserName($UserID)
    {
        $query = "select UserName from Accounts where UserID = :userID";
        $whereParam = array(":userID" => $UserID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp[0]["UserName"];
    }

    function updatePassword()
    {
        $whereParams[":email"] = $this->Email;
        return PdoDataAccess::update("Accounts", $this, "Email=:email", $whereParams);
    }

    static function EmailExists($email)
    {
        $query = "select count(*) from Accounts where lower(Email) = lower(:email)";
        $whereParam[":email"] = $email;
        $temp = PdoDataAccess::runquery($query, $whereParam);
        if($temp[0][0] == 0){
            return false;
        }
        return true;
    }

    static function SearchUser($where = "", $whereParam = array())
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
