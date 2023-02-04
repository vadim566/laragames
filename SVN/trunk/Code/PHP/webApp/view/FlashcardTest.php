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
echo '<script type="text/javascript" charset="utf8" src="../js/Flashcards.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';
require_once '../class/FlashcardSetMember.class.php';
require_once '../class/FlashcardsSet.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please Login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

if(!isset($_REQUEST["setID"]) || !isset($_REQUEST["flashcardNo"]))
{
    echo "OOOOPS, flashcard not found. <br />";
    die();
}

$flashcardType = $_REQUEST["flashcardType"];
$nextFlashcard = $_REQUEST["flashcardNo"] + 1;
$prvFlashcard = $_REQUEST["flashcardNo"] - 1;

$where = " f.FlashcardsSetID = :setID and f.TestCreatorID = :uID";
$whereParam = array(":setID" => $_REQUEST["setID"], ":uID" => $_SESSION[SessionIndex['UserID']]);
$homePageAddress = FlashcardsSet::selectContentWebAddress($where, $whereParam);
$showContextStatus = FlashcardsSet::selectContextStatus($where, $whereParam);

$where = " FlashcardsSetID = :setID";
$whereParam = array(":setID" => $_REQUEST["setID"]);
$numberOfTests = FlashcardSetMember::getNumberOfQuestions($where, $whereParam);

$where = " FlashcardsSetID = :setID and FlashcardNo = :flashcardNo";
$whereParam = array(":setID" => $_REQUEST["setID"], ":flashcardNo" => $_REQUEST["flashcardNo"]);
$info = FlashcardSetMember::selectFlashcard($where, $whereParam);

$index = 0;
for($i = 0; $i < count($info); $i++)
{
    if($info[$i]["FlashcardPart"] == "question")
    {
        $questionType =  $info[$i]["FlashcardType"];
        $question = $questionType == 'raw_text' ?  $info[$i]["FlashcardContent"] : $homePageAddress . $info[$i]["FlashcardContent"];
    }
    else if($info[$i]["FlashcardPart"] == "answer")
    {
        $flashcardPartType = $info[$i]["FlashcardType"];
        $answers[$index][0] = $flashcardPartType == 'raw_text' ?  $info[$i]["FlashcardContent"] : $homePageAddress . $info[$i]["FlashcardContent"];
        $answers[$index][1] = "yes";
        $answers[$index][2] = $flashcardPartType;
        $answers[$index][3] = $info[$i]["FlashcardSetMemberID"];
        $index++;
    }
    else if($info[$i]["FlashcardPart"] == "distractors")
    {
        $flashcardPartType = $info[$i]["FlashcardType"];
        $answers[$index][0] = $flashcardPartType == 'raw_text' ?  $info[$i]["FlashcardContent"] : $homePageAddress . $info[$i]["FlashcardContent"];
        $answers[$index][1] = "no";
        $answers[$index][2] = $flashcardPartType;
        $answers[$index][3] = $info[$i]["FlashcardSetMemberID"];
        $index++;
    }
    else if($info[$i]["FlashcardPart"] == "text_context")
    {
        $textContext = $info[$i]["FlashcardContent"];
    }
    else if($info[$i]["FlashcardPart"] == "multimedia_context")
    {
        $multimediaContextType =  $info[$i]["FlashcardType"];
        $multimediaContext = $info[$i]["FlashcardContent"];
    }
}

shuffle($answers);
?>


