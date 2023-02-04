<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 28/08/2020
 * Time: 12:23 PM
 */

require_once 'user.class.php';
require_once '../shared-modules/extra_modules.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";
$relatedPage = basename(__FILE__) . "::" . $task;

switch ($task)
{
    case "save_user_profile":
        save_user_profile();

    case "save_cover_picture":
        save_cover_picture();

    case "save_profile_picture":
        save_profile_picture();
}

function save_user_profile()
{
    global $relatedPage;
    $resultArray = array(1=>"notSetYet");

    $userObj = fill_user($_REQUEST);
    if ($userObj->UserID == null)
        kill_process($relatedPage, $resultArray, "Failure_UserNotDetected");
     else
        $resultArray[0] = $userObj->UserID;

    $userWhere = " UserID = :uID";
    $userWhereParam = array(":uID" => $userObj->UserID);
    if(user::user_has_profile_info($userWhere, $userWhereParam))
    {
        if($userObj->update())
            $resultArray[1] = "UpdateSucceed";
        else
            $resultArray[1] = "UpdateFailure";
    }
    else
    {
        if($userObj->insert())
            $resultArray[1] = "InsertSucceed";
        else
            $resultArray[1] = "InsertFailure";
    }
    reload_session($userObj->UserID);
    kill_process($relatedPage, $resultArray);
}

function fill_user($src)
{
    $userObj = new user();
    PdoDataAccess::FillObjectByArray($userObj, $src);
    return $userObj;
}

function make_empty_user($userID)
{
    $userObj = new user();
    $userObj->UserID = $userID;
    $userObj->FirstName = "";
    $userObj->MiddleName = "";
    $userObj->LastName = "";
    $userObj->DisplayName = "--";
    $userObj->GenderID = "-1";
    $userObj->CountryID = "-1";
    $userObj->BirthDate = "";
    $userObj->WebsiteAddress = "";
    $userObj->Interests = "";
    $userObj->AboutMe = "";
    $userObj->CoverPictureExtension = "";
    $userObj->ProfilePictureExtension = "";
    $userObj->EmailNotification = "no";
    return $userObj;
}

function save_cover_picture()
{
    global $relatedPage;
    $resultArray = array(1=>"notSetYet");

    $userObj = fill_user($_REQUEST);
    if ($userObj->UserID == null)
        kill_process($relatedPage, $resultArray, "Failure_UserNotDetected");
     else
        $resultArray[0] = $userObj->UserID;


    if ($_FILES['CoverPictureFile']['error'] == 1 )
        kill_process($relatedPage, $resultArray, "Failure_CoverPictureFileError");

    //checking format and encoding for uploaded files
    if (!file_is_uploaded('CoverPictureFile'))
        kill_process($relatedPage, $resultArray, "Failure_CoverPictureFileSendingError");

    $fileExtension = file_extension_is_valid('CoverPictureFile', array('jpg', 'jpeg', 'gif', 'png'));
    if ($fileExtension == "notValid")
        kill_process($relatedPage, $resultArray, "Failure_CoverPictureFileTypeError");

    $userObj->CoverPictureExtension = $fileExtension;
    $fileName = $userObj->UserID . "." . $userObj->CoverPictureExtension;
    $fileDir = Repository . "user-cover-picture/";
    $file = $_FILES['CoverPictureFile'];
    if (!upload_file($fileName, $fileDir, $file))
        kill_process($relatedPage, $resultArray, "Failure_CoverPictureFileUploadError");

    $userObj->update();
    reload_session($userObj->UserID);
    kill_process($relatedPage, $resultArray, "Succeed");
}

function save_profile_picture()
{
    global $relatedPage;
    $resultArray = array(1=>"notSetYet");
    $userObj = fill_user($_REQUEST);
    if ($userObj->UserID == null)
        kill_process($relatedPage, $resultArray, "Failure_UserNotDetected");
    else
        $resultArray[0] = $userObj->UserID;
    if ($_FILES['ProfilePictureFile']['error'] == 1 )
        kill_process($relatedPage, $resultArray, "Failure_ProfilePictureFileError");
    //checking format and encoding for uploaded files
    if (!file_is_uploaded('ProfilePictureFile'))
        kill_process($relatedPage, $resultArray, "Failure_ProfilePictureFileSendingError");
    $fileExtension = file_extension_is_valid('ProfilePictureFile', array('jpg', 'jpeg', 'gif', 'png'));
    if ($fileExtension == "notValid")
        kill_process($relatedPage, $resultArray, "Failure_ProfilePictureFileTypeError");
    $userObj->ProfilePictureExtension = $fileExtension;
    $fileName = $userObj->UserID . "." . $userObj->ProfilePictureExtension;
    $fileDir = Repository . "user-profile-picture/";
    $file = $_FILES['ProfilePictureFile'];
    if (!upload_file($fileName, $fileDir, $file))
        kill_process($relatedPage, $resultArray, "Failure_ProfilePictureFileUploadError");
    $userObj->update();
    reload_session($userObj->UserID);
    kill_process($relatedPage, $resultArray, "Succeed");
}

function start_session($accountInfo)
{
    $userWhere = " UserID = :uID";
    $userWhereParam = array(":uID" => $accountInfo['UserID']);
    $userInfo = user::search_user($userWhere, $userWhereParam);
    if(!empty($userInfo))
        $userObj = fill_user($userInfo);
    else
        $userObj = make_empty_user($_SESSION[SessionIndex['UserID']]);

    session_start();
    $_SESSION[SessionIndex['UserID']] = $accountInfo['UserID'];
    $_SESSION[SessionIndex['UserName']] = $accountInfo['UserName'];
    $_SESSION[SessionIndex['UserEmail']] = $accountInfo['Email'];
    $_SESSION[SessionIndex['UserInfo']] = (array) $userObj ;
    return true;
}

function reload_session($UserID)
{
    $userWhere = " UserID = :uID";
    $userWhereParam = array(":uID" => $UserID);
    $userInfo = user::search_user($userWhere, $userWhereParam);
    if(!empty($userInfo))
        $userObj = fill_user($userInfo);
    else
        $userObj = make_empty_user($_SESSION[SessionIndex['UserID']]);

    $_SESSION[SessionIndex['UserInfo']] = (array) $userObj ;
    return true;
}