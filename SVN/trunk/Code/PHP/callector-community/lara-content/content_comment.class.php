<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */

require_once ROOT . '/shared-modules/PdoDataAccess.class.php';

class content_comment
{
    public $CommentID;
    public $ContentID;
    public $UserID;
    public $CommentText;
    public $ParentID;
    public $ReplyTo;
    public $CommentTime;

    function insert()
    {
        PdoDataAccess::insert("ContentComments", $this);
    }

    static function getCommentInfo()
    {
        $whereParam = array(":cID" => $_REQUEST['Q1']);
        $query = "SELECT cc.*, a.UserName FROM ContentComments cc
                    LEFT JOIN Accounts a on (cc.UserID = a.UserID)
                      where ContentID = :cID" ;
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp;
    }

}