<?php
require_once __DIR__ . '/../SharedModules/PdoDataAccess.class.php';


$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "SaveEvaluation":
        SaveEvaluation();

    case "SaveUserComments":
        SaveUserComments();

}

function LanguageDropBox()
{
    $retStr = "<select  class='form-control' name='QuestionnaireID' id='QuestionnaireID' required>";
    $retStr .= "<option value=''>Please select the language..</option>";

    $query = "select * from EuroCallQuestionnaires where IsValid = 'yes' order by QuestionnaireLanguage ";
    $temp = PdoDataAccess::runquery($query);
    for($i=0; $i<count($temp); $i++)
        $retStr .= "<option value='" . $temp[$i]["QuestionnaireID"] . "'"  . " >" . $temp[$i]["QuestionnaireLanguage"] . "</option>";

    $retStr .= "</select>";
    return $retStr;
}

function InsertUser()
{
    $randomVal = rand(100,999);
    $Result["UserName"] = uniqid($randomVal);
    $Result["VersionOne"] = $randomVal  < 449 ? 'human' : 'tts';

    $userObj = (object) array("UserName" => $Result["UserName"],
                              "QuestionnaireID" => $_REQUEST["QuestionnaireID"],
                              "UserGender" => $_REQUEST["UserGender"],
                              "UserBirthYear" => $_REQUEST["UserBirthYear"],
                              "EducationBackground" => $_REQUEST["EducationBackground"],
                              "LanguageExpertise" => $_REQUEST["LanguageExpertise"],
                              "TeachingExperience" => $_REQUEST["TeachingExperience"],
                              "HearingImpairment" => $_REQUEST["HearingImpairment"],
                              "ReadingImpairment" => $_REQUEST["ReadingImpairment"],
                              "VersionOne" => $Result["VersionOne"],
                              "RegisterTime" => (new DateTime('now'))->format('Y-m-d H:i:s'),
                              "NameByUser" => $_REQUEST["NameByUser"]);
    if(PdoDataAccess::insert("EuroCallUsers", $userObj))
        return $Result;
    return false;
}

function GetUserID()
{
    $query = "select UserID from EuroCallUsers where UserName = :userName and QuestionnaireID = :qID ";
    $whereParam = array(":userName" => $_REQUEST["UserName"], ":qID" => $_REQUEST["QuestionnaireID"]);
    $temp = PdoDataAccess::runquery($query, $whereParam);
    return $temp[0]["UserID"];
}

function GetQuestions()
{
    $query = "select * from EuroCallSegments where QuestionnaireID = :id order by SegmentNumber";
    $whereParam = array(":id" => $_REQUEST["QuestionnaireID"]);
    return PdoDataAccess::runquery($query, $whereParam);
}

function SaveEvaluation()
{
    $userID = GetUserID();
    $segmentQuery = "insert into EuroCallSegmentResponses(UserID, SegmentID, UserResponse) values ";
    $versionQuery = "insert into EuroCallVersionResponses(UserID, AudioVersion, QuestionNumber, UserResponse) values ";
    foreach ($_REQUEST as $index => $val)
    {
        if(strpos($index, '**') !== false)
        {
            $pieces = explode('**', $index);
            $segmentID = $pieces[1];
            $userResponse = $val;
            $segmentQuery .= "('" . $userID . "','" . $segmentID . "','" . $userResponse . "'),";
        }
        elseif(strpos($index, '__') !== false)
        {
            $pieces = explode('__', $index);
            $audioVersion = $pieces[0];
            $questionNumber = $pieces[1];
            $userResponse = $val;
            $versionQuery .= "('" . $userID . "','" . $audioVersion . "','" . $questionNumber . "','"  . $userResponse . "'),";
        }
    }
    $ExitTime = (new DateTime('now'))->format('Y-m-d H:i:s');
    $overallVersionQuery = "insert into EuroCallVersionOverallResponses(UserID, OverallV1, OverallV2, ExitTime) values('" .
        $userID . "','" . $_REQUEST["OverallV1"] . "','" . $_REQUEST["OverallV2"] . "','" . $ExitTime . "')";

    PdoDataAccess::runquery(substr($segmentQuery, 0, -1));
    PdoDataAccess::runquery(substr($versionQuery, 0, -1));
    PdoDataAccess::runquery($overallVersionQuery);
    die();
}

