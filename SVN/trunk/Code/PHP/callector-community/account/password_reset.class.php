<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */

require_once ROOT . '/shared-modules/PdoDataAccess.class.php';

class password_reset
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

    static function search_password_reset_info($where = "", $whereParam = array())
    {
        $query = "select * from PasswordReset p
                  left join Accounts a on (lower(p.PasswordResetEmail) = lower(a.Email))
                  where " . $where;
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp;
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("PasswordReset", $where, $whereParams);
    }
}