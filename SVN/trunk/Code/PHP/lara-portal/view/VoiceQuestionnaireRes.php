<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 10/13/2019

 */

?>

<link rel="stylesheet" href="../css/MainContent.css">
<link rel="stylesheet" href="../css/TableToDiv.css">
<link rel="stylesheet" href="../SharedModules/jquery/jquery-ui.css">
<meta charset="utf-8">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<?php
$now = new DateTime();
echo '<script src="../js/LoggingData.js?' . $now->format('His') . '"></script>';
echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
echo '<script src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
echo '<script src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';
require_once '../class/ReadingHistory.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please Login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}
?>

<div class="logData" id="logDataDiv">

        <div class="table">
            <div class="tr">
                <div class="tdTXT">
                    <a href="../SharedModules/DownloadFile.php?download=VQ_SegmentResponses" target="_blank">Segment Responses </a>
                </div>
            </div>
            <div class="tr">
                <div class="tdTXT">
                    <a href="../SharedModules/DownloadFile.php?download=VQ_VersionOverallResponses" target="_blank">Version Overall Responses</a>

                </div>
            </div>
            <div class="tr">
                <div class="tdTXT">
                    <a href="../SharedModules/DownloadFile.php?download=VQ_VersionResponses" target="_blank">Version Responses</a>
                </div>
            </div>
        </div>

</div>