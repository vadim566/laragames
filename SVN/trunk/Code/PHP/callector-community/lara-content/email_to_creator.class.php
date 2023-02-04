<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */

require_once ROOT . '/shared-modules/PdoDataAccess.class.php';

class email_to_creator
{
    public $EmailID;
    public $From;
    public $To;
    public $When;
    public $EmailBody;
    public $EmailSubject;

    function insert()
    {
        PdoDataAccess::insert("EmailsToCreators", $this);
    }

    function set_sender_info($senderID)
    {
        $whereParam = array(":uID" => $senderID);
        $query = "select Email, UserName from Accounts a where UserID = :uID";
        $temp = PdoDataAccess::runquery($query, $whereParam);
        $this->From = $temp[0][0];
        $this->EmailSubject = $temp[0][1] . " from callector-community; ";
    }

    function set_receiver_info($contentID)
    {
        $whereParam = array(":cID" => $contentID);
        $query = "select Email, ContentName FROM Contents c
                      left join Accounts a on (c.CreatorID = a.UserID)
                      where ContentID = :cID" ;
        $temp = PdoDataAccess::runquery($query, $whereParam);
        $this->To = $temp[0][0];
        $this->EmailSubject .= "about " . $temp[0][1];
    }
}