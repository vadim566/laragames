<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/20/2019
 * Time: 03:17 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';


class DistributedResourcePage
{
    public $ResourcePageID;
    public $ResourceID;
    public $PageNumber;
    public $PageName;

    function insert()
    {
        PdoDataAccess::insert("DistributedResourcePages", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("DistributedResourcePages", "ResourcePageID", $where, $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("DistributedResourcePages", $where, $whereParams);
    }

    static function LastPageNumber($where, $whereParam)
    {
        $query = "SELECT MAX(PageNumber) from DistributedResourcePages";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp[0][0];
    }
}


?>