<div class="HistoryResourceNav" style="width: 100%; height: 100%">
    <div class="table"  style="height: 100%">
        <!--question-->
        <div class="tr">
            <div class="tdTXT">
                <?php if($questionType == "raw_text") {
                    echo $question . "<br/>";
                } else if($questionType == "video_file_name") { ?>
                    <video width="320" height="240" controls muted autoplay>
                        <source src="<?php echo $question; ?>" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                <?php } else if($questionType == "audio_file_name") { ?>
                    <audio controls autoplay>
                        <source src="<?php echo $question; ?>" type="audio/mpeg">
                        Your browser does not support the audio tag.
                    </audio>
                <?php } ?>
            </div>
        </div>
        <!--hint-->
        <?php
            if($flashcardType == "lemma_translation_ask_l2" || $flashcardType == "token_translation_ask_l2" ||
                $flashcardType == "token_translation_ask_l2_audio" || $flashcardType == "lemma_translation_ask_l2_audio" ||
                $flashcardType == "signed_video_ask_l2") { ?>
                <div class="tr" ><div class="tdTXT"></div><br/></div>
                <div class="tr">
                    <div class="tdTitle"><img src="../img/first-aid-icon.png"></div>
                    <div class="tdInput">
                    <?php
                        if(($flashcardType == "lemma_translation_ask_l2" || $flashcardType == "token_translation_ask_l2") &&
                            $showContextStatus["ShowTextContext"] == "YES")
                            echo $textContext . "<br/>";
                        if($multimediaContext != "" && $showContextStatus["ShowMultimediaContext"] == "YES")
                        {
                            if($multimediaContextType == "audio_file_name")
                                echo '<audio controls>
                                        <source src=' . $homePageAddress . $multimediaContext . ' type="audio/mpeg">
                                        Your browser does not support the audio tag.
                                      </audio>';
                            else if($multimediaContextType == "video_file_name")
                                echo '<video width="320" height="240" controls muted>
                                        <source src=' . $homePageAddress . $multimediaContext . ' type="video/mp4">
                                        Your browser does not support the video tag.
                                      </video>';
                        }
                    ?>
                    </div>
                </div>
        <?php } else if($flashcardType == "sentence_with_gap" && $multimediaContext != "" && $showContextStatus["ShowMultimediaContext"] == "YES") {  ?>
            <div class="tr" ><div class="tdTXT"></div><br/></div>
            <div class="tr" id="audioForSentenceWithGap" style="display: none">
                <div class="tdTXT">
                    <?php
                        echo '<audio controls>
                            <source src=' . $homePageAddress . $multimediaContext . ' type="audio/mpeg">
                                Your browser does not support the audio tag.
                            </audio>';
                    ?>
                </div>
            </div>
        <?php } ?>
        <!--answers-->
        <?php for($i = 0;$i < 4;$i++) {?>
            <div class="tr">
                <div class="tdTXT">
                    <input type="radio" name="Answers" id="<?php echo $answers[$i][3]; ?>"
                           value="<?php echo $answers[$i][1]; ?>"
                           onclick="checkAnswer(<?php echo $_REQUEST["setID"] . "," . $nextFlashcard . ",'" . $flashcardType . "'," . $numberOfTests ; ?>)">
                    <?php if($answers[$i][2] == "raw_text") {
                        echo $answers[$i][0];
                    } else if($answers[$i][2] == "video_file_name") { ?>
                        <video width="320" height="240" controls muted>
                            <source src="<?php echo $answers[$i][0]; ?>" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    <?php } else if($answers[$i][2] == "audio_file_name") { ?>
                        <audio controls>
                            <source src="<?php echo $answers[$i][0]; ?>" type="audio/mpeg">
                            Your browser does not support the audio tag.
                        </audio>
                    <?php } ?>
                </div>
            </div>
        <?php } ?>
        <!--result-->
        <div class="tr" >
            <div class="tdTXT">
                <img src="../img/Accept-icon.png" id="Correct" hidden>
                <img src="../img/Button-Close-icon.png" id="Incorrect" hidden>
            </div>
        </div>
        <!--currentScore-->
        <div class="tr">
            <div class="tdTXT" id="currentScore">
            </div>
        </div>
        <!--navigation-->
        <div class="tr" align = "center">
            <div class="tdTXT">
                <img src="../img/sign-left-icon.png"
                     onclick="goToFlashcard(<?php echo $_REQUEST["setID"] . "," . $prvFlashcard .
                         ",'" . $flashcardType . "'," . $numberOfTests ; ?>)" >
                Flashcard <?php echo $_REQUEST["flashcardNo"]; ?>
                <img src="../img/sign-right-icon.png"
                     onclick="goToFlashcard(<?php echo $_REQUEST["setID"] . "," . $nextFlashcard .
                         ",'" . $flashcardType . "'," . $numberOfTests ; ?>)">
            </div>
        </div>
        <!--summary-->
        <div class="tr" id="ShowResponseSummary" style="display: none">
            <div class="tdTXT">
                <img src="../img/documents-icon.png" title="Show responses summary" onclick="showResponsesSummary(<?php echo $_REQUEST["setID"]; ?>)">
            </div>
        </div>
        <div class="tr">
            <div class="tdTXT" id="ResponseSummaryDiv" style="display: none">
            </div>
        </div>
    </div>
</div>