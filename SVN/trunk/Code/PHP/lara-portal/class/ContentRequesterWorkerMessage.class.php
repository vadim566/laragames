<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 10/7/2019
 * Time: 12:42 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';


class ContentRequesterWorkerMessage
{
    public $MessageID;
    public $ContentID;
    public $UserID;
    public $UserRole;
    public $MessageBody;
    public $MessageDateTime;

    function insert()
    {
        PdoDataAccess::insert("ContentRequesterWorkerMessages", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentRequesterWorkerMessages", "MessageID", $where, $whereParams);
    }

    static function  selectMessages($whereParam = array())
    {
        $query = "select c.ContentID, a.UserName,  UserRole,  MessageDateTime, MessageBody 
                    from ContentRequesterWorkerMessages c
	                left join Accounts a on (c.UserId = a.UserID)
	                where ContentID = :cID
	                order by MessageDateTime";

        $temp = PdoDataAccess::runquery($query, $whereParam);

        return $temp;
    }
}
