<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/19/2020
 * Time: 10:25 PM
 */

require_once "../class/PasswordReset.class.php";

$selector = $_REQUEST["selector"];
$validator = $_REQUEST["validator"];

if(empty($selector) || empty($validator))
{
    echo "We could not validate your request";
    die();
}
else {
    if (ctype_xdigit($selector) !== false || ctype_xdigit($validator) !== false) {
        $where = " PasswordResetSelector = :selector ";
        $whereParam = array(":selector" => $selector);

        $res = PasswordReset::SearchPasswordResetInfo($where, $whereParam);
        if (count($res) == 0)
        {
            echo "<h1>No user is registered for this email.</h1>";
        } else {
            $userName = $res[0]["UserName"];
            echo "<h1>Reset password for lara user " . $userName . "</h1>";
?>
            <div id="rpMsg" class="resetPassInstruction"></div>

            <form class="form-newPass" method="post" id="NewPassForm" name="NewPassForm">

                <input type="hidden" id="selector" name="selector" value="<?php echo $selector; ?>">
                <input type="hidden" id="validator" name="validator" value="<?php echo $validator; ?>">
                <input type="password" name="Password" id="Password" placeholder="New password">
                <input type="password" name="PwdRepeat" id="PwdRepeat" placeholder="Repeat password">
                <button type="button" name="NewPassSubmit" id="NewPassSubmit" onclick="UpdatePassword()">Update
                    Password
                </button>
            </form>

            <?php
        }
    }
}
?>