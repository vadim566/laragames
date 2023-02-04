<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/21/2019
 */

?>

<link rel="stylesheet" href="../css/MainContent.css">
<link rel="stylesheet" href="../css/TableToDiv.css">
<link rel="stylesheet" href="../SharedModules/jquery/jquery-ui.css">
<meta charset="utf-8">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<?php
    $now = new DateTime();
    echo '<script src="../js/ReadingHistory.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';
require_once '../SharedModules/ExtraModules.class.php';
require_once '../class/Language.class.php';
require_once '../class/Account.class.php';
require_once '../class/ReadingHistory.class.php';
require_once '../class/DistributedResource.class.php';
require_once '../data/ReadingHistory.data.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

$drp_L1 = Language::LanguageDropBox("L1ID", true);
$drp_L2 = DistributedResource::LanguagesOfResources("L2ID", true);
$R_H_Obj = array();

if(isset($_GET["Q0"]))
{
    $where = " ReadingHistoryID = :readingHistoryID";
    $whereParam = array(":readingHistoryID" => $_GET["Q0"]);
    $info = ReadingHistory::SearchReadingHistory($where, $whereParam);
	if(count($info) != 0)
	{
        $R_H_Obj = FillItems($info[0]);
    }
    $drp_ContentResources = DistributedResource::ContentResourceDropBox("ResourceID", $R_H_Obj->L2ID);
}
else
{
    $R_H_Obj = MakeEmptyHistory();

    $drp_ContentResources = "<select name='ResourceID' id='ResourceID'>";
    $drp_ContentResources .= "<option value=-1  selected>---</option>";
    $drp_ContentResources .= "</select>";
}

$jsObjName = "R_H_Val";
echo ExtraModules::objToJS($R_H_Obj, $jsObjName);

$activeTab = 0;
if(isset($_GET["activeTab"]))
{
    $activeTab = $_GET["activeTab"];
}

$MsgToShow = "notSetYet";
$PythonFailureReturnMsgs = array("RecompileFailureHR", "RecompileFailureRH", "FailedToAddNewPage");

if(isset($_GET["activeTab"]))
{
    $MsgToShow = $_GET["msg"];
}

$backwardButton = '<div class="table">
        <div class="tr">
            <div class="tdTitle">
                <img src="../img/backward-icon.png" title="click to go back"
                     onclick=\'$("#mainContentDIV").load("ReadingHistories.php");\' >
            </div>
        </div>
    </div>';


echo '<script>onLoad(' . $activeTab . ',"'. $MsgToShow .'");</script>';
?>

