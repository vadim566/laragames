<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/17/2019
 * Time: 02:38 PM
 */

require_once ROOT . 'SharedModules/PdoDataAccess.class.php';


class DistributedResource
{

    public $ResourceID;
    public $ResourceName;
    public $WebAddress;
    public $ResourceType;
    public $ParentID;
    public $UserID;
    public $L2ID;
    public $IsDeleted;

    function insert()
    {
        PdoDataAccess::insert("DistributedResources", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("DistributedResources", "ResourceID", $where, $whereParams);
    }

    static function SearchResource($where = "", $whereParam = array())
    {
        $query = "select * from DistributedResources ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function FullSelect($where = "", $whereParam = array())
    {
        $query = "select ResourceID, ResourceName, dr.WebAddress, c.WebAddress contentWebAddress,
                          UserID, UserName, 
                          ResourceType, dr.L2ID, LanguageName from DistributedResources dr

                    left join Accounts a using (UserID)
                    left join Languages l on (dr.L2ID = l.LanguageID)
                    left join Contents c on (c.IsDeleted = 'NO' and c.DistributedResourceID = dr.ResourceID)";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    function update()
    {
        $whereParams[":resourceID"] = $this->ResourceID;
        PdoDataAccess::update("DistributedResources", $this, "ResourceID=:resourceID", $whereParams);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("DistributedResources", $where, $whereParams);
    }

    static function isLanguageResourceRegistered($intendedWebAddress = "")
    {
        $query = "select * from DistributedResources where WebAddress = :webAddress ";
        $whereParam = array(":webAddress" => $intendedWebAddress);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        if(count($temp) == 0)
            return "-1";
        else
            return $temp[0]["ResourceID"];

    }

    static function CreateAllResources($where, $whereParam)
    {
        $query = "SELECT concat('\"', d1.ResourceID, '_', d1.ResourceName, '\"') as ResID, 
	                concat('[\"', d1.WebAddress, '\",',
			              if(d1.ResourceType = 'Language', '\"LanguageResource\"]',
                          concat('\"', d2.ResourceID, '_', d2.ResourceName, '\"]'))) as ResInfo
                  FROM DistributedResources d1 
                  left join DistributedResources d2 on (d1.ParentID = d2.ResourceID)";

        $query .= (!empty($where)) ? " where " . $where : "";
        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function ContentResourceDropBox($dropBoxName, $LanguageID = -1)
    {
        $retStr = "<select name=$dropBoxName id=$dropBoxName>";
        $retStr .= "<option value=-1  selected>---</option>";

        $query = "select * from DistributedResources 
                    where ResourceType = 'Content'
                      and IsDeleted = 'NO' and L2ID = :l2id";
        $whereParam = array(":l2id" => $LanguageID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        for($i=0; $i<count($temp); $i++)
        {
            $retStr .= "<option value='" . $temp[$i]["ResourceID"] . "'>";
            $retStr .= str_replace("_", " ", $temp[$i]["ResourceName"]);
            $retStr .= "</option>";
        }

        $retStr .= "</select>";
        return $retStr;
    }

    static function LanguageResourceDropBox($dropBoxName, $hasExtraRow, $selectedID = -1)
    {
        $retStr = "<select name=$dropBoxName id=$dropBoxName>";
        if($hasExtraRow)
        {
            $retStr .= "<option value=-1 ";
            if($selectedID == -1)
                $retStr .= " selected ";
            $retStr .= ">---</option>";
        }

        $query = "select * from DistributedResources where ResourceType = 'Language'";
        $temp = PdoDataAccess::runquery($query);
        for($i=0; $i<count($temp); $i++)
        {
            $retStr .= "<option value='" . $temp[$i]["ResourceID"] . "'" ;
            if($temp[$i]["ResourceID"] == $selectedID)
                $retStr .= " selected ";
            $retStr .= " >";
            $retStr .= $temp[$i]["WebAddress"];
            $retStr .= "</option>";
        }

        $retStr .= "</select>";
        return $retStr;
    }

    static function NextPageCompileResourceInfo($where, $whereParam)
    {
        $query = "SELECT concat(d1.ResourceID, '_', d1.ResourceName, '  ',
				d2.ResourceID, '_', d2.ResourceName) as ResInfo
                  FROM DistributedResources d1 
                  left join DistributedResources d2 on (d1.ParentID = d2.ResourceID)";

        $query .= (!empty($where)) ? " where " . $where : "";
        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp[0][0];
    }

    static function LanguagesOfResources($dropBoxName, $hasExtraRow, $selectedID = -1)
    {
        $retStr = "<select name=$dropBoxName id=$dropBoxName>";
        if($hasExtraRow)
        {
            $retStr .= "<option value=-1 ";
            if($selectedID == -1)
                $retStr .= " selected ";
            $retStr .= ">---</option>";
        }

        $query = "select LanguageName, LanguageID from DistributedResources dr
                    left join Languages l on (dr.L2ID = l.LanguageID )
                    where ResourceType = 'Content' group by L2ID";
        $temp = PdoDataAccess::runquery($query);
        for($i=0; $i<count($temp); $i++)
        {
            $retStr .= "<option value='" . $temp[$i]["LanguageID"] . "'" ;
            if($temp[$i]["LanguageID"] == $selectedID)
                $retStr .= " selected ";
            $retStr .= " >";
            $retStr .= $temp[$i]["LanguageName"];
            $retStr .= "</option>";
        }

        $retStr .= "</select>";
        return $retStr;
    }

    static function UsageInReadingsCount($ResourceID)
    {
        $query = "select count(*) from ReadingHistoryResources rhr where ResourceID = :rID";
        $whereParam = array(":rID" => $ResourceID);
        $temp = PdoDataAccess::runquery($query, $whereParam);

        return $temp[0][0];
    }

    static function PartialUpdate($setPart, $wherePart, $params)
    {
        $query = "update DistributedResources set " . $setPart . " where " . $wherePart;
        PdoDataAccess::runquery($query, $params);
    }


}


?>