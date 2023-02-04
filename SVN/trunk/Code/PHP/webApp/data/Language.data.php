<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 5/5/2019
 * Time: 01:42 AM
 */

require_once '../class/Language.class.php';
require_once '../SharedModules/ExtraModules.class.php';
require_once '../SharedModules/LogConstants.php';
require_once 'MultiWordExpressions.data.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "hasTreeTagger":
        hasTreeTagger();

    case "ImportLanguageMWE":
        ImportLanguageMWE();
}

function hasTreeTagger()
{
    $hasTreeTagger = Language::hasTreeTagger($_POST["LanguageID"]);
    echo $hasTreeTagger;
    die();
}

function FillLanguageItems()
{
    $langObj = new  Language();
    PdoDataAccess::FillObjectByArray($langObj, $_REQUEST);
    return $langObj;
}

function ImportLanguageMWE()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = -1;

    $mweDefFileName = $_REQUEST["fileName"];
    $languageID = $_REQUEST["languageID"];


    $LanguageName = Language::getLanguageName($languageID);
    $LangCorpusDirName = ContentTmpDirectory . $LanguageName . "/";
    $langDirRes = ExtraModules::CreateDir($LangCorpusDirName, SubDirNamesContentTmp);
    $txtSource = ContentTmpDirectory . $mweDefFileName;
    $txtDestinationDir = LaraContentDir . $LanguageName . '/' . SubDirNames["corpus"];
    ExtraModules::CreateDir($txtDestinationDir);
    $txtDestination = $txtDestinationDir . '/mwe_defs.txt';
    if(!rename($txtSource, $txtDestination))
    {
        $resultArray[0]["resultMsg"] = "FailedToCopyLexiconToDestination";
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

    $resourcesDir = $LangCorpusDirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;

    $bashFile = $resourcesDir . "/CheckMweDefs.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py check_mwe_defs " .
        $txtDestination . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $languageID, LanguageRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $languageID, LanguageRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
    {
        $resultArray[0]["resultMsg"] = "NotWellFormattedFile";
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

    $jsonFile = $resourcesDir . "/mwe_defs.json";
    $bashFile = $resourcesDir . "/MweTxtToJson.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py mwe_txt_defs_to_json " .
        $txtDestination . " " . $jsonFile . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $languageID, LanguageRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $languageID, LanguageRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
    {
        $resultArray[0]["resultMsg"] = "FailedConvertingToJSON";
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

    $mweFileJsonData = json_decode(file_get_contents($jsonFile), true);

    $mwes = $mweFileJsonData["mwes"];
    $classes = $mweFileJsonData["classes"];
    $transforms = $mweFileJsonData["transforms"];

    ReadLexiconMultiWords($mwes, $languageID, $resourcesDir);
    ReadLexiconClasses($classes, $languageID, $resourcesDir);
    ReadLexiconTransforms($transforms, $languageID, $resourcesDir);
    Language::UpdateMweLexiconStatus($languageID);
    $resultArray[0]["resultMsg"] = "SuccessfullyConvertingToJSON";
    ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}
?>