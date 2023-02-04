<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: April 2020
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class PasswordReset
{
    public $PasswordResetID;
    public $PasswordResetEmail;
    public $PasswordResetSelector;
    public $PasswordResetToken;
    public $PasswordResetExpires;

    function insert()
    {
        PdoDataAccess::insert("PasswordReset", $this);
    }

    static function SearchPasswordResetInfo($where = "", $whereParam = array())
    {
        $query = "select * from PasswordReset p
                  left join Accounts a on (p.PasswordResetEmail = a.Email)
                  where " . $where;
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp;
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("PasswordReset", $where, $whereParams);
    }
}

