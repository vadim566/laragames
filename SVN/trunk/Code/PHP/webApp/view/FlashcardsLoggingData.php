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
    echo '<script src="../js/Flashcards.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';
require_once '../class/FlashcardsSet.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please Login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

$drp_content = FlashcardsSet::FlashcardContentDropBox("ContentID");

echo '<script>onLoad();</script>';

?>

<div class="logData" id="logDataDiv">

    <form method="POST" id="FlashcardLogForm" enctype='multipart/form-data'>
        <input type="hidden" id="task" name="task" value="getFlashcardLog">

        <div class="table">
            <div class="tr">
                <div class="tdHalf">
                    <div class="tdTitle">From:</div>
                    <div class="tdInput">
                        <input type="text" name="StartDate" id="StartDate">
                    </div>
                </div>
                <div class="tdHalf">
                    <div class="tdTitle">To:</div>
                    <div class="tdInput">
                        <input type="text" name="EndDate" id="EndDate">
                    </div>
                </div>
            </div>
            <div class="tr">
                <div class="tdHalf">
                    <div class="tdTitle">Content:</div>
                    <div class="tdInput">
                        <?php echo $drp_content; ?>
                    </div>
                </div>
                <div class="tdHalf">
                    <div class="tdTitle"></div>
                    <div class="tdInput">
                        <input type="button" value="show logs" id="SearchButt" name="SearchButt" onclick="searchFlashcardLog()">
                    </div>
                </div>
            </div>
        </div>

        <div id="FlashcardLogsDataDiv">
        </div>
        <br/>
        <div id="ResponseSummaryDiv" style="display: none">
        </div>

    </form>

</div>