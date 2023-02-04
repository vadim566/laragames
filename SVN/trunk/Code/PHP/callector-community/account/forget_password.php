<?php

require_once "../config.php";

?>
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


<body class="forget-password">
	<div class="wrapper">		

		<div class="forget-password-page">
			<div class="forget-password-popup">
				<div class="forget-password-pop">
					<div class="row">
                        <div class="sign_in_sec current">
                            <h3>Reset your password</h3>
                            <p>An email will be sent to you with the instruction on how to reset your password.</p>
                            <form method="post" id="ResetPassForm" name="ResetPassForm">
                                <div class="row">
                                    <div class="col-lg-12 no-pdd">
                                        <div class="sn-field">
                                            <input type="text" name="Email" id="Email" placeholder="E-mail">
                                            <i class="la la-globe"></i>
                                        </div><!--sn-field end-->
                                    </div>
                                    <div class="col-lg-12 no-pdd">
                                        <button type="button" name="ResetPassSubmit" id="ResetPassSubmit" onclick="reset_password_request()">Reset Password</button>
                                    </div>
                                    <div class="col-lg-12 no-pdd">
                                        <p id="rpMsg"></p>
                                    </div>
                                    <div class="forget-password-cancel"><a href="../index.php">Cancel</a></div>
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