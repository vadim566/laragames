<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/17/2019
 * Time: 02:38 PM
 */

require_once ROOT . 'SharedModules/PdoDataAccess.class.php';


class ImportContent
{

    public $ImportContentID;
    public $ImportFileName;
    public $CreatorID;
    public $ContentID;

    function insert()
    {
        PdoDataAccess::insert("ImportContents", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ImportContents", "ImportContentID", $where, $whereParams);
    }

    function update()
    {
        $where = "ImportContentID = :importContentID";
        $whereParams[":importContentID"] = $this->ImportContentID;
        PdoDataAccess::update("ImportContents", $this, $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ImportContents", $where, $whereParams);
    }
}


?>