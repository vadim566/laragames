<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 10/7/2019
 * Time: 12:42 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';


class ContentGiveUpReason
{
    public $ReasonID;
    public $ContentID;
    public $UserID;
    public $UserRole;
    public $ReasonBody;
    public $ReasonDateTime;

    function insert()
    {
        PdoDataAccess::insert("ContentGiveUpReason", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentGiveUpReason", "ReasonID", $where, $whereParams);
    }

    static function  selectReasons($whereParam = array())
    {
        $query = "select c.ContentID, a.UserName,  UserRole,  MessageDateTime, MessageBody 
                    from ContentGiveUpReason c
	                left join Accounts a on (c.UserId = a.UserID)
	                where ContentID = :cID
	                order by ReasonDateTime";

        $temp = PdoDataAccess::runquery($query, $whereParam);

        return $temp;
    }
}
