<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: july 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class UserActivitiesLogs
{
    public $LogID;
    public $LogData;
    public $LogDateTime;
    public $RelatedID;
    public $RelatedPage;
    public $UserID;
    public $IPAddress;

    function insert()
    {
        PdoDataAccess::insert("UserActivitiesLogs", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("UserActivitiesLogs", "LogID", $where, $whereParams);
    }

    static function SearchContentLogs($where = "", $whereParam = array())
    {
        $query = "select ContentName, LogData, LogDateTime from UserActivitiesLogs al
                    join Contents c on (RelatedID = ContentID)
                  where RelatedPage = 'content' and ContentName is not null ";

        $query .= (!empty($where)) ?  $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function SearchReadingLogs($where = "", $whereParam = array())
    {
        $query = "select * from(";
        $query .= " select ReadingHistoryName itemName, LogData, LogDateTime from  ReadingHistories rh
                    join UserActivitiesLogs al on (RelatedID = ReadingHistoryID)
                  where RelatedPage = 'history' and ReadingHistoryName is not null ";

        $query .= (!empty($where)) ?  $where : "";

        $query .= " union 
                    select concat(rh.ReadingHistoryName, ' - ',  dr.ResourceName) itemName, LogData, LogDateTime
                      from ReadingHistoryResources rhr
	                left join ReadingHistories rh on (rhr.ReadingHistoryID = rh.ReadingHistoryID)
                    left join DistributedResources dr on (rhr.ResourceID = dr.ResourceID)
                    left join UserActivitiesLogs al on (RelatedID = rhr.ReadingHistoryResourceID)
                  where RelatedPage = 'hResource' and ReadingHistoryName is not null";

        $query .= (!empty($where)) ?  $where : "";

        $query .= ") t order by LogDateTime";
        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }
}
