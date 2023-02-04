<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/11/2019
 * Time: 12:23 PM
 */

require_once '../class/Account.class.php';
require_once '../class/PasswordReset.class.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "userSignUp":
        userSignUp();

    case "userLogin":
        userLogin();

    case "userLogout":
        userLogout();

    case "ResetPasswordRequest":
        ResetPasswordRequest();

    case "UpdatePassword":
        UpdatePassword();
}

function userSignUp()
{
    $userObj = FillItems($_POST);

    $res = $userObj->checkDuplication();
    if($res == "NoDuplication")
    {
        $userObj->PasswordSalt = generateRandomSalt();
        $userObj->Password = password_hash($userObj->Password . $userObj->PasswordSalt, PASSWORD_DEFAULT);
        $userObj->insert();
    }

    echo $res;
    die();
}

function userLogin()
{
    $where = " Username = :userNameEmail or lower(Email) = lower(:userNameEmail)";
    $whereParam = array(":userNameEmail" => $_POST["UserNameEmail"]);
    $res = Account::UserLogin($where, $whereParam);

    if (count($res) == 0)
    {
        echo "UserNotFound";
    } else if (!password_verify(  $_POST["UserPassword"] . $res[0]["PasswordSalt"] , $res[0]["Password"]))
    {
        echo "WrongPassword";
    } else {
        session_start();
        $_SESSION[SessionIndex['UserID']] = $res[0]['UserID'];
        $_SESSION[SessionIndex['UserName']] = $res[0]['UserName'];
        echo "LoginNow";
    }
    die();
}

function FillItems($src)
{
    $userObj = new Account();
    PdoDataAccess::FillObjectByArray($userObj, $src);
    return $userObj;
}

function generateRandomSalt() {
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $randomString = '';
    for ($i = 0; $i < 10; $i++) {
        $randomString .= $characters[rand(0, strlen($characters) - 1)];
    }
    return $randomString;
}

function userLogout()
{
    session_start();
    session_unset();
    session_destroy();
    echo true;
    die();
}

function ResetPasswordRequest()
{
    $userEmail = $_REQUEST["Email"];
    if(Account::EmailExists($userEmail))
    {
        $where = " PasswordResetEmail = :email";
        $whereParam = array(":email" => $userEmail);

        PasswordReset::delete($where, $whereParam);

        $selector = bin2hex(random_bytes(8));
        $token = random_bytes(32);

        $passResObj = new PasswordReset();
        $passResObj->PasswordResetEmail = $userEmail;
        $passResObj->PasswordResetSelector = $selector;
        $passResObj->PasswordResetToken = password_hash($token, PASSWORD_DEFAULT);
        $passResObj->PasswordResetExpires = date("U") + 1800;
        $passResObj->insert();

        $createNewPassURL = WebAddress . "view/index.php?status=createNewPassword&selector=" . $selector . "&validator=" . bin2hex($token);

        $to = $userEmail;
        $subject = "Reset your Lara portal password";
        $message = "<p>We receive a password reset request. The link to reset your password is below. 
                    If you did not make this request, you can ignore this email.</p>";
        $message .= "<br>Here is your password reset link: </br>";
        $message .=  "<a href = '" . $createNewPassURL . "' target = 'blank'>" . $createNewPassURL . "</a></p>";

        $headers = "From: laraTeam <hanieh.habibi@unige.ch>\r\n";
        $headers .= "Reply-To: hanieh.habibi@unige.ch\r\n";
        $headers .= "Content-type: text/html\r\n";

        mail($to, $subject, $message, $headers);

        echo "succeed";
    }
    else
    {
        echo "emailNotExists";
    }
    die();
}

function UpdatePassword()
{
    $selector = $_REQUEST["selector"];
    $validator = $_REQUEST["validator"];
    $newPassword = $_REQUEST["Password"];

    $currentTime = date("U");

    $where = " PasswordResetSelector = :selector and PasswordResetExpires >= :now";
    $whereParam = array(":selector" => $selector, ":now" => $currentTime);

    $res = PasswordReset::SearchPasswordResetInfo($where, $whereParam);

    if (count($res) == 0)
    {
        echo "NoResetRequest";
        die();
    }
    else {
        $tokenBin = hex2bin($validator);
        $tokenCheck = password_verify($tokenBin, $res[0]["PasswordResetToken"]);

        if($tokenCheck === false)
        {
            echo "NotValidLink";
            die();
        }
        else
        {
            $userObj = new Account();
            $userObj->Email = $res[0]["PasswordResetEmail"];
            $userObj->PasswordSalt = generateRandomSalt();
            $userObj->Password = password_hash($newPassword . $userObj->PasswordSalt, PASSWORD_DEFAULT);
            $userObj->updatePassword();
            echo "LoginWithNewPass";
            die();
        }
    }
}
