<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 6/6/2019
 * Time: 05:45 PM
 */


require_once '../Config.php';
require_once '../data/Content.data.php';
require_once '../class/Content.class.php';
require_once '../class/FlashcardsSet.class.php';
require_once '../class/FlashcardSetMember.class.php';
require_once '../class/FlashcardResponse.class.php';
require_once '../SharedModules/ExtraModules.class.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "generateFlashcardSet":
        generateFlashcardSet();

    case "saveResponse":
        saveResponse();

    case "getResponseSummary":
        getResponseSummary();

    case "getFlashcardLog":
        getFlashcardLog();

    case "repeatLastTest":
        repeatLastTest();
}

function generateFlashcardSet()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = -1;

    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["contentID"]);
    $contentResult = Content::SearchContent($where, $whereParam);

    $resourcesDir = ContentTmpDirectory . $contentResult[0]["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $contentResult[0]["DirName"]  . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;
    $corpusDir = LaraContentDir . $contentResult[0]["DirName"] . "/" . SubDirNames["corpus"] . "/";

    $createBackupDIRRes = ExtraModules::CreateDir($backupDir);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(FlashcardRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }

    $flashcardsFileName = "flashcard_" . $_REQUEST["userID"] . ".json";
    if(!makeFlashcards($flashcardsFileName, $resourcesDir, $backupDir, $corpusDir))
    {
        $resultArray[0]["resultMsg"] = "GenerateFailed";
        ExtraModules::UserActivityLog(FlashcardRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    $resultArray[0]["id"] = saveFlashcardsInDB($flashcardsFileName, $resourcesDir);
    $resultArray[0]["resultMsg"] = "GenerateSucceed";
    ExtraModules::UserActivityLog(FlashcardRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function makeFlashcards($flashcardsFileName, $resourcesDir, $backupDir, $corpusDir)
{
    $bashFile = $resourcesDir .  $_REQUEST["userID"] . "_makeFlashcard.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv  . " " . TreeTaggerEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py make_flashcards " .
        $corpusDir . "local_config.json " .
        $_REQUEST["flashcardType"] . " " .
        $_REQUEST["flashcardsNumber"] . " " .
        $_REQUEST["flashcardLevel"] . " " .
        $_REQUEST["flashcardWordType"] . " " .
        $_REQUEST["userID"] . " " .
        $_REQUEST["strategy"] . " " .
        $_REQUEST["contentID"] . " " .
        $resourcesDir . $flashcardsFileName . " 2>&1";

    fwrite($fp, $command);
    ExtraModules::BackupFile($resourcesDir . $flashcardsFileName,
                             $backupDir . date("Ymd_His") . "_" . $flashcardsFileName);
    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $_REQUEST["contentID"], FlashcardRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $_REQUEST["contentID"], FlashcardRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function saveFlashcardsInDB($flashcardsFileName, $resourcesDir)
{
    $flashCardsSetObj = new FlashcardsSet();
    $flashCardsSetObj->ContentID = $_REQUEST["contentID"];
    $flashCardsSetObj->TestCreatorID = $_REQUEST["userID"];
    $flashCardsSetObj->TestDate = (new DateTime('now'))->format('Y-m-d H:i:s');
    $flashCardsSetObj->NumberOfTests = $_REQUEST["flashcardsNumber"];
    $flashCardsSetObj->FlashcardType = $_REQUEST["flashcardType"];
    $flashCardsSetObj->FlashcardLevel = $_REQUEST["flashcardLevel"];
    $flashCardsSetObj->FlashcardWordType = $_REQUEST["flashcardWordType"];
    $flashCardsSetObj->insert();
    $where = "ContentID = :contentID and TestCreatorID = :userID";
    $whereParam = array(":contentID" => $flashCardsSetObj->ContentID, ":userID" => $flashCardsSetObj->TestCreatorID);
    $flashcardsSetID = FlashcardsSet::lastID($where, $whereParam);
    $flashcardsSetJsonData = json_decode(file_get_contents($resourcesDir . $flashcardsFileName), true);

    //reformat Python json
    $membersArray[] = array("FlashcardsSetID","FlashcardNo","FlashcardPart","FlashcardContent","FlashcardType");

    for($i = 0; $i < count($flashcardsSetJsonData); $i++)
    {
        $membersArray[] = array($flashcardsSetID,
                                $i + 1,
                                "answer",
                                $flashcardsSetJsonData[$i]["answer"]["value"],
                                $flashcardsSetJsonData[$i]["answer"]["type"]);
        $membersArray[] = array($flashcardsSetID,
                                $i + 1,
                                "question",
                                $flashcardsSetJsonData[$i]["question"]["value"],
                                $flashcardsSetJsonData[$i]["question"]["type"]);
        $membersArray[] = array($flashcardsSetID,
                                $i + 1,
                                "multimedia_context",
                                $flashcardsSetJsonData[$i]["multimedia_context"]["value"],
                                $flashcardsSetJsonData[$i]["multimedia_context"]["type"]);
        $membersArray[] = array($flashcardsSetID,
                                $i + 1,
                                "text_context",
                                $flashcardsSetJsonData[$i]["text_context"]["value"],
                                $flashcardsSetJsonData[$i]["text_context"]["type"]);
        for($j = 0; $j < count($flashcardsSetJsonData[$i]["distractors"]); $j++)
                $membersArray[] = array($flashcardsSetID,
                                        $i + 1,
                                        "distractors",
                                        $flashcardsSetJsonData[$i]["distractors"][$j]["value"],
                                        $flashcardsSetJsonData[$i]["distractors"][$j]["type"]);
    }

    //put flashcards array in json
    $processedFlashcardsJson = $resourcesDir . "flashcard_after_" . $_REQUEST["userID"] . ".json";
    file_put_contents( $processedFlashcardsJson, json_encode($membersArray, JSON_PRETTY_PRINT));
    //put flashcards json in csv
    $flashCardCsv = $resourcesDir . "flashcard_after_" . $_REQUEST["userID"] . ".csv";
    $bashFile = $resourcesDir . "/flashcardsToCSV.txt";
    $flashcardToCSV = ExtraModules::JsonToCsv($bashFile, $flashCardCsv,"", $processedFlashcardsJson, $_REQUEST["contentID"]);
    //put flashcards csv in table
    if($flashcardToCSV)
    {
        FlashcardSetMember::insertFlashcardSetMembers($flashCardCsv);
        return $flashcardsSetID;
    }
    else
    {
        $resultArray[0]["id"] = $flashcardsSetID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToFlashcardMembers";
        ExtraModules::UserActivityLog(FlashcardRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

function saveResponse()
{
    $flashCardResponseObj = new FlashcardResponse();
    $flashCardResponseObj->FlashcardsSetID = $_REQUEST["setID"];
    $flashCardResponseObj->FlashcardNo = $_REQUEST["flashcardNo"];
    $flashCardResponseObj->FlashcardSetMemberID = $_REQUEST["responseID"];
    $flashCardResponseObj->ExaminerID = $_SESSION[SessionIndex['UserID']];
    $flashCardResponseObj->insert();

    $resultArray[0]["id"] = $_REQUEST["responseID"];;
    $resultArray[0]["resultMsg"] = "FlashcardResponseSaved";
    ExtraModules::UserActivityLog(FlashcardRelatedPage, $resultArray);
    getResponseSummary(true);
}

function getResponseSummary($justCurrentScore = false)
{
    if(!$justCurrentScore)
    {
        $scoreTitle = "Total score : ";
        $responseSummaryRes = FlashcardResponse::getResponseSummary($_REQUEST["setID"]);

        $responseSummaryTable = "<table border='1' style='width: 70%'>" ;
        $responseSummaryTable .= "<tr>
                        <th style='width: 10%'>Card number</th>
                        <th style='width: 40%;'>Question</th>
                        <th style='width: 30%'>Your answer</th>
                        <th style='width: 20%'>Result</th>
                        </tr>" ;
        if(count($responseSummaryRes) > 0)
        {
            for($i = 0; $i < count($responseSummaryRes); $i++)
            {
                $responseSummaryTable .= "<tr>";
                $responseSummaryTable .=  "<td>" . $responseSummaryRes[$i]["FlashcardNo"] . "</td>"  ;
                $responseSummaryTable .=  "<td>" . $responseSummaryRes[$i]["question"] . "</td>"  ;
                $responseSummaryTable .=  "<td>" . $responseSummaryRes[$i]["answer"] . "</td>"  ;
                $responseSummaryTable .=  "<td>" . $responseSummaryRes[$i]["answerStatus"] . "</td>"  ;
                $responseSummaryTable .= "</tr>";
            }
        }
        $responseSummaryTable .= "</table>" ;
    }
    else
    {
        $responseSummaryTable = "";
        $scoreTitle = "Current score : ";
    }

    $where = " FlashcardsSetID = :setID";
    $whereParam = array(":setID" => $_REQUEST["setID"]);
    $numberOfTests = FlashcardSetMember::getNumberOfQuestions($where, $whereParam);
    $testMaxScore = $numberOfTests * 3;
    $answeredFlashcards = FlashcardResponse::AnsweredFlashcardsInSet($_REQUEST["setID"]);

    if(count($answeredFlashcards) > 0)
    {
        $totalScore = 0;
        for($i = 0; $i < count($answeredFlashcards); $i++)
        {
            $FlashcardNo = $answeredFlashcards[$i][0];
            $totalScore += FlashcardResponse::getFlashcardScore($_REQUEST["setID"], $FlashcardNo);
        }
        $responseSummaryTable .= "<table style='width: 70%'>" ;
        $responseSummaryTable .= "<tr>";
        $responseSummaryTable .= "<td style='width: 35%'>" . $scoreTitle . "</td>";
        $responseSummaryTable .= "<td style='width: 65%'>" . $totalScore . "/" . $testMaxScore . "</td>";
        $responseSummaryTable .= "</tr></table>";
    }

    echo $responseSummaryTable;
    die();
}

function getFlashcardLog()
{
    $where = " where 1=1";
    $whereParam = array();

    if(!empty($_REQUEST["StartDate"]))
    {
        $where .= " and TestDate > :startDate";
        $whereParam[":startDate"] = $_REQUEST["StartDate"];
    }

    if(!empty($_REQUEST["EndDate"]))
    {
        $where .= " and TestDate < :endDate";
        $whereParam[":endDate"] = $_REQUEST["EndDate"];
    }

    if($_REQUEST["ContentID"] != -1)
    {
        $where .= " and ContentID = :contentID";
        $whereParam[":contentID"] = $_REQUEST["ContentID"];
    }

    $flashcardsLogRes = FlashcardsSet::SearchFlashcardLogs($where, $whereParam);


    $LogHistory = "<table border='1'>" ;
    $LogHistory .= "<tr>
                        <th style='width: 5%'>#</th>
                        <th style='width: 45%;'>user</th>
                        <th style='width: 50%'>time</th>
                        </tr>" ;
    if(count($flashcardsLogRes) > 0)
    {
        for($i = 0; $i < count($flashcardsLogRes); $i++)
        {
            $LogHistory .= "<tr>";
            $LogHistory .=  "<td>" . ($i+1) . "</td>"  ;
            $LogHistory .=  "<td>" . $flashcardsLogRes[$i]["UserName"] . "</td>"  ;
            $LogHistory .=  "<td><span onclick='showResponsesSummary(" . $flashcardsLogRes[$i]["FlashcardsSetID"] . ")'> " . $flashcardsLogRes[$i]["TestDate"] . "</span></td>"  ;
            $LogHistory .= "</tr>";
        }
    }
    $LogHistory .= "</table>" ;

    echo $LogHistory;
    die();
}

function repeatLastTest()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = -1;

    $where = " where ContentID = :cID and TestCreatorID = :tcID";
    $whereParam = array(":cID" => $_REQUEST["contentID"] , ":tcID" => $_REQUEST["userID"]);
    $lastFlashcardID = FlashcardsSet::GetLastFlashcardID($where, $whereParam);

    if($lastFlashcardID == -1)
    {
        $resultArray[0]["resultMsg"] = "NoPrvTest";
    }
    else
    {
        $resultArray[0]["id"] = $lastFlashcardID;
        $resultArray[0]["resultMsg"] = "SuccessfullyFoundPrvTest";
    }

    ExtraModules::UserActivityLog(FlashcardRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}