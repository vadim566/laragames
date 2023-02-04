<?php

require_once '../config.php';

function obj_to_js($object, $jsObjName)
{
    $objArr = get_object_vars($object);
    //$retVal = "<script>var ". $jsObjName." = " . json_encode($objArr). "</script>";
    return json_encode($objArr);
}

function ldt_user_drop_box($headerInfo, $dropBoxName, $selectedID = -1)
{
    $url = 'https://regulus.unige.ch/litedevtools/server/api/account/allUsers';

    $header = [
        "Authorization: " . $headerInfo
    ];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
    curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
    curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
    curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 100);

    $result = curl_exec ($ch);

    if ($result === FALSE) {
        curl_close($ch);
        return "something wrong here";
    }

    $ldtUsers = json_decode($result, true);
    asort($ldtUsers, SORT_STRING | SORT_FLAG_CASE | SORT_NATURAL);
    $ldtUsersKeys = array_keys($ldtUsers);

    $retStr = "<select name=$dropBoxName id=$dropBoxName>";
    $retStr .= "<option value=-1";
    if($selectedID == -1)
        $retStr .= " selected ";
    $retStr .= ">Anonymous</option>";

    for ($i = 0; $i < count($ldtUsers); $i++) {
        $retStr .= "<option value='" . $ldtUsersKeys[$i] . "'";
        if($ldtUsersKeys[$i] == $selectedID)
            $retStr .= " selected ";
        $retStr .= " >";
        $retStr .= $ldtUsers[$ldtUsersKeys[$i]];
        $retStr .= "</option>";
    }

    $retStr .= "</select>";
    curl_close($ch);
    return $retStr;
}

function get_ldt_username($headerInfo, $userID)
{

    $url = 'https://regulus.unige.ch/litedevtools/server/api/account/userName/' . $userID;

    $header = [
        "Authorization: " . $headerInfo
    ];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
    curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
    curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
    curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 100);

    $result = curl_exec ($ch);


    if ($result === FALSE) {
        curl_close($ch);
        return "something wrong here";
    }
    else
    {
        curl_close($ch);
        return substr($result, 1, strlen($result)-2);
    }
}

function get_ldt_userID($headerInfo, $userName)
{
    $url = 'https://regulus.unige.ch/litedevtools/server/api/account/userId/' . $userName;

    $header = [
        "Authorization: " . $headerInfo
    ];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
    curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
    curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
    curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 100);

    $result = curl_exec ($ch);

    if ($result === FALSE) {
        curl_close($ch);
        return "something wrong here";
    }
    else
    {
        curl_close($ch);
        return substr($result, 1, strlen($result)-2);
    }
}

function get_countries_list($dropBoxName, $hasExtraRow, $selectedID = -1)
{
    $retStr = "<select name=$dropBoxName id=$dropBoxName 
                       class='form-control' style='-webkit-appearance: menulist-button;'>";
    if($hasExtraRow)
    {
        $retStr .= "<option value=-1 ";
        if($selectedID == -1)
            $retStr .= " selected ";
        $retStr .= ">---</option>";
    }

    $query = "select * from Countries order by CountryName";
    $temp = PdoDataAccess::runquery($query);
    for($i=0; $i<count($temp); $i++)
    {
        $retStr .= "<option value='" . $temp[$i]["CountryID"] . "'" ;
        if($temp[$i]["CountryID"] == $selectedID)
            $retStr .= " selected ";
        $retStr .= " >" . $temp[$i]["CountryName"] . " (" . $temp[$i]["CountryAbr"] . ")" . "</option>";
    }
    $retStr .= "</select>";
    return $retStr;
}

function get_genders_list($dropBoxName, $hasExtraRow, $selectedID = -1)
{
    $retStr = "<select name=$dropBoxName id=$dropBoxName 
                       class='form-control' style='-webkit-appearance: menulist-button;'>";
    if($hasExtraRow)
    {
        $retStr .= "<option value=-1 ";
        if($selectedID == -1)
            $retStr .= " selected ";
        $retStr .= ">---</option>";
    }

    $query = "select * from Genders order by GenderID";
    $temp = PdoDataAccess::runquery($query);
    for($i=0; $i<count($temp); $i++)
    {
        $retStr .= "<option value='" . $temp[$i]["GenderID"] . "'" ;
        if($temp[$i]["GenderID"] == $selectedID)
            $retStr .= " selected ";
        $retStr .= " >" . $temp[$i]["GenderTitle"] . "</option>";
    }
    $retStr .= "</select>";
    return $retStr;
}

function kill_process($relatedPage, $resultArray, $resultArrayMsg = "")
{
    if($resultArrayMsg != "")
        $resultArray[1] = $resultArrayMsg;
    if(!user_activity_log($relatedPage, $resultArray))
        $resultArray[1] .= " _ LoggingActivityFailed";
    $result = json_encode($resultArray);
    echo $result;
    die();
}

function user_activity_log($relatedPage, $resultArray)
{
    $activityLogObj = array(
        "LogData" => $resultArray[1],
        "LogDateTime" => (new DateTime('now'))->format('Y-m-d H:i:s'),
        "RelatedID" => $resultArray[0],
        "RelatedPage" => $relatedPage,
        "UserID" => isset($_SESSION[SessionIndex['UserID']]) ? $_SESSION[SessionIndex['UserID']] : "-1" ,
        "IPAddress" => $_SERVER['REMOTE_ADDR']);

    if(PdoDataAccess::insert("UserActivitiesLogs", $activityLogObj))
        return true;
    return false;
}

function file_is_uploaded($fileName)
{
    if(file_exists($_FILES[$fileName]['tmp_name']) && is_uploaded_file($_FILES[$fileName]['tmp_name']))
        return true;
    return false;
}

function file_extension_is_valid($fileName, $validExt)
{
    $ext = pathinfo($_FILES[$fileName]["name"], PATHINFO_EXTENSION);
    if(in_array($ext, $validExt))
        return $ext;
    return "notValid";
}

function upload_file($fileName, $fileDir, $file)
{
    $fp = fopen($fileDir . $fileName, "w");
    if ($fp === false)
        return false;

    if(!fwrite($fp, fread(fopen($file ['tmp_name'], 'r'), $file['size'])))
        return false;

    fclose($fp);
    return true;
}

function image_to_base64($path)
{
    $type = pathinfo($path, PATHINFO_EXTENSION);
    $data = file_get_contents($path);
    return 'data:image/' . $type . ';base64,' . base64_encode($data);
}
