<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: july 2019
 */


require_once ROOT . 'SharedModules/PdoDataAccess.class.php';

class ExternalCommandsLogs
{
    public $LogID;
    public $LogType;
    public $LogData;
    public $LogDateTime;
    public $UserID;
    public $RelatedID;
    public $RelatedPage;
    public $ParentID;

    function insert()
    {
        PdoDataAccess::insert("ExternalCommandsLogs", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ExternalCommandsLogs", "LogID", $where, $whereParams);
    }

    static function SearchPythonCommandRes($RelatedID = "", $RelatedPage = "", $MsgToShow = "")
    {
        $query = "select PythonRelatedCommand from ServerToClientReturns where SentMsgToClientSide  = :msgToSent ";
        $whereParam = array(":msgToSent" => $MsgToShow);

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $pythonRelatedCommand = $temp[0]["PythonRelatedCommand"];

        $query = ' select pyRes.* from ExternalCommandsLogs pyRes
                      left join ExternalCommandsLogs pyCmnt on (pyRes.ParentID = pyCmnt.LogID)
                      where pyCmnt.RelatedID = :relatedID and pyCmnt.RelatedPage = :relatedPage and pyCmnt.LogData like :logData 
                        Order by pyRes.LogID desc limit 1';
        $whereParam = array(":relatedID" => $RelatedID, ":relatedPage" => $RelatedPage, ":logData" => "%". $pythonRelatedCommand ."%");

        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp[0]["LogData"];
    }

    static function SearchExternalCommandsLogs($RelatedID = "", $RelatedPage = "")
    {

        $query = 'SELECT CONCAT( LogType , " : ", LogData) as LogInfo , 
                         CONCAT( "Executed at : " , LogDateTime) as LogTime 
                         FROM ExternalCommandsLogs
                         where LogType in ("PythonRes","PythonCmnd") and 
                               RelatedID = :relatedID and RelatedPage = :relatedPage 
                         ORDER BY LogID DESC';

        $whereParam = array(":relatedID" => $RelatedID, ":relatedPage" => $RelatedPage);

        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp;
    }

    static function SearchFlashcardsExternalCommandsLogs($where = "", $whereParams = array())
    {

        $query = 'SELECT CONCAT( LogType , " : ", LogData) as LogInfo , 
                         CONCAT( "Executed at : " , LogDateTime) as LogTime 
                         FROM ExternalCommandsLogs
                         where LogType in ("PythonRes","PythonCmnd") and ' . $where . '
                         ORDER BY LogID DESC';

        $temp = PdoDataAccess::runquery($query, $whereParams);

        return $temp;
    }
}
?>
