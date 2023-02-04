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
    public $RecordingTaskID;
    public $RecordingTaskType;
    public $RecordingTaskDate;

    function insert()
    {
        PdoDataAccess::insert("ContentRecordingTasks", $this);
    }
}
?>
