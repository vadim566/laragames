<?php
require_once '../config.php';
require_once '../shared-modules/extra_modules.php';
require_once 'email_to_creator.class.php';
require_once 'content_visit.class.php';
require_once 'content_comment.class.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";
$relatedPage = basename(__FILE__) . "::" . $task;

switch ($task)
{
    case "send_email_to_creator":
        send_email_to_creator();

    case "save_content_cover_picture":
        save_content_cover_picture();

    case "save_content_profile_picture":
        save_content_profile_picture();

    case "search_all_content":
        search_all_content();

    case "content_web_page_visit":
        content_web_page_visit();

    case "save_comment":
        save_comment();
}

function search_content_for_feed($where = "", $whereParam = array())
{
    $query = "select c.*, l1.LanguageName l1Name, l2.LanguageName l2Name from Contents c
                      left join Languages l1 on (c.L1ID = l1.LanguageID)
                      left join Languages l2 on (c.L2ID = l2.LanguageID) ";

    $query .= (!empty($where)) ? " where " . $where : "";
    $query .= " order by c.ContentID desc ";

    if(!empty($whereParam))
        $temp = PdoDataAccess::runquery($query, $whereParam);
    else
        $temp = PdoDataAccess::runquery($query);

    return $temp;
}

function search_content_segment_for_feed($where = "1 = 1", $whereParam = array())
{
    $query = "select * from ContentSegments 
    			where ContentID in (select ContentID from Contents where " . $where . " ) 
                and SegmentOrder between 1 and 5
                order by ContentID";
    if(!empty($whereParam))
        $temp = PdoDataAccess::runquery($query, $whereParam);
    else
        $temp = PdoDataAccess::runquery($query);

    $result = array();
    for($i = 0; $i < count($temp); $i++)
    {
        $result[$temp[$i]["ContentID"]][$temp[$i]["SegmentOrder"]]["SegmentInL1"] = $temp[$i]["SegmentInL1"];
        $result[$temp[$i]["ContentID"]][$temp[$i]["SegmentOrder"]]["SegmentInL2"] = $temp[$i]["SegmentInL2"];
        $result[$temp[$i]["ContentID"]][$temp[$i]["SegmentOrder"]]["RecordingFileName"] = $temp[$i]["RecordingFileName"];
    }
    return $result;
}

function search_content_segment($where = "1 = 1", $whereParam = array())
{
    $query = "select * from ContentSegments c
                where " . $where . "  
                and SegmentOrder between 1 and 15 order by SegmentOrder";
    if(!empty($whereParam))
        $temp = PdoDataAccess::runquery($query, $whereParam);
    else
        $temp = PdoDataAccess::runquery($query);

    return $temp;
}

function search_all_content()
{
    $query = "select c.ContentID, replace(c.ContentName, '_', ' ') cName,ContentStatus, webAddress, ProfilePictureExtension,
                    UserName, UserID, l1.LanguageName l1Name, l2.LanguageName l2Name 
                    from Contents c
                      left join Languages l1 on (c.L1ID = l1.LanguageID)
                      left join Languages l2 on (c.L2ID = l2.LanguageID) 
                      left join Accounts a on (c.CreatorID = a.UserID) 
                    where c.IsDeleted = 'NO' and c.ContentStatus = 'pages' and c.ParentID is null ";

    if(!empty($_REQUEST["ContentSearchText"]))
    {
        $whereParam = array(":searchText" => "%" . $_REQUEST["ContentSearchText"] . "%");
        $query .=  " and (c.ContentName like :searchText or l1.LanguageName like :searchText or l2.LanguageName like :searchText)";
    }
    $query .= " order by c.ContentID desc ";

    if(!empty($whereParam))
        $contentList = PdoDataAccess::runquery($query, $whereParam);
    else
        $contentList = PdoDataAccess::runquery($query);

    $html = "<div class='row'>";
    for($i = 0; $i < count($contentList); $i++) {
        $contentInfo = $contentList[$i];
        if (empty($contentInfo["ProfilePictureExtension"]))
            $contentProfileImgSrc = "../images/resources/cmp-icon.png";
        else
            $contentProfileImgSrc = image_to_base64(Repository . 'lara-content-profile-picture/' .
                $contentInfo["ContentID"] . '.' . $contentInfo["ProfilePictureExtension"]);
        $html .= "<div class='col-lg-3 col-md-4 col-sm-6'><div class='company_profile_info'><div class='company-up-info'>";
        $html .= "<img src=" . $contentProfileImgSrc . " width='90' height='90'>";
        $html .= "<h3>" . $contentInfo['cName'] . "</h3>";
        $html .= "<h4><a href='../user/user-profile.php?id=" . $contentInfo['UserID'] . "'>" . $contentInfo['UserName'] . "</a></h4>";
        $html .= "<h4>" . $contentInfo['l1Name'] . " - " . $contentInfo['l2Name'] . "</h4>";
        $html .= "<ul>";
        $html .= "<li><a href='#' title='' class='follow'>Follow</a></li>";
        $html .= "<li><a href='#' title='' class='mail-creator' onclick='open_email_to_creator_box(\"" . $contentInfo['ContentID']. "\")'>
                    <i class='fa fa-envelope'></i></a></li>";
        $html .= "</ul></div>";
        $html .= "<a href='content_profile.php?Q1=" . $contentInfo['ContentID'] . "' title='' class='view-more-pro'>View Profile</a>";
        $html .= "</div><!--company_profile_info end--></div>";
    }
    $html .= "</div>";

    echo $html;
    die();
}

