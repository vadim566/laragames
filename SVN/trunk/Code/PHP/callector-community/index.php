<?php

require_once "config.php";

?>
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>Callector community</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta name="description" content="" />
	<meta name="keywords" content="" />
	<link rel="stylesheet" type="text/css" href="css/animate.css">
	<link rel="stylesheet" type="text/css" href="css/bootstrap.min.css">
	<link rel="stylesheet" type="text/css" href="css/line-awesome.css">
	<link rel="stylesheet" type="text/css" href="css/line-awesome-font-awesome.min.css">
	<link href="vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
	<link rel="stylesheet" type="text/css" href="css/font-awesome.min.css">
	<link rel="stylesheet" type="text/css" href="lib/slick/slick.css">
	<link rel="stylesheet" type="text/css" href="lib/slick/slick-theme.css">
	<link rel="stylesheet" type="text/css" href="css/style.css">
	<link rel="stylesheet" type="text/css" href="css/responsive.css">
</head>


<body class="sign-in">
	

	<div class="wrapper">		

		<div class="sign-in-page">
			<div class="signin-popup">
				<div class="signin-pop">
					<div class="row">
						<div class="col-lg-6">
							<div class="cmp-info">
								<div class="cm-logo">
									<img src="images/cm-logo.png" alt="">
									<p>
                                        CALLector, which officially started on April 1 2018 and will continue until December 31 2021, is funded by the Swiss National Science Foundation under its COST program, and the project is closely linked with <a href="http://enetcollect.eurac.edu/" target="_blank">the enetCollect COST project</a>. The overall goal of CALLector is to create a platform, structured as a social network, for crowdsourced construction and use of CALL content. We are developing tools for text-based content using <a href="https://lara-portal.unige.ch/" target="blank">the LARA platform</a>.
                                    </p>
								</div><!--cm-logo end-->	
								<img src="images/cm-main-img.png" alt="">			
							</div><!--cmp-info end-->
						</div>
						<div class="col-lg-6">
							<div class="login-sec">
								<ul class="sign-control">
									<li data-tab="tab-1" class="current"><a href="#" title="">Sign in</a></li>				
									<li data-tab="tab-2"><a href="#" title="">Sign up</a></li>				
								</ul>			
								<div class="sign_in_sec current" id="tab-1">
									
									<h3>Sign in</h3>
									<form action="account/account.data.php" method="post" id="LoginForm" name="LoginForm">
										<div class="row">
											<div class="col-lg-12 no-pdd">
												<div class="sn-field">
													<input type="text" name="UserNameEmail" id="UserNameEmail" placeholder="E-mail/Username">
													<i class="la la-user"></i>
												</div><!--sn-field end-->
											</div>
											<div class="col-lg-12 no-pdd">
												<div class="sn-field">
													<input type="password" name="UserPassword" id="UserPassword" placeholder="Password">
													<i class="la la-lock"></i>
												</div>
											</div>
											<div class="col-lg-12 no-pdd">
												<div class="checky-sec">
													<div class="fgt-sec">
														<!--commented by hani
														input type="checkbox" name="cc" id="c1">
														<label for="c1">
															<span></span>
														</label>
														<small>Remember me</small-->
													</div><!--fgt-sec end-->
													<a href="account/forget_password.php" title="">Forgot Password?</a>
												</div>
											</div>
											<div class="col-lg-12 no-pdd">
												<button type="submit" name="LoginSubmit" id="LoginSubmit">Sign in</button>
											</div>
                                            <div class="col-lg-12 no-pdd">
                                                <p name="loginResponseMsg" id="loginResponseMsg"></p>
                                            </div>
										</div>
									</form>
									<!-- commented by hani
									    div class="login-resources">
										<h4>Login Via Social Account</h4>
										<ul>
											<li><a href="#" title="" class="fb"><i class="fa fa-facebook"></i>Login Via Facebook</a></li>
											<li><a href="#" title="" class="tw"><i class="fa fa-twitter"></i>Login Via Twitter</a></li>
										</ul>
									</div><!--login-resources end-->
								</div><!--sign_in_sec end-->
								<div class="sign_in_sec" id="tab-2">
                                    <form method="post" id="SignupForm" name="SignupForm">
                                        <div class="row">
                                            <div class="col-lg-12 no-pdd">
                                                <p class="sign_up_error" id="UserNameMsg"></p>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <div class="sn-field">
                                                    <input type="text" name="UserName" id="UserName" placeholder="Username">
                                                    <i class="la la-user"></i>
                                                </div>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <p class="sign_up_error" id="EmailMsg"></p>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <div class="sn-field">
                                                    <input type="text" name="Email" id="Email" placeholder="E-mail">
                                                    <i class="la la-globe"></i>
                                                </div>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <p class="sign_up_error" id="PasswordMsg"></p>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <div class="sn-field">
                                                    <input type="password" name="Password" id="Password" placeholder="Password">
                                                    <i class="la la-lock"></i>
                                                </div>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <p class="sign_up_error" id="PwdRepeatMsg"></p>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <div class="sn-field">
                                                    <input type="password" name="PwdRepeat" id="PwdRepeat" placeholder="Repeat password">
                                                    <i class="la la-lock"></i>
                                                </div>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <div class="checky-sec st2">
                                                    <div class="fgt-sec">
                                                        <input type="checkbox" name="cc" id="c2">
                                                        <label for="c2">
                                                            <span></span>
                                                        </label>
                                                        <small>Yes, I understand and agree to the Callector community Terms & Conditions.</small>
                                                    </div><!--fgt-sec end-->
                                                </div>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <button type="button" onclick="send_sign_up_form()">Get Started</button>
                                            </div>
                                            <div class="col-lg-12 no-pdd">
                                                <p name="signupResponseMsg" id="signupResponseMsg"></p>
                                            </div>
                                        </div>
                                    </form>
								</div>
							</div><!--login-sec end-->
						</div>
					</div>		
				</div><!--signin-pop end-->
			</div><!--signin-popup end-->
			<div class="footy-sec">
				<div class="container">
					<ul>
						<li><a href="https://www.unige.ch/callector/" target="_blank">Callector</a></li>
						<li><a href="https://enetcollect.eurac.edu/" target="_blank">enetCollect</a></li>
						<li><a href="https://lara-portal.unige.ch/" target="_blank">LARA portal</a></li>
						<li><a href="https://laraplatform.wordpress.com/" target="_blank">LARA blog</a></li>
                        <li><a href="http://www.snf.ch/en/Pages/default.aspx" target="_blank">SNF</a></li>
						<li><a href="#" title="">Copyright Policy</a></li>
					</ul>
					<p><img src="images/copy-icon.png" alt="">Copyright 2020</p>
				</div>
			</div><!--footy-sec end-->
		</div><!--sign-in-page end-->


	</div><!--theme-layout end-->



<script type="text/javascript" src="js/jquery.min.js"></script>
<script type="text/javascript" src="js/popper.js"></script>
<script type="text/javascript" src="js/bootstrap.min.js"></script>
<script type="text/javascript" src="lib/slick/slick.min.js"></script>
<script type="text/javascript" src="js/script.js"></script>
<script type="text/javascript" src="index.js"></script>
</body>
</html>