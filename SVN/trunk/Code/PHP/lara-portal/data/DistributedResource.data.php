<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/6/2019
 * Time: 11:44 PM
 */

require_once '../Config.php';
require_once '../SharedModules/ExtraModules.class.php';
require_once '../SharedModules/LogConstants.php';
require_once '../class/DistributedResource.class.php';
require_once '../class/DistributedResourcePage.class.php';
require_once '../class/ExternalCommandsLogs.class.php';
require_once '../class/Content.class.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "AddDistributedResource":
        AddDistributedResource();

    case "DeleteResource":
        DeleteResource();
}

function FillDistributedResourceItems($src)
{
    $rscObj = new DistributedResource();
    PdoDataAccess::FillObjectByArray($rscObj, $src);
    return $rscObj;
}

function MakeEmptyResource()
{
    $obj = new DistributedResource();
    $obj->UserID = $_SESSION[SessionIndex['UserID']];
    $obj->ResourceName = "";
    $obj->WebAddress = "";
    $obj->ResourceType = "Content";
    $obj->ParentID = null;
    $obj->IsDeleted = "NO";
    return $obj;
}

function AddDistributedResource()
{
    //json response is created using this array
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = -1;

    $D_R_Obj = FillDistributedResourceItems($_REQUEST);
    $D_R_Obj->ResourceName = str_replace(" ","_",$D_R_Obj->ResourceName);

    //add or update content to database
    if ($D_R_Obj->ResourceID == null)
    {
        //create new data raw in database for new content
        $D_R_Obj->insert();
        $D_R_Obj->ResourceID = $D_R_Obj->lastID();
        $resultArray[0]["id"] = $D_R_Obj->ResourceID;
    }
    else
    {
        $resultArray[0]["id"] = $D_R_Obj->ResourceID;
        $D_R_Obj->update();
    }

    if($D_R_Obj->ResourceType == "Content")
    {
        if(!empty($_REQUEST["ResourceID"]))
        {
            $where = "ResourceID = :rID";
            $whereParam = array(":rID" => $D_R_Obj->ResourceID);
            DistributedResourcePage::delete($where, $whereParam);
        }
        if (!ExternalResourcePageNames($D_R_Obj))
        {
            ExtraModules::UserActivityLog(ResourceRelatedPage, $resultArray, "FailedToExtractPageNamesDR");
            ExtraModules::KillProcess($resultArray, "FailedToExtractPageNamesDR");
        }
    }
    ExtraModules::UserActivityLog(ResourceRelatedPage, $resultArray, "ResourceAdded");
    ExtraModules::KillProcess($resultArray, "ResourceAdded");
}

function ExternalResourcePageNames($rscObj)
{
    $dirName = $rscObj->ResourceID . '_' . $rscObj->ResourceName;
    if (is_dir(WorkingTmpDirectory . $dirName) === false) {
        mkdir(WorkingTmpDirectory . $dirName);
    }
    $compileDir = WorkingTmpDirectory . $dirName . "/";
    //1- create resource file
    $resourceFile = $compileDir . "resource.json";
    $fp = fopen($resourceFile, "w");
    $fileContent = '{"' . $rscObj->ResourceID . '_' . $rscObj->ResourceName . '" : ["' .
        $rscObj->WebAddress . '",""]}';
    fwrite($fp, $fileContent);
    fclose($fp);

    //2- create config file
    $configFile = $compileDir . "config.json";
    $fp = fopen($configFile, "w");
    $fileContent = '{"id": "abc", "reading_history": [], 
        "working_tmp_directory" : "' . WorkingTmpDirectory . '",
        "lara_tmp_directory" : "' . ContentTmpDirectory .'", 
        "compiled_directory" : "' . ContentTmpDirectory . '",

        "resource_file" : "' . $resourceFile .'"}';
    fwrite($fp, $fileContent);
    fclose($fp);

    //3- create and run bash command file
    $pageNamesFile = $compileDir . "pageNames.json";
    $bashFile = $compileDir . "PageNamesForResource.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py " .
        "get_page_names_for_resource  " . $rscObj->ResourceID . '_' . $rscObj->ResourceName .
        " " .  $configFile."  " . $pageNamesFile . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $rscObj->ResourceID, ResourceRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $rscObj->ResourceID, ResourceRelatedPage, $LogID);


    if($output == false)
        return false;

    //4- read json file
    $outputString = file_get_contents($pageNamesFile);
    $PagesNamesArray = json_decode($outputString, true); // decode the JSON into an associative array

    //6- save in DistributedResourcePages table
    for($i = 0; $i < count($PagesNamesArray); $i++)
    {
        $resourcePage = new DistributedResourcePage();
        $resourcePage->ResourceID = $rscObj->ResourceID;
        $resourcePage->PageNumber = $PagesNamesArray[$i]['page_number'];
        $resourcePage->PageName = $PagesNamesArray[$i]['base_file'];
        $resourcePage->insert();
    }

    return true;
}

function DeleteResource()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $where = " ResourceID = :resourceID";
    $whereParam = array(":resourceID" => $_GET["resourceID"]);
    $info = DistributedResource::SearchResource($where, $whereParam);
    $resourceObj = FillDistributedResourceItems($info[0]);

    $resultArray[0]["id"] = $resourceObj->ResourceID;

    DistributedResourcePage::delete($where, $whereParam);

    $FileNameParts = explode("/", $resourceObj->WebAddress);
    $dirName = DistributedDir . $FileNameParts[count($FileNameParts) - 1];
    ExtraModules::RemoveDir($dirName);


    $setPart = "IsDeleted = 'YES'";
    DistributedResource::PartialUpdate($setPart, $where, $whereParam);

    $setPart = "DistributedResourceID = NULL ";
    $wherePart = "DistributedResourceID = :drID";
    $params = array(":drID" => $_GET["resourceID"]);
    Content::PartialUpdate($setPart, $wherePart, $params);

    ExtraModules::UserActivityLog(ResourceRelatedPage, $resultArray, "SuccessfulDeleteResource");
    ExtraModules::KillProcess($resultArray, "SuccessfulDeleteResource");
}