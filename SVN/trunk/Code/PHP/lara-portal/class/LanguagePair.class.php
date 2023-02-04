<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 10/7/2019
 * Time: 12:42 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';


class LanguagePair
{
    public $LanguagePairID;
    public $L1ID;
    public $L2ID;

    function insert()
    {
        PdoDataAccess::insert("LanguagePairs", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("LanguagePairs", "LanguagePairID", $where, $whereParams);
    }

    function LanguagePairExists()
    {
        $query = "select * from LanguagePairs where  " .
            "L1ID = :l1ID and L2ID = :l2ID";

        $whereParams = array(":l1ID" => $this->L1ID,
            ":l2ID" => $this->L2ID);
        $temp = PdoDataAccess::runquery($query, $whereParams);

        if(count($temp) == 0)
        {
            return false;
        }
        else
        {
            $this->LanguagePairID = $temp[0]["LanguagePairID"];
            return true;
        }
    }

    static function getLanguagePairID($L1ID, $L2ID)
    {
        $query = "select * from LanguagePairs where  " .
            "L1ID = :l1ID and L2ID = :l2ID";

        $whereParams = array(":l1ID" => $L1ID,
            ":l2ID" => $L2ID);
        $temp = PdoDataAccess::runquery($query, $whereParams);

        if(count($temp) == 0)
        {
            return false;
        }
        else
        {
            $LanguagePairID = $temp[0]["LanguagePairID"];
            return $LanguagePairID;
        }
    }
}
?>