<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/21/2019
 * Time: 03:17 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';
require_once '../SharedModules/ExtraModules.class.php';


class ReadingHistoryResource
{

    public $ReadingHistoryResourceID;
    public $ReadingHistoryID;
    public $ResourceID;
    public $LastReadPage;

    function insert()
    {
        PdoDataAccess::insert("ReadingHistoryResources", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ReadingHistoryResources", "ReadingHistoryResourceID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ReadingHistoryResources", $where, $whereParams);
    }

    static function SearchReadingHistoryResource($where = "", $whereParam = array())
    {
        $query = "select * from ReadingHistoryResources rhr
                    left join DistributedResources dr on (rhr.ResourceID = dr.ResourceID)
                     where dr.ResourceID is not null  ";

        $query .= (!empty($where)) ? " and " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function FullSelect($where = "", $whereParam = array(), $logData = false)
    {
        $query = "select rhr.*, rh.UserID, rh.ReadingHistoryName, drp.PageName, drp.PageNumber, dr.ResourceName
                      from ReadingHistoryResources rhr
	                left join ReadingHistories rh on (rhr.ReadingHistoryID = rh.ReadingHistoryID)
                    left join DistributedResources dr on (rhr.ResourceID = dr.ResourceID)
                    left join DistributedResourcePages drp on (rhr.ResourceID = drp.ResourceID) ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        if($logData)
        {
            $resultArray = array();
            $resultArray[0]["id"] = $whereParam[":readingHistoryResourceID"];
            $resultArray[0]["nextPage"] = $whereParam[":pageNumber"];
            $resultArray[0]["resultMsg"] = "Reading page ";
            ExtraModules::UserActivityLog(HistoryResourceRelatedPage, $resultArray);
        }

        return $temp;
    }

    static function LastReadPagePlus($rhrID)
    {
        $query = "update ReadingHistoryResources set  LastReadPage = LastReadPage + 1 
                  where ReadingHistoryResourceID = :rhrID ";
        $wherParam = array(":rhrID" => $rhrID);
        PdoDataAccess::runquery($query, $wherParam);
        return true;
    }

    static function CheckResourceDuplication($where = "", $whereParams = array())
    {
        $query = "select count(*) from ReadingHistoryResources rhr";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParams))
            $temp = PdoDataAccess::runquery($query, $whereParams);
        else
            $temp = PdoDataAccess::runquery($query);

        if($temp[0][0] == 0)
            return true;
        else
            return false;
    }
}
?>