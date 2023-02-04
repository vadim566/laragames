<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */

require_once ROOT . '/shared-modules/PdoDataAccess.class.php';

class content_visit
{
    public $VisitID;
    public $UserID;
    public $ContentID;
    public $VisitDate;
    public $VisitType;

    function insert()
    {
        PdoDataAccess::insert("ContentVisit", $this);
    }

    static function selectVisits()
    {
        $ret = array();
        $query = "select visitType, count(distinct UserID) visitCount 
                    from ContentVisit 
                    group by ContentID, VisitType 
                    having contentID = :cID";
        $whereParam = array(":cID" => $_REQUEST['Q1']);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        for($i = 0 ; $i < count($temp); $i++)
            $ret[$temp[$i]["visitType"]] = $temp[$i]["visitCount"];
        return $ret;
    }
}