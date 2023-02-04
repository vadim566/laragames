<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/25/2019
 * Time: 18:08 PM
 */
?>

<link rel="stylesheet" href="../css/MainContent.css">
<link rel="stylesheet" type="text/css" href="../css/LaraPageStyles.css">

<?php

$now = new DateTime();
echo '<script type="text/javascript" charset="utf8" src="../js/ReadingHistory.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../js/LaraPageScript.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';
require_once '../class/ReadingHistoryResource.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please Login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

if(!isset($_REQUEST["rhrID"]) || !isset($_REQUEST["pageToLoad"]))
{
    echo "OOOOPS, Page not found. <br />";
    die();
}

$where = " ReadingHistoryResourceID = :readingHistoryResourceID and PageNumber = :pageNumber";
$whereParam = array(":readingHistoryResourceID" => $_REQUEST["rhrID"], ":pageNumber" => $_REQUEST["pageToLoad"]);
$info = ReadingHistoryResource::FullSelect($where, $whereParam, true);


?>

<div class="HistoryResourceNav" style="width: 100%; height: 100%">
    <div class="table" style="height: 5%">
        <div class="tr">
            <div class="tdTXT">
                <p class="BookInfo">
                    <?php echo $info[0]["ResourceName"]; ?>
                </p>
            </div>
        </div>
    </div>

    <div class="table"  id="fromWeb" style="height: 75%">
        <div class="tr" style="height: 100%">
            <div class="tdTXT" style="height: 100%; padding: 0px 50px">
                    <iframe id="main_frame" name="main_frame" frameborder="0" width="100%" height="99%"
                            src=<?php echo PortalReadingHistoryDir . $info[0]["UserID"] . "_" . $info[0]["ReadingHistoryID"] . "/" .
                        str_replace(" ", "_", $info[0]["ReadingHistoryName"]) .
                        "_" . $info[0]["UserID"] . "_" . $info[0]["ReadingHistoryID"] . "vocabpages/" .$info[0]["PageName"];  ?>>
                    </iframe>
            </div>
        </div>
    </div>

    <div class="table" id="navigationBar" style="height: 20%">
        <img src="../img/sign-left-icon.png"
              onclick="goToPrvPage(<?php echo $info[0]["ReadingHistoryResourceID"] . "," . $info[0]["PageNumber"]; ?>)" >
            <span class="BookInfo">
                Page <?php echo $info[0]["PageNumber"]; ?>
            </span>
        <img src="../img/sign-right-icon.png"
              onclick="goToNextPage(<?php echo $info[0]["ReadingHistoryResourceID"] . "," . $info[0]["PageNumber"]; ?>)">
    </div>
</div>