function SaveUserComments()
{
    print_r($_REQUEST);
    echo "***" . $_REQUEST["UserComments"];
    if(empty($_REQUEST["UserComments"]))
        die();
    $userID = GetUserID();
    $commentQuery = "insert into EuroCallUserComments(UserID, UserComments) values ('" . $userID . "','" . $_REQUEST["UserComments"] . "')";
    echo $commentQuery;
    PdoDataAccess::runquery($commentQuery);
    die();
}

function Report()
{
    $query = "SELECT u.NameByUser, u.UserID uID, q.QuestionnaireLanguage, UserGender, UserBirthYear, LanguageExpertise, TeachingExperience,
                sr.UserID segEval, o.OverallV1, o.OverallV2, c.UserID comments, RegisterTime, ExitTime   
            FROM EuroCallUsers u 
            left join (SELECT UserID FROM EuroCallSegmentResponses group by userID) sr on (u.UserID = sr.UserID) 
            left join EuroCallVersionOverallResponses o on (u.UserID = o.UserID)
            left join EuroCallUserComments c on (u.UserID = c.UserID)
            left join EuroCallQuestionnaires q on (u.QuestionnaireID = q.QuestionnaireID)
            where  q.IsValid = 'yes'
            order by QuestionnaireLanguage, u.UserID desc ";
    return PdoDataAccess::runquery($query);
}

function SegmentResponses()
{
    $query = "SELECT q.QuestionnaireLanguage, u.UserID, u.UserGender, u.UserBirthYear, u.EducationBackground, u.LanguageExpertise, u.TeachingExperience, 
                      u.HearingImpairment, u.ReadingImpairment, u.VersionOne, SegmentText, UserResponse 
                FROM EuroCallSegmentResponses sr
                    left join EuroCallSegments s on (sr.SegmentID = s.SegmentID)
                    left join EuroCallUsers u on (sr.UserID = u.UserID)
                    left join EuroCallQuestionnaires q on (u.QuestionnaireID = q.QuestionnaireID)
                    where q .IsValid = 'yes' order by u.QuestionnaireID";

    return PdoDataAccess::runquery($query);
}

function VersionOverallResponses()
{
    $query = "SELECT q.QuestionnaireLanguage, u.UserID, u.UserGender, u.UserBirthYear, u.EducationBackground, u.LanguageExpertise, u.TeachingExperience, 
                        u.HearingImpairment, u.ReadingImpairment, u.VersionOne,  OverallV1, OverallV2, UserComments, u.RegisterTime, ExitTime
                         FROM  EuroCallVersionOverallResponses o
                         left join EuroCallUserComments c on (o.UserID = c.UserID)
                        left join EuroCallUsers u on (o.UserID = u.UserID)
                        left join EuroCallQuestionnaires q on (u.QuestionnaireID = q.QuestionnaireID)
                   where q.IsValid = 'yes' order by UserID";

    return PdoDataAccess::runquery($query);
}

function VersionResponses()
{
    $query = "SELECT q.QuestionnaireLanguage, r.UserID, r.AudioVersion, r.QuestionNumber, r.UserResponse 
                    FROM EuroCallVersionResponses r 
                    left join EuroCallUsers u on (r.UserID = u.UserID)
                    left join EuroCallQuestionnaires q on (u.QuestionnaireID = q.QuestionnaireID)
                    where q.IsValid = 'yes'";

    return PdoDataAccess::runquery($query);
}