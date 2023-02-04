<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentEmbeddedItem
{
    public $ItemID;
    public $ItemType;
    public $ItemName;
    public $IsUploaded;
    public $ContentID;
    public $ItemState;


    function insert()
    {
        PdoDataAccess::insert("ContentEmbeddedItems", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentEmbeddedItems", "ContentID", $where, $whereParams);
    }

    static function SearchContentEmbeddedItem($where = "", $whereParam = array())
    {
        $query = "select * from ContentEmbeddedItems ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function itemExists($contentID, $itemType, $itemName)
    {
        $query = "select count(*) from ContentEmbeddedItems where  " .
            "ItemType = :itemType and ItemName = :itemName and ContentID = :contentID";

        $whereParams = array(":contentID" => $contentID,
            ":itemType" => $itemType,
            ":itemName" => $itemName);
        $temp = PdoDataAccess::runquery($query, $whereParams);

        if($temp[0][0] == 0)
            return false;
        else
            return true;
    }

    static function updateItemState($contentID, $itemType, $itemName)
    {
        $query = "update ContentEmbeddedItems set ItemState = 'NEW'  where  " .
            "ItemType = :itemType and ItemName = :itemName and ContentID = :contentID";

        $whereParams = array(":contentID" => $contentID,
            ":itemType" => $itemType,
            ":itemName" => $itemName);

        PdoDataAccess::runquery($query, $whereParams);
    }

    static function updateUploadStatus($contentID, $itemType, $itemName)
    {
        $query = "update ContentEmbeddedItems set IsUploaded = 'YES' where  " .
                    "ItemType = :itemType and ItemName = :itemName and ContentID = :contentID";

        $whereParams = array(":contentID" => $contentID,
            ":itemType" => $itemType,
            ":itemName" => $itemName);

        PdoDataAccess::runquery($query, $whereParams);
    }

    static function MakeItemsStateOld($contentID)
    {
        $query = "update ContentEmbeddedItems set ItemState = 'OLD' where  " .
            " ContentID = :contentID";

        $whereParams = array(":contentID" => $contentID);

        PdoDataAccess::runquery($query, $whereParams);
    }

    static function ListOfContentEItems($contentID)
    {
        $query = "SELECT c.ContentID, image.ImageNames, audio.AudioNames, css.cssNames, script.ScriptNames
                    from ContentEmbeddedItems c
                left join (select ContentID, group_concat(
                Concat(ItemName, ':', IsUploaded) SEPARATOR '@@') as ImageNames FROM ContentEmbeddedItems 
                where ItemType = 'Image' group by ContentID) image 
                on (image.ContentID = c.ContentID)
                left join (SELECT ContentID, group_concat(
                Concat(ItemName, ':', IsUploaded) SEPARATOR '@@') as AudioNames FROM ContentEmbeddedItems
                where ItemType = 'Audio' group by ContentID) audio
                on  (audio.ContentID = c.ContentID)
                left join (SELECT ContentID, group_concat(
                Concat(ItemName, ':', IsUploaded) SEPARATOR '@@') as CssNames FROM ContentEmbeddedItems
                where ItemType = 'CSS' group by ContentID) css
                on  (css.ContentID = c.ContentID)
                left join (SELECT ContentID, group_concat(
                Concat(ItemName, ':', IsUploaded) SEPARATOR '@@') as ScriptNames FROM ContentEmbeddedItems
                where ItemType = 'Script' group by ContentID) script
                on  (script.ContentID = c.ContentID)
                
                where c.ContentID = :contentID ";

        $whereParam = array(":contentID" => $contentID);

        $temp = PdoDataAccess::runquery($query, $whereParam);

        if(count($temp) == 0)
            return false;
        return $temp[0];
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentEmbeddedItems", $where, $whereParams);
    }

    static function  allUploaded($contentID)
    {
        $query = "select count(*) from ContentEmbeddedItems where  " .
            " IsUploaded = 'NO' and ContentID = :contentID";

        $whereParams = array(":contentID" => $contentID);
        $temp = PdoDataAccess::runquery($query, $whereParams);

        if($temp[0][0] == 0)
            return true;
        else
            return false;
    }

}
?>
