<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentRecordingTask
{
    public $ContentRecordingTaskID;
    public $ContentID;
    public $TaskID;
    public $TaskType;
    public $LastUpdate;
    public $TotalItems;
    public $RecordedItems;

    function insert()
    {
        PdoDataAccess::insert("ContentRecordingTasks", $this);
    }

    static function RecordingsHasChanged($contentID, $taskType)
    {
        $query = "SELECT * FROM ContentRecordingTasks where ContentID = :cID and TaskType = :taskType
                    order by ContentRecordingTaskID desc limit 2";
        $whereParam = array(":cID" => $contentID, ":taskType" => $taskType);
        $temp = PdoDataAccess::runquery($query, $whereParam);

        if(count($temp) < 2)
            return true;

        if($temp[0]["LastUpdate"] != $temp[1]["LastUpdate"])
            return true;

        return false;
    }
}