function lara_content_full_select($where = "", $whereParam = array())
{
    $query = "select c.ContentID, c.ContentName, c.ContentStatus, c.webAddress, 
                     c.CoverPictureExtension, c.ProfilePictureExtension, c.CreatorID, 
                     a.UserName, 
                     l1.LanguageName l1Name, l2.LanguageName l2Name, 
                     u.FirstName, u.LastName, u.DisplayName, u.ProfilePictureExtension CreatorProfilePictureExtension
                    from Contents c
                      left join Languages l1 on (c.L1ID = l1.LanguageID)
                      left join Languages l2 on (c.L2ID = l2.LanguageID) 
                      left join Accounts a on (c.CreatorID = a.UserID)                       
                      left join Users u on (c.CreatorID = u.UserID) ";
    $query .= (!empty($where)) ? " where " . $where : "";
    $query .= " order by c.ContentID desc ";

    if(!empty($whereParam))
        $temp = PdoDataAccess::runquery($query, $whereParam);
    else
        $temp = PdoDataAccess::runquery($query);

    return $temp[0];
}

function send_email_to_creator()
{
    global $relatedPage;
    $resultArray[0] = $_REQUEST["ContentID"];
    $resultArray[1] = "notSetYet";

    $emailObj = new email_to_creator();
    $emailObj->EmailBody = $_REQUEST["EmailBody"];
    $emailObj->set_sender_info($_REQUEST["From"]);
    $emailObj->set_receiver_info($_REQUEST["ContentID"]);
    $emailObj->When = date("Y-m-d H:i:s");
    $emailObj->insert();

    $to = $emailObj->To;
    $subject = $emailObj->EmailSubject;
    $message = "<p>" . $emailObj->EmailBody . "</p>";

    $headers = "From: CALLector community team <hanieh.habibi@unige.ch>\r\n";
    $headers .= "Reply-To: hanieh.habibi@unige.ch\r\n";
    $headers .= "Content-type: text/html\r\n";

    $resultArray[1] = mail($to, $subject, $message, $headers) ? "succeed" : "failure";
    kill_process($relatedPage, $resultArray);
}

