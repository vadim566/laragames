<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ApacheLog
{

    public $LogId;
    public $IPAddress;
    public $Date;
    public $AccessMethod;
    public $RequestedURL;
    public $Param7_9;
    public $SourceURL;
    public $Browser;
    public $SystemInfo;
    public $Param17_22;
    public $GrepExpression;

    function insert()
    {
        PdoDataAccess::insert("ApacheLog", $this);
    }
}
