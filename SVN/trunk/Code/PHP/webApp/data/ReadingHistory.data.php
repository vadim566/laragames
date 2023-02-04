<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/21/2019
 * Time: 12:16 PM
 */

require_once '../Config.php';
require_once '../SharedModules/ExtraModules.class.php';
require_once '../SharedModules/LogConstants.php';
require_once '../class/ReadingHistory.class.php';
require_once '../class/Language.class.php';
require_once '../class/Account.class.php';
require_once '../class/DistributedResource.class.php';
require_once '../class/DistributedResourcePage.class.php';
require_once '../class/ReadingHistoryResource.class.php';
require_once '../class/ExternalCommandsLogs.class.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "AddReadingHistory":
        AddReadingHistory();

    case "AddHistoryResource":
        AddHistoryResource();

    case "GetHistoryResources":
        GetHistoryResources();

    case "GetReadingHistoryLog":
        GetReadingHistoryLog();

    case "GoToNextPage":
        GoToNextPage();

    case "DeleteHistory":
        DeleteHistory();

}

function AddReadingHistory()
{
    //json response is created using this array
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = -1;

    $R_H_Obj = FillItems($_REQUEST);

    //add or update content to database
    if ($R_H_Obj->ReadingHistoryID == null)
    {
        //create new data raw in database for new content
        $R_H_Obj->insert();
        $R_H_Obj->ReadingHistoryID = $R_H_Obj->lastID();
        $resultArray[0]["id"] = $R_H_Obj->ReadingHistoryID;
        //creating the folder structure for the saved content
        $R_H_DirName = ReadingHistoryDir . $R_H_Obj->UserID . "_" . $R_H_Obj->ReadingHistoryID;
        $createDIRRes = ExtraModules::CreateDir($R_H_DirName);
        if ($createDIRRes == "CreateDIRFailed")
        {
            $resultArray[0]["resultMsg"] = "CreateDIRFailedAddReadingHistory";
        }
        else
        {
            if(CreateReadingConfigFile($R_H_Obj))
            {
                $resultArray[0]["resultMsg"] = "NewReadingHistoryIsReady";
            }
            else
            {
                $resultArray[0]["resultMsg"] = "FailedToCreateConfigFile";
            }
        }
    }
    else
    {
        $resultArray[0]["id"] = $R_H_Obj->ReadingHistoryID;

        //compare ServerSide and ClientSide
        $preferencesHasChanged = PreferencesHasChanged($R_H_Obj);
        //if any changes in preferences ->
        if($preferencesHasChanged)
        {
            $R_H_Obj->update();
            //regenerate the config file
            if(CreateReadingConfigFile($R_H_Obj))
            {
                //if there is any assigned Resource for this history ->
                if($R_H_Obj->hasAssignedResource())
                {
                    //call CompileReadingHistory function
                    $compileRes = CompileReadingHistory($R_H_Obj);
                    if($compileRes)
                    {
                        $resultArray[0]["resultMsg"] = "RecompileSucceedRH";
                    }
                    else
                    {
                        $resultArray[0]["resultMsg"] = "RecompileFailureRH";
                    }
                }
                else
                {
                    $resultArray[0]["resultMsg"] = "NewPreferencesSaved";
                }
            }
            else
            {
                $resultArray[0]["resultMsg"] = "FailedToCreateConfigFile";
            }
        }
        else
        {
            $resultArray[0]["resultMsg"] = "NoChangeInPreferences";
        }
    }

    ExtraModules::UserActivityLog(HistoryRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function AddHistoryResource()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_GET["ReadingHistoryID"];

    $where = " ReadingHistoryID = :readingHistoryID and ResourceID = :resourceID ";
    $whereParam = array(":readingHistoryID" => $_GET["ReadingHistoryID"], ":resourceID" => $_GET["ResourceID"] );

    if(ReadingHistoryResource::CheckResourceDuplication($where, $whereParam) == false)
    {
        $resultArray[0]["resultMsg"] = "DuplicatedResource";
    }
    else
    {
        $R_H_R_Obj = new ReadingHistoryResource();
        $R_H_R_Obj->ReadingHistoryID = $_GET["ReadingHistoryID"];
        $R_H_R_Obj->ResourceID =  $_GET["ResourceID"];
        $R_H_R_Obj->LastReadPage = "1";
        $R_H_R_Obj->insert();

        $where = " ReadingHistoryID = :readingHistoryID";
        $whereParam = array(":readingHistoryID" => $_GET["ReadingHistoryID"]);
        $info = ReadingHistory::SearchReadingHistory($where, $whereParam);
        $R_H_Obj = FillItems($info[0]);

        if(CreateReadingConfigFile($R_H_Obj))
        {
            //call CompileReadingHistory function
            $compileRes = CompileReadingHistory($R_H_Obj);
            if($compileRes)
            {
                $resultArray[0]["resultMsg"] = "RecompileSucceedHR";
            }
            else
            {
                $resultArray[0]["resultMsg"] = "RecompileFailureHR";
            }
        }
        else
        {
            $resultArray[0]["resultMsg"] = "FailedToCreateConfigFile";
        }
    }
    ExtraModules::UserActivityLog(HistoryRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function GetHistoryResources()
{
    $where = " ReadingHistoryID = :readingHistoryID";
    $whereParam = array(":readingHistoryID" => $_GET["ReadingHistoryID"]);
    $info = ReadingHistory::SearchReadingHistory($where, $whereParam);
    $R_H_Obj = FillItems($info[0]);

    $where = " rhr.ReadingHistoryID = :readingHistoryID";
    $whereParam = array(":readingHistoryID" => $R_H_Obj->ReadingHistoryID);
    $temp = ReadingHistoryResource::SearchReadingHistoryResource($where, $whereParam);
    $ReadingHistory = "<table border='1'>" ;
    $ReadingHistory .= "<tr>
                        <th>Text name</th>
                        <th>On page</th>
                        <th>Continue reading</th>
                        </tr>" ;
    if(count($temp) > 0)
    {
        for($i = 0; $i < count($temp); $i++)
        {
            $ReadingHistory .= "<tr>";
            $ReadingHistory .=  "<td>" . $temp[$i]["ResourceName"] . "</td>"  ;
            $ReadingHistory .=  "<td>" . $temp[$i]["LastReadPage"] . "</td>"  ;
            if($temp[$i]["IsDeleted"] == "NO")
            {
                $ReadingHistory .=  "<td align='center'><img src='../img/read-icon.png' title='Read me' 
                               onclick='loadNavigatePage(".$temp[$i]["ReadingHistoryResourceID"].",".
                    $temp[$i]["LastReadPage"] . ");'/></td>"  ;
            }
            else
            {
                $ReadingHistory .=  "<td align='center'><img src='../img/forbidden-icon.png' title='Deleted by owner'/></td>"  ;
            }

            $ReadingHistory .= "</tr>";
        }
    }
    $ReadingHistory .= "</table>" ;

    echo $ReadingHistory;
    die();
}

function GoToNextPage()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ReadingHistoryResourceID"];

    $where = " ReadingHistoryResourceID = :readingHistoryResourceID and PageNumber = :pageNumber";
    $whereParam = array(":readingHistoryResourceID" => $_REQUEST["ReadingHistoryResourceID"],
                        ":pageNumber" => $_REQUEST["CurrentPage"]);
    $info = ReadingHistoryResource::FullSelect($where, $whereParam, false);
    $NextPage = $info[0]["PageNumber"] + 1;
    $resultArray[0]["nextPage"] = $NextPage;

    $where = " ResourceID = :resourceID";
    $whereParam = array(":resourceID" => $info[0]["ResourceID"]);

    $LastPageNumberOfResource = DistributedResourcePage::LastPageNumber($where, $whereParam); //pages in book.

    if ($LastPageNumberOfResource == $info[0]["PageNumber"])
    {
        $resultArray[0]["resultMsg"] = "NoNextPage" ;
    }
    else
    {
        if($NextPage <= $info[0]["LastReadPage"])
        {
            $resultArray[0]["resultMsg"] = "NextPageExists";
        }
        else
        {
            $where = " ReadingHistoryID = :readingHistoryID";
            $whereParam = array(":readingHistoryID" => $info[0]["ReadingHistoryID"]);
            $infoRH = ReadingHistory::SearchReadingHistory($where, $whereParam);
            $R_H_Obj = FillItems($infoRH[0]);

            if(CompileNextPage($R_H_Obj, $info[0]["ResourceID"]))
            {
                ReadingHistoryResource::LastReadPagePlus($info[0]["ReadingHistoryResourceID"]);
                if (CreateReadingConfigFile($R_H_Obj)) {
                    $resultArray[0]["resultMsg"] = "NewPageAdded";
                } else {
                    $resultArray[0]["resultMsg"] = "FailedToCreateNewConfigFile";
                }
            }
            else
            {
                $resultArray[0]["resultMsg"] = "FailedToAddNewPage";
            }
        }
    }
    ExtraModules::UserActivityLog(HistoryResourceRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function FillItems($src)
{
    $R_H_Obj = new ReadingHistory();
    PdoDataAccess::FillObjectByArray($R_H_Obj, $src);
    return $R_H_Obj;
}

function MakeEmptyHistory()
{
    $R_H_Obj = new ReadingHistory();
    $R_H_Obj->UserID = $_SESSION[SessionIndex['UserID']];
    $R_H_Obj->L1ID = -1;
    $R_H_Obj->L2ID = -1;
    $R_H_Obj->AudioMouseOver = 'YES';
    $R_H_Obj->WordTranslationMouseOver = 'YES';
    $R_H_Obj->SegmentTranslationMouseOver = 'YES';
    $R_H_Obj->SegmentTranslationAsPopup = 'NO';//new
    $R_H_Obj->TableOfContents = 'YES';
    $R_H_Obj->ColouredWords = 'YES';
    $R_H_Obj->AudioWordsInColour = 'NO';
    $R_H_Obj->TranslatedWordsInColour = 'NO';//new
    $R_H_Obj->MaxExamplesPerWordPage = '10';
    $R_H_Obj->Font = 'serif';
    $R_H_Obj->FrequencyListsInMainText = 'NO';
    $R_H_Obj->FontSize = "medium";
    $R_H_Obj->SegmentTranslationCharacter = "✎";//new

    return $R_H_Obj;
}

function PreferencesHasChanged($newHistoryObj)
{
    $where = " ReadingHistoryID = :readingHistoryID";
    $whereParam = array(":readingHistoryID" => $_REQUEST["ReadingHistoryID"]);
    $info = ReadingHistory::SearchReadingHistory($where, $whereParam);
    if(count($info) != 0)
    {
        $oldHistoryObj = FillItems($info[0]);
        if( $oldHistoryObj->ReadingHistoryName != $newHistoryObj->ReadingHistoryName ||
            $oldHistoryObj->L1ID != $newHistoryObj->L1ID ||
            $oldHistoryObj->L2ID != $newHistoryObj->L2ID ||
            $oldHistoryObj->AudioMouseOver != $newHistoryObj->AudioMouseOver ||
            $oldHistoryObj->WordTranslationMouseOver != $newHistoryObj->WordTranslationMouseOver ||
            $oldHistoryObj->SegmentTranslationMouseOver != $newHistoryObj->SegmentTranslationMouseOver ||
            $oldHistoryObj->SegmentTranslationAsPopup != $newHistoryObj->SegmentTranslationAsPopup ||
            $oldHistoryObj->TableOfContents != $newHistoryObj->TableOfContents ||
            $oldHistoryObj->ColouredWords != $newHistoryObj->ColouredWords ||
            $oldHistoryObj->AudioWordsInColour != $newHistoryObj->AudioWordsInColour ||
            $oldHistoryObj->TranslatedWordsInColour != $newHistoryObj->TranslatedWordsInColour ||
            $oldHistoryObj->MaxExamplesPerWordPage != $newHistoryObj->MaxExamplesPerWordPage ||
            $oldHistoryObj->Font != $newHistoryObj->Font ||
            $oldHistoryObj->FontSize != $newHistoryObj->FontSize ||
            $oldHistoryObj->SegmentTranslationCharacter != $newHistoryObj->SegmentTranslationCharacter ||
            $oldHistoryObj->FrequencyListsInMainText != $newHistoryObj->FrequencyListsInMainText )
        {
            return true;
        }
        return false;
    }

    return false;

}

function CreateReadingConfigFile($R_H_Obj)
{
    $R_H_ID = str_replace(" ", "_", $R_H_Obj->ReadingHistoryName)
      . "_" . $R_H_Obj->UserID . "_" . $R_H_Obj->ReadingHistoryID;
    $L1Name = Language::getLanguageName($R_H_Obj->L1ID);
    $L2Name = Language::getLanguageName($R_H_Obj->L2ID);
    $L2RTL = Language::isRightToLeft($R_H_Obj->L2ID);
    $R_H_DirName = ReadingHistoryDir . $R_H_Obj->UserID . "_" . $R_H_Obj->ReadingHistoryID;
    $ResourceFileAddress = $R_H_DirName . "/resources.json";
    CreateResourceFile($R_H_Obj, $ResourceFileAddress);

    $where = " rhr.ReadingHistoryID = :readingHistoryID";
    $whereParam = array(":readingHistoryID" => $R_H_Obj->ReadingHistoryID);
    $temp = $R_H_Obj->listOfHistoryResourcesForConfig($where, $whereParam);
    $ReadingHistory = "[" ;
    if(count($temp) > 0)
    {
        for($i = 0; $i < count($temp); $i++)
        {
            $ReadingHistory .=  $temp[$i]["HistoryResInfo"] .  ',' . "\n"  ;
        }
        $ReadingHistory = rtrim($ReadingHistory);
        $ReadingHistory = rtrim($ReadingHistory,",");
        $ReadingHistory .=   "\n"  ;
    }
    $ReadingHistory .= "]" ;

    $reading_config_data = '{';
    $reading_config_data .= '"id" : "' . $R_H_ID . '",';
    $reading_config_data .= '"l1" : "' . $L1Name . '",';
    $reading_config_data .= '"language" : "' . $L2Name . '",';
    if($L2RTL == "YES")
        $reading_config_data .= '"text_direction" : "rtl",';
    $reading_config_data .= '"resource_file" : "' . $ResourceFileAddress . '",';
    $reading_config_data .= '"reading_history" : ' . $ReadingHistory . ',';
    $reading_config_data .= '"html_style" : "new",';

    $reading_config_data .= '"audio_mouseover" : "' . strtolower($R_H_Obj->AudioMouseOver) . '",';
    $reading_config_data .= '"translation_mouseover" : "' . strtolower($R_H_Obj->WordTranslationMouseOver) . '",';
    $reading_config_data .= '"segment_translation_mouseover" : "' . strtolower($R_H_Obj->SegmentTranslationMouseOver) . '",';
    $reading_config_data .= '"segment_translation_as_popup" : "' . strtolower($R_H_Obj->SegmentTranslationAsPopup) . '",';
    if(!empty($R_H_Obj->SegmentTranslationCharacter))
        $reading_config_data .= '"segment_translation_character" : "' . $R_H_Obj->SegmentTranslationCharacter . '",';
    $reading_config_data .= '"allow_table_of_contents" : "' . strtolower($R_H_Obj->TableOfContents) . '",';
    $reading_config_data .= '"coloured_words" : "' . strtolower($R_H_Obj->ColouredWords) . '",';
    if ($R_H_Obj->AudioWordsInColour == 'YES')
        $reading_config_data .= '"audio_words_in_colour" : "red"';
    $reading_config_data .= '"translated_words_in_colour" : "' . strtolower($R_H_Obj->TranslatedWordsInColour) . '",';

    $reading_config_data .= '"max_examples_per_word_page":' . $R_H_Obj->MaxExamplesPerWordPage . ',';
    $reading_config_data .= '"font" : "' . strtolower($R_H_Obj->Font) . '",';
    $reading_config_data .= '"font_size" : "' . strtolower($R_H_Obj->FontSize) . '",';
    $reading_config_data .= '"frequency_lists_in_main_text_page" : "' . strtolower($R_H_Obj->FrequencyListsInMainText) . '",';
    $reading_config_data .= '"working_tmp_directory" : "' . rtrim(WorkingTmpDirectory, "/") . '",';
    $reading_config_data .= '"lara_tmp_directory" : "' . rtrim(WorkingTmpDirectory, "/") . '",';
    $reading_config_data .= '"compiled_directory" : "' . $R_H_DirName . '"';
    $reading_config_data .= '}';

    $local_config_file = $R_H_DirName  . '/reading_config.json';
    $handle = fopen($local_config_file, 'w') or die('Cannot open file:  ' . $local_config_file);
    fwrite($handle, $reading_config_data);
    fclose($handle);

    return true;
}

function CreateResourceFile($R_H_Obj, $resourceFile)
{
    $fp = fopen($resourceFile, "w");

    $where = " d1.L2ID = :l2id";
    $whereParam = array(":l2id" => $R_H_Obj->L2ID);
    $temp = DistributedResource::CreateAllResources($where, $whereParam);
    $fileContent = "{" . "\n";
    for($i = 0; $i < count($temp); $i++)
    {
        $fileContent .=  $temp[$i]["ResID"] . ' : ';
        $fileContent .=  $temp[$i]["ResInfo"] .  ',' . "\n"  ;
    }
    $fileContent = rtrim($fileContent);
    $fileContent = rtrim($fileContent,",");
    $fileContent .=   "\n"  ;
    $fileContent .= "}" ;
    fwrite($fp, $fileContent);
    fclose($fp);

    return true;
}

function CompileReadingHistory($R_H_Obj)
{
    $R_H_DirName = ReadingHistoryDir . $R_H_Obj->UserID . "_" . $R_H_Obj->ReadingHistoryID;
    $configFile = $R_H_DirName . "/reading_config.json";
    $replyFile = $R_H_DirName . "/reply.json";
    $bashFile = $R_H_DirName . "/CompileReadingHistory.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir .
        "lara_run_for_portal.py compile_reading_history  " . $configFile . " " . $replyFile ." 2>&1";
    fwrite($fp, $command);
    fclose($fp);


    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $R_H_Obj->ReadingHistoryID, HistoryRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $R_H_Obj->ReadingHistoryID, HistoryRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function CompileNextPage($R_H_Obj, $ReadingHistoryResourceID)
{
    $where = " d1.ResourceID = :resourceID";
    $whereParam = array(":resourceID" => $ReadingHistoryResourceID);
    $ResourcesInfo = DistributedResource::NextPageCompileResourceInfo($where, $whereParam);

    $R_H_DirName = ReadingHistoryDir . $R_H_Obj->UserID . "_" . $R_H_Obj->ReadingHistoryID;
    $configFile = $R_H_DirName . "/reading_config.json";
    $replyFile = $R_H_DirName . "/replyNextPage.json";
    $bashFile = $R_H_DirName . "/CompileNextPage.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir .
        "lara_run_for_portal.py compile_next_page_in_history  " . $ResourcesInfo . " " .
        $configFile . " " . $replyFile ." 2>&1";
    fwrite($fp, $command);
    fclose($fp);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $R_H_Obj->ReadingHistoryID, HistoryRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $R_H_Obj->ReadingHistoryID, HistoryRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function DeleteHistory()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $where = " ReadingHistoryID = :readingHistoryID";
    $whereParam = array(":readingHistoryID" => $_GET["ReadingHistoryID"]);
    $info = ReadingHistory::SearchReadingHistory($where, $whereParam);
    $R_H_Obj = FillItems($info[0]);

    $resultArray[0]["id"] = $R_H_Obj->ReadingHistoryID;

    $R_H_DirName = ReadingHistoryDir . $R_H_Obj->UserID . "_" . $R_H_Obj->ReadingHistoryID;
    ExtraModules::RemoveDir($R_H_DirName);

    $where = " ReadingHistoryID = :readingHistoryID";
    $whereParam = array(":readingHistoryID" => $R_H_Obj->ReadingHistoryID);

    ReadingHistory::delete($where, $whereParam);
    ReadingHistoryResource::delete($where, $whereParam);

    $resultArray[0]["resultMsg"] = "SuccessfulDeleteHistory";
    ExtraModules::UserActivityLog(HistoryRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function GetReadingHistoryLog()
{
    $where = "";
    $whereParam = array();

    if(!empty($_REQUEST["StartDate"]))
    {
        $where .= " and LogDateTime > :startDate";
        $whereParam[":startDate"] = $_REQUEST["StartDate"];
    }

    if(!empty($_REQUEST["EndDate"]))
    {
        $where .= " and LogDateTime < :endDate";
        $whereParam[":endDate"] = $_REQUEST["EndDate"];
    }

    if($_REQUEST["ReadingHistoryID"] != -1)
    {
        $where .= " and rh.ReadingHistoryID = :readingHistoryID";
        $whereParam[":readingHistoryID"] = $_REQUEST["ReadingHistoryID"];
    }
    else
    {
        $where .= " and rh.UserID = :uID";
        $whereParam[":uID"] = $_SESSION[SessionIndex['UserID']];
    }

    $readingLogRes = UserActivitiesLogs::SearchReadingLogs($where, $whereParam);


    $LogHistory = "<table border='1'>" ;
    $LogHistory .= "<tr>
                        <th style='width: 5%'>#</th>
                        <th style='width: 40%'>which</th>
                        <th style='width: 30%;'>what</th>
                        <th style='width: 25%'>when</th>
                        </tr>" ;
    if(count($readingLogRes) > 0)
    {
        for($i = 0; $i < count($readingLogRes); $i++)
        {
            $LogHistory .= "<tr>";
            $LogHistory .=  "<td>" . ($i+1) . "</td>"  ;
            $LogHistory .=  "<td>" . $readingLogRes[$i]["itemName"] . "</td>"  ;
            $LogHistory .=  "<td>" . $readingLogRes[$i]["LogData"] . "</td>"  ;
            $LogHistory .=  "<td>" . $readingLogRes[$i]["LogDateTime"] . "</td>"  ;
            $LogHistory .= "</tr>";
        }
    }
    $LogHistory .= "</table>" ;

    echo $LogHistory;
    die();
}