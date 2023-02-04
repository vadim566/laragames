<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 28/08/2020
 * Time: 12:23 PM
 */

require_once 'account.class.php';
require_once 'password_reset.class.php';
require_once '../user/user.data.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";
$relatedPage = basename(__FILE__) . "::" . $task;

switch ($task)
{
    case "user_sign_up":
        user_sign_up();

    case "user_login":
        user_login();

    case "user_logout":
        user_logout();

    case "reset_password_request":
        reset_password_request();

    case "update_password":
        update_password();
}

function user_sign_up()
{
    global $relatedPage;
    $resultArray[0] = -1;
    $resultArray[1] = "notSetYet";

    $userObj = fill_account($_POST);

    $resultArray[1] = $res = $userObj->check_duplication();
    if($res == "NoDuplication")
    {
        $userObj->PasswordSalt = generate_random_salt();
        $userObj->Password = password_hash($userObj->Password . $userObj->PasswordSalt, PASSWORD_DEFAULT);
        $userObj->insert();

        $where = " Username = :userName";
        $whereParam = array(":userName" => $_POST["UserName"]);
        $userRes = account::search_account($where, $whereParam);
        $resultArray[0] = $userRes[0]["UserID"];
    }
    kill_process($relatedPage, $resultArray);
}

function user_login()
{
    global $relatedPage;
    $resultArray[0] = -1;
    $resultArray[1] = "notSetYet";

    $where = " Username = :userNameEmail or lower(Email) = lower(:userNameEmail)";
    $whereParam = array(":userNameEmail" => $_POST["UserNameEmail"]);
    $res = account::search_account($where, $whereParam);

    if (count($res) == 0)
    {
        $resultArray[1] = "UserNotFound";
    }
    else if (!password_verify(  $_POST["UserPassword"] . $res[0]["PasswordSalt"] , $res[0]["Password"]))
    {
        $resultArray[0] = $res[0]["UserID"];
        $resultArray[1] = "WrongPassword";
    }
    else {
        start_session($res[0]);
        $resultArray[0] = $res[0]["UserID"];
        $resultArray[1] = "LoginNow";
    }
    kill_process($relatedPage, $resultArray);
}

function fill_account($src)
{
    $accountObj = new account();
    PdoDataAccess::FillObjectByArray($accountObj, $src);
    return $accountObj;
}

function generate_random_salt() {
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $randomString = '';
    for ($i = 0; $i < 10; $i++) {
        $randomString .= $characters[rand(0, strlen($characters) - 1)];
    }
    return $randomString;
}

function user_logout()
{
    session_start();
    session_unset();
    session_destroy();
    echo true;
    die();
}

function reset_password_request()
{
    global $relatedPage;
    $resultArray[0] = -1;
    $resultArray[1] = "notSetYet";

    $userEmail = $_REQUEST["Email"];
    if(account::email_exists($userEmail))
    {
        $where = " lower(Email) = lower(:email)";
        $whereParam = array(":email" => $userEmail);
        $res = account::search_account($where, $whereParam);
        $resultArray[0] = $res[0]["UserID"];

        $where = " PasswordResetEmail = :email";
        $whereParam = array(":email" => $userEmail);

        password_reset::delete($where, $whereParam);

        $selector = bin2hex(random_bytes(8));
        $token = random_bytes(32);

        $passResObj = new password_reset();
        $passResObj->PasswordResetEmail = $userEmail;
        $passResObj->PasswordResetSelector = $selector;
        $passResObj->PasswordResetToken = password_hash($token, PASSWORD_DEFAULT);
        $passResObj->PasswordResetExpires = date("U") + 1800;
        $passResObj->insert();

        $createNewPassURL = WebAddress . "account/create_new_password.php?selector=" . $selector . "&validator=" . bin2hex($token);

        $to = $userEmail;
        $subject = "Reset your Lara portal password";
        $message = "<p>We receive a password reset request. The link to reset your password is below. 
                    If you did not make this request, you can ignore this email.</p>";
        $message .= "<br>Here is your password reset link: </br>";
        $message .=  "<a href = '" . $createNewPassURL . "' target = 'blank'>" . $createNewPassURL . "</a></p>";

        $headers = "From: laraTeam <hanieh.habibi@unige.ch>\r\n";
        $headers .= "Reply-To: hanieh.habibi@unige.ch\r\n";
        $headers .= "Content-type: text/html\r\n";

        $resultArray[1] = mail($to, $subject, $message, $headers) ? "succeed" : "failure";
    }
    else
    {
        $resultArray[1] = "emailNotExists";
    }
    kill_process($relatedPage, $resultArray);
}

function update_password()
{
    global $relatedPage;
    $resultArray[0] = -1;
    $resultArray[1] = "notSetYet";

    $selector = $_REQUEST["selector"];
    $validator = $_REQUEST["validator"];
    $newPassword = $_REQUEST["Password"];

    $currentTime = date("U");

    $where = " PasswordResetSelector = :selector and PasswordResetExpires >= :now";
    $whereParam = array(":selector" => $selector, ":now" => $currentTime);

    $res = password_reset::search_password_reset_info($where, $whereParam);

    if (count($res) == 0)
    {
        $resultArray[1] = "NoResetRequest";
    }
    else {
        $resultArray[0] = $res[0]["UserID"];
        $tokenBin = hex2bin($validator);
        $tokenCheck = password_verify($tokenBin, $res[0]["PasswordResetToken"]);

        if($tokenCheck === false)
        {
            $resultArray[1] = "NotValidLink";
        }
        else
        {
            $userObj = new account();
            $userObj->Email = $res[0]["PasswordResetEmail"];
            $userObj->PasswordSalt = generate_random_salt();
            $userObj->Password = password_hash($newPassword . $userObj->PasswordSalt, PASSWORD_DEFAULT);
            $userObj->update_password();
            $resultArray[1] = "LoginWithNewPass";
        }
    }
    kill_process($relatedPage, $resultArray);
}