<div class="newReadingHistory">

    <?php echo $backwardButton; ?>
    <div class="table readingHistoryError"  style="display: none">
        <div class="tr">
            <div class="tdInput">
                <p class="ErrorMsg"></p>
            </div>
            <div class="tdTitle">
                <img src='../img/ok-icon.png' title='hide it'
                     onclick='$(".readingHistoryError").css("display", "none");' >
                <?php
                if(in_array($MsgToShow, $PythonFailureReturnMsgs)){
                    echo "<a target='_blank' 
                              href='../SharedModules/DownloadFile.php?" .
                              "download=PythonOutputDetail&relatedID=" . $R_H_Obj->ReadingHistoryID .
                                "&relatedPage=history&msgToShow=" . $MsgToShow . "'><img src='../img/detail-icon.png' title='more detail'></a>";
                }
                ?>
            </div>
        </div>
    </div>

    <div id="tabs">

    <form method="POST" id="readingHistoryForm" enctype='multipart/form-data'>
        <input type="hidden" id="task" name="task" value="AddReadingHistory">
        <input type="hidden" id="ReadingHistoryID" name="ReadingHistoryID">
        <input type="hidden" id="DirName" name="DirName">
        <input type="hidden" id="UserID" name="UserID">

        <ul>
            <li><a href="#createHistory">Create reading history</a></li>
            <li><a href="#addResource">Add text</a></li>
        </ul>
        <!--START OF FIRST TAB, ie Uploading ALL necessary data-->
        <div class="table" id="createHistory">
            <div id="MandatoryDiv" class="table">
                <div class="tr">
                    <div class="tdTitle">Reading history name:</div>
                    <div class="tdInput">
                        <input type="text" name="ReadingHistoryName" id="ReadingHistoryName"  size="20" value="">
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Reading language:</div>
                    <div class="tdInput">
                        <?php echo $drp_L2; ?>
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Translation language:</div>
                    <div class="tdInput">
                        <?php echo $drp_L1; ?>
                    </div>
                </div>
            </div>
            <div id="ComplementaryDiv" class="table">
                <div class="tr">
                    <div class="tdTitle">Audio mouseover:</div>
                    <div class="tdInput">
                        <input type="radio" id="AudioMouseOver_Y" name="AudioMouseOver"  value="YES" >On
                        <input type="radio"  id="AudioMouseOver_N" name="AudioMouseOver"  value="NO" >Off &nbsp;
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Show word translation:</div>
                    <div class="tdInput">
                        <input type="radio"  id="WordTranslationMouseOver_Y" name="WordTranslationMouseOver"  value="YES" >On
                        <input type="radio" id="WordTranslationMouseOver_N" name="WordTranslationMouseOver"  value="NO" >Off
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Show segment translation:</div>
                    <div class="tdInput">
                        <input type="radio" id="SegmentTranslationMouseOver_Y" name="SegmentTranslationMouseOver"  value="YES" >On
                        <input type="radio" id="SegmentTranslationMouseOver_N" name="SegmentTranslationMouseOver"  value="NO" >Off&nbsp;
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Segment translation as popup:</div>
                    <div class="tdInput">
                        <input type="radio" id="SegmentTranslationAsPopup_Y" name="SegmentTranslationAsPopup"  value="YES" >On
                        <input type="radio" id="SegmentTranslationAsPopup_N" name="SegmentTranslationAsPopup"  value="NO" >Off&nbsp;
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Segment translation character:</div>
                    <div class="tdInput">
                        <input type="text" name="SegmentTranslationCharacter" id="SegmentTranslationCharacter"
                               style="width: 5%" size="5">
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Table of contents:</div>
                    <div class="tdInput">
                        <input type="radio" id="TableOfContents_Y" name="TableOfContents"  value="YES" >On
                        <input type="radio" id="TableOfContents_N" name="TableOfContents"  value="NO" >Off&nbsp;
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Coloured words:</div>
                    <div class="tdInput">
                        <input type="radio" id="ColouredWords_Y" name="ColouredWords"  value="YES" >On
                        <input type="radio" id="ColouredWords_N" name="ColouredWords"  value="NO" >Off&nbsp;
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Translated words in colour:</div>
                    <div class="tdInput">
                        <input type="radio" id="TranslatedWordsInColour_Y" name="TranslatedWordsInColour"  value="YES" >Yes
                        <input type="radio" id="TranslatedWordsInColour_N" name="TranslatedWordsInColour"  value="NO" >No &nbsp;
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Audio words in red colour:</div>
                    <div class="tdInput">
                        <input type="radio" id="AudioWordsInColour_Y" name="AudioWordsInColour"  value="YES" >On
                        <input type="radio" id="AudioWordsInColour_N" name="AudioWordsInColour"  value="NO" >Off &nbsp;
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Max examples per information page:</div>
                    <div class="tdInput">
                        <input type="radio" id="MaxExamplesPerWordPage_5"  name="MaxExamplesPerWordPage"  value="5" >5
                        <input type="radio" id="MaxExamplesPerWordPage_10" name="MaxExamplesPerWordPage"  value="10" >10 &nbsp;
                        <input type="radio" id="MaxExamplesPerWordPage_15" name="MaxExamplesPerWordPage"  value="15" >15
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Font:</div>
                    <div class="tdInput">
                        <input type="radio" id="Font_serif"  name="Font"  value="serif">
                        <span style="font-family: Serif; font-size: 1em">serif</span>&nbsp;&nbsp;&nbsp;&nbsp;
                        <input type="radio" id="Font_sans-serif" name="Font"  value="sans-serif">
                        <span style="font-family: Sans-Serif; font-size: 1em">sans-serif</span>&nbsp;&nbsp;&nbsp;&nbsp;
                        <input type="radio" id="Font_monospace"  name="Font"  value="monospace">
                        <span style="font-family: monospace; font-size: 1em">monospace</span>
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Font size:</div>
                    <div class="tdInput">
                        <input type="radio" id="Font_xx_small"  name="FontSize"  value="xx-small">xx-small
                        <input type="radio" id="Font_x_small"  name="FontSize"  value="x-small">x-small
                        <input type="radio" id="Font_small"  name="FontSize"  value="small">small
                        <input type="radio" id="Font_medium"  name="FontSize"  value="medium">medium
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle"></div>
                    <div class="tdInput">
                        <input type="radio" id="Font_large"  name="FontSize"  value="large">large
                        <input type="radio" id="Font_x_large"  name="FontSize"  value="x-large">x-large
                        <input type="radio" id="Font_xx_large"  name="FontSize"  value="xx-large">xx-large
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Frequency lists in:</div>
                    <div class="tdInput">
                        <input type="radio" id="FrequencyListsInMainText_Y" name="FrequencyListsInMainText"  value="YES" >Main text page
                        <input type="radio" id="FrequencyListsInMainText_N" name="FrequencyListsInMainText"  value="NO" >Information page
                    </div>
                </div>
            </div>
            <div id="SaveFirstStepInfo" class="table">
                <div class="tr">
                    <div class="tdButton">
                        <input type="button"  id="OperationButt" name="OperationButt" title="Save your reading history"
                               value="Save" onclick="addReadingHistory()" >
                    </div>
                </div>
            </div>
        </div>
        <!--END OF FIRST TAB-->
        <!--****************************************************************-->
        <!--START OF SECOND TAB, ie result of first phase compile-->
        <div class="table" id="addResource" style="display: none">
            <div id="MandatoryDiv" class="table">
                <div class="tr">
                    <div class="tdTXT">Add a text to reading history:
                        <?php echo $drp_ContentResources; ?>
                        <input type="button"  id="AddHistoryRes" name="AddHistoryRes" title="Add this text to your reading history"
                               value="Add" onclick="addHistoryResource()" >
                    </div>
                </div>
            </div>
        </div>
        <!--END OF SECOND TAB-->
        <!--****************************************************************-->
    </form>
    </div>

    <?php echo $backwardButton; ?>
</div>