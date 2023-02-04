<?php
/**
 *
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/21/2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ReadingHistory
{
    public $ReadingHistoryID;
    public $ReadingHistoryName;
    public $UserID;
    public $L1ID;
    public $L2ID;
    public $AudioMouseOver;
    public $WordTranslationMouseOver;
    public $SegmentTranslationMouseOver;
    public $TableOfContents;
    public $ColouredWords;
    public $AudioWordsInColour;
    public $MaxExamplesPerWordPage;
    public $Font;
    public $FrequencyListsInMainText;
    public $FontSize;
    public $SegmentTranslationCharacter;
    public $TranslatedWordsInColour;
    public $SegmentTranslationAsPopup;

    function insert()
    {
        PdoDataAccess::insert("ReadingHistories", $this);
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ReadingHistories", $where, $whereParams);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ReadingHistories", "ReadingHistoryID", $where, $whereParams);
    }

    static function SearchReadingHistory($where = "", $whereParam = array())
    {
        $query = "select * from ReadingHistories ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function FullSelect($where = "", $whereParam = array())
    {
        $query = "SELECT rh.*, l1.LanguageName L1Name, l2.LanguageName L2Name
                  FROM ReadingHistories rh 
                  left join Languages l1 on (rh.L1ID = l1.LanguageID)
                  left join Languages l2 on (rh.L2ID = l2.LanguageID)";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    function update()
    {
        $whereParams[":readingHistoryID"] = $this->ReadingHistoryID;
        PdoDataAccess::update("ReadingHistories", $this, "ReadingHistoryID=:readingHistoryID", $whereParams);
    }

    static function PartialUpdate($setPart, $wherePart, $params)
    {
        $query = "update ReadingHistories set " . $setPart . " where " . $wherePart;
        PdoDataAccess::runquery($query, $params);
    }

    function hasAssignedResource()
    {
        $query = "select count(*) from ReadingHistoryResources 
                  where ReadingHistoryID = :readingHistoryID";

        $whereParams[":readingHistoryID"] = $this->ReadingHistoryID;

        $temp = PdoDataAccess::runquery($query, $whereParams);
        if($temp[0][0] == 0)
            return false;
        else
            return true;
    }

    function listOfHistoryResourcesForConfig($where, $whereParam)
    {
        $query = "SELECT concat('[\"', d1.ResourceID, '_', d1.ResourceName, '\",',
				                '\"', d2.ResourceID, '_', d2.ResourceName, '\",',
                                '[1,' , rhr.LastReadPage, ']]') as HistoryResInfo 
                          
				  FROM ReadingHistoryResources rhr
                    left join DistributedResources d1  on (rhr.ResourceID = d1.ResourceID)
                    left join DistributedResources d2 on (d1.ParentID = d2.ResourceID)";

        $query .= (!empty($where)) ? " where " . $where : "";
        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function ReadingDropBox($dropBoxName, $userID, $selectedID = -1)
    {
        $retStr = "<select name=$dropBoxName id=$dropBoxName>";
        $retStr .= "<option value=-1 ";
        if($selectedID == -1)
            $retStr .= " selected ";
        $retStr .= ">all</option>";

        $query = "select concat(ReadingHistoryName , ',' , l1.LanguageName, '-', l2.LanguageName) RhTitle, ReadingHistoryID 
                    from ReadingHistories 
                      left join Languages l1 on (l1.LanguageID = L1ID)
                      left join Languages l2 on (l2.LanguageID = L2ID)
                  where UserID = :uid order by ReadingHistoryID desc";
        $whereParam = array(":uid" => $userID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        for($i=0; $i<count($temp); $i++)
        {
            $retStr .= "<option value='" . $temp[$i]["ReadingHistoryID"] . "'" ;
            if($temp[$i]["ReadingHistoryID"] == $selectedID)
                $retStr .= " selected ";
            $retStr .= " >";
            $retStr .= $temp[$i]["RhTitle"];
            $retStr .= "</option>";
        }
        $retStr .= "</select>";
        return $retStr;
    }

}

?>