function save_content_cover_picture()
{
    global $relatedPage;
    $resultArray = array( 1=>"notSetYet");

    if (!isset($_REQUEST["ContentID"]))
        kill_process($relatedPage, $resultArray, "Failure_UserNotDetected");
    else
        $resultArray[0] = $_REQUEST["ContentID"];

    if ($_FILES['ContentCoverPictureFile']['error'] == 1 )
        kill_process($relatedPage, $resultArray, "Failure_ContentCoverPictureFileError");

    //checking format and encoding for uploaded files
    if (!file_is_uploaded('ContentCoverPictureFile'))
        kill_process($relatedPage, $resultArray, "Failure_ContentCoverPictureFileSendingError");

    $fileExtension = file_extension_is_valid('ContentCoverPictureFile', array('jpg', 'jpeg', 'gif', 'png'));
    if ($fileExtension == "notValid")
        kill_process($relatedPage, $resultArray, "Failure_ContentCoverPictureFileTypeError");

    $fileName = $_REQUEST["ContentID"] . "." . $fileExtension;
    $fileDir = Repository . "lara-content-cover-picture/";
    $file = $_FILES['ContentCoverPictureFile'];
    if (!upload_file($fileName, $fileDir, $file))
        kill_process($relatedPage, $resultArray, "Failure_ContentCoverPictureFileUploadError");

    $query = "update Contents set CoverPictureExtension = :extension  where ContentID = :contentID";
    $params = array(":extension" => $fileExtension, ":contentID" => $_REQUEST["ContentID"]);

    PdoDataAccess::runquery($query, $params);
    kill_process($relatedPage, $resultArray, "Succeed");
}

function save_content_profile_picture()
{
    global $relatedPage;
    $resultArray = array( 1=>"notSetYet");

    if (!isset($_REQUEST["ContentID"]))
        kill_process($relatedPage, $resultArray, "Failure_UserNotDetected");
    else
        $resultArray[0] = $_REQUEST["ContentID"];

    if ($_FILES['ContentProfilePictureFile']['error'] == 1 )
        kill_process($relatedPage, $resultArray, "Failure_ContentProfilePictureFileError");

    //checking format and encoding for uploaded files
    if (!file_is_uploaded('ContentProfilePictureFile'))
        kill_process($relatedPage, $resultArray, "Failure_ContentProfilePictureFileSendingError");

    $fileExtension = file_extension_is_valid('ContentProfilePictureFile', array('jpg', 'jpeg', 'gif', 'png'));
    if ($fileExtension == "notValid")
        kill_process($relatedPage, $resultArray, "Failure_ContentProfilePictureFileTypeError");

    $fileName = $_REQUEST["ContentID"] . "." . $fileExtension;
    $fileDir = Repository . "lara-content-profile-picture/";
    $file = $_FILES['ContentProfilePictureFile'];
    if (!upload_file($fileName, $fileDir, $file))
        kill_process($relatedPage, $resultArray, "Failure_ContentProfilePictureFileUploadError");

    $query = "update Contents set ProfilePictureExtension = :extension  where ContentID = :contentID";
    $params = array(":extension" => $fileExtension, ":contentID" => $_REQUEST["ContentID"]);

    PdoDataAccess::runquery($query, $params);
    kill_process($relatedPage, $resultArray, "Succeed");
}

function content_profile_page_visit()
{
    $visitObj = new content_visit();
    $visitObj->ContentID = $_REQUEST['Q1'];
    $visitObj->UserID = $_SESSION[SessionIndex['UserID']];
    $visitObj->VisitType = "snPage";
    $visitObj->VisitDate = date("Y-m-d H:i:s");

    $visitObj->insert();
}

function content_web_page_visit()
 {
     $visitObj = new content_visit();
     $visitObj->ContentID = $_REQUEST['contentID'];
     $visitObj->UserID = $_SESSION[SessionIndex['UserID']];
     $visitObj->VisitType = "webPage";
     $visitObj->VisitDate = date("Y-m-d H:i:s");

     $visitObj->insert();
 }

function save_comment()
{
    global $relatedPage;
    $resultArray = array(1 => "notSetYet");

    if (!isset($_REQUEST["ContentID"]))
        kill_process($relatedPage, $resultArray, "Failure_UserNotDetected");
    else
        $resultArray[0] = $_REQUEST["ContentID"];

    $commentObj = new content_comment();
    $commentObj->ContentID = $_REQUEST['ContentID'];
    $commentObj->UserID = $_SESSION[SessionIndex['UserID']];
    $commentObj->CommentText = $_REQUEST['CommentText'];
    $commentObj->CommentTime = date("Y-m-d H:i:s");
    $commentObj->insert();

    kill_process($relatedPage, $resultArray, "Succeed");
}


