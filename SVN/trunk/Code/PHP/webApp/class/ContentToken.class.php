<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/17/2019
 * Time: 02:38 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';


class ContentToken
{

    public $ContentTokenID;
    public $ContentID;
    public $SegmentOrder;
    public $SectionType;
    public $OrderInSection;
    public $EntryText;

    static function insertContentTokens($insertFile)
    {
        $insertQuery = "load data local infile '$insertFile' into table ContentTokens
                           fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID,SegmentOrder,SectionType,OrderInSection,EntryText)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function updateContentTokens($contentFileName, $tmpTableName)
    {
        $updateQuery = "create temporary table " . $tmpTableName . "  LIKE ContentTokens";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "load data local infile '$contentFileName' into table $tmpTableName
                            fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentTokenID,ContentID,SegmentOrder,SectionType,OrderInSection,EntryText)";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "insert into ContentTokens
                            select * from " . $tmpTableName . " tmpTable
                                on duplicate key update EntryText = tmpTable.EntryText";
        PdoDataAccess::runquery($updateQuery);
        $updateQuery = "drop temporary table " . $tmpTableName ;
        PdoDataAccess::runquery($updateQuery);
        return true;
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentTokens", $where, $whereParams);
    }

    static function SearchContentToken($where = "", $whereParam = array())
    {
        $query = "select * from ContentTokens ";
        $query .= (!empty($where)) ? " where " . $where : "1=1";

        $query .= " order by SegmentOrder, SectionType, OrderInSection";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        $tokenInfo = array();
        for($i = 0; $i < count($temp); $i++)
        {
            $index1 = $temp[$i]["SegmentOrder"];
            switch ($temp[$i]["SectionType"])
            {
                case "token":
                    $index2 = 1;
                    break;

                case "type":
                    $index2 = 2;
                    break;

                case "segment":
                    $index2 = 3;
                    break;
            }
            $index3 = $temp[$i]["OrderInSection"];

            $tokenInfo[$index1][$index2][$index3]["ContentTokenID"] = $temp[$i]["ContentTokenID"];
            $tokenInfo[$index1][$index2][$index3]["EntryText"] = $temp[$i]["EntryText"];
        }
        return $tokenInfo;
    }

    static function NumberOfPages($contentID)
    {
        $query = "SELECT max(SegmentOrder) FROM ContentTokens where ContentID = :contentID";
        $whereParam[":contentID"] = $contentID;

        $temp = PdoDataAccess::runquery($query, $whereParam);
        $totalSegments = $temp[0][0];
        $numberOfPages = ceil($totalSegments / 5);
        return $numberOfPages;
    }
}