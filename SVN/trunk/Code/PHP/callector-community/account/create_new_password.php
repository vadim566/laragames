
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Callector community</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="" />
    <meta name="keywords" content="" />
    <link rel="stylesheet" type="text/css" href="../css/animate.css">
    <link rel="stylesheet" type="text/css" href="../css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="../css/line-awesome.css">
    <link rel="stylesheet" type="text/css" href="../css/line-awesome-font-awesome.min.css">
    <link href="../vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" type="text/css" href="../css/font-awesome.min.css">
    <link rel="stylesheet" type="text/css" href="../lib/slick/slick.css">
    <link rel="stylesheet" type="text/css" href="../lib/slick/slick-theme.css">
    <link rel="stylesheet" type="text/css" href="../css/style.css">
    <link rel="stylesheet" type="text/css" href="../css/responsive.css">
</head>

<?php
require_once "../config.php";
require_once "password_reset.class.php";

$selector = $_REQUEST["selector"];
$validator = $_REQUEST["validator"];
$status = "";

if(empty($selector) || empty($validator))
{
    $status = "NotValid";
}
else {
    if (ctype_xdigit($selector) !== false || ctype_xdigit($validator) !== false) {
        $where = " PasswordResetSelector = :selector ";
        $whereParam = array(":selector" => $selector);
        $res = password_reset::search_password_reset_info($where, $whereParam);
        if (count($res) == 0)
        {
            $status = "NotValid";
        } else {
            $status = "ValidRequest";
            $userName = $res[0]["UserName"];
        }
    }
    else
    {
          $status = "NotValid";
    }
}
?>

<body class="forget-password">
<div class="wrapper">

    <div class="forget-password-page">
        <div class="forget-password-popup">
            <div class="forget-password-pop">
                <div class="row">
                    <div class="sign_in_sec current">
                        <h3>Reset your password</h3>
                        <p>
                            <?php if($status == "NotValid") {
                                echo "We could not validate your request";
                                die();
                            }
                            echo "Reset password for " . $userName ;
                            ?>
                        </p>
                        <form method="post" id="NewPassForm" name="NewPassForm">
                            <input type="hidden" id="selector" name="selector" value="<?php echo $selector; ?>">
                            <input type="hidden" id="validator" name="validator" value="<?php echo $validator; ?>">
                            <div class="row">
                                <div class="col-lg-12 no-pdd">
                                    <div class="sn-field">
                                        <input type="password" name="Password" id="Password" placeholder="Password">
                                        <i class="la la-lock"></i>
                                    </div><!--sn-field end-->
                                </div>
                                <div class="col-lg-12 no-pdd">
                                    <div class="sn-field">
                                        <input type="password" name="PwdRepeat" id="PwdRepeat" placeholder="Repeat password">
                                        <i class="la la-lock"></i>
                                    </div>
                                </div>
                                <div class="col-lg-12 no-pdd">
                                    <button type="button" name="NewPassSubmit" id="NewPassSubmit" onclick="update_password()">Update Password</button>
                                </div>
                                <div class="col-lg-12 no-pdd">
                                    <p id="rpMsg"></p>
                                </div>
                                <div class="forget-password-cancel"><a href="../index.php">Home</a></div>
                            </div>
                        </form>
                    </div><!--cmp-info end-->
                </div>
            </div><!--forget-password-pop end-->
        </div><!--forget-password-popup end-->
    </div><!--forget-password-page end-->


</div><!--theme-layout end-->



<script type="text/javascript" src="../js/jquery.min.js"></script>
<script type="text/javascript" src="../js/popper.js"></script>
<script type="text/javascript" src="../js/bootstrap.min.js"></script>
<script type="text/javascript" src="../lib/slick/slick.min.js"></script>
<script type="text/javascript" src="../js/script.js"></script>
<script type="text/javascript" src="forget_password.js"></script>
</body>
</html>