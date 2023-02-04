<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 9/11/2019
 * Time: 03:59 PM
 */

require_once '../Config.php';
require_once '../SharedModules/ExtraModules.class.php';

$query = "select ContentID, ContentName, DirName, WebAddress 
          from Contents where webAddress is not null";
$temp = PdoDataAccess::runquery($query);

$count = count($temp);

for($i = 0; $i < $count; $i++)
{
    $oldName = CallectorDir . str_replace(" ","_", $temp[$i]["ContentName"]). "vocabpages";
    $newName = CallectorDir . $temp[$i]["DirName"] . "vocabpages";
    rename ($oldName , $newName);

    $newWebAddress = WebRoot . $temp[$i]["DirName"] . "vocabpages" . "/_hyperlinked_text_.html";
    $updateQuery = "update Contents set webAddress = : webAddress where ContentID = :contentID";
    $whereParam = array(":webAddress" => $newWebAddress, ":contentID" => $temp[$i]["ContentID"]);

    PdoDataAccess::runquery($updateQuery, $whereParam);

    echo $oldName . "</br>";
    echo $newName . "</br>";
    echo $newWebAddress . "</br>";
    echo $updateQuery ."</br>";
    print_r($whereParam);
    echo "</br>" . "---------------------" . "</br>";

}
?>