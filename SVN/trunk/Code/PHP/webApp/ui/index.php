<!DOCTYPE html>
<html lang="en"> 
<head>
    <title>LARA Portal</title>
    
    <!-- Meta -->
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <meta name="description" content="LARA Portal">
    <link rel="shortcut icon" href="favicon.ico">
    
    <!-- FontAwesome JS-->
    <script defer src="../assets/plugins/fontawesome/js/all.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script src="../js/index.js"></script>


    <!-- App CSS -->  
    <link id="theme-style" rel="stylesheet" href="../assets/css/portal.css">

</head>

<?php
require_once '../Config.php';
?>


<body class="app app-login p-0">    	
    <div class="row g-0 app-auth-wrapper">
	    <div class="col-12 col-md-7 col-lg-6 auth-main-col text-center p-5">
		    <div class="d-flex flex-column align-content-end">
			    <div class="app-auth-body mx-auto">	
				    <div class="app-auth-branding mb-4"><a class="app-logo" href="https://www.unige.ch/callector/lara/" target="_blank"><img class="logo-icon mr-2" src="../assets/images/lara-logo.png" alt="logo"></a></div>
					<h2 class="auth-heading text-center mb-5">Log in to LARA Portal</h2>
			        <div class="auth-form-container text-left">
                        <form class="auth-form login-form" action="../data/User.data.php" method="post" id="LoginForm" name="LoginForm">
							<div class="email mb-3">
								<label class="sr-only" for="UserNameEmail">Email</label>
								<input id="UserNameEmail" name="UserNameEmail" type="text" class="form-control signin-email" placeholder="E-mail/Username" required="required">
							</div><!--//form-group-->
							<div class="password mb-3">
								<label class="sr-only" for="UserPassword">Password</label>
								<input id="UserPassword" name="UserPassword" type="password" class="form-control signin-password" placeholder="Password" required="required">
								<div class="extra mt-3 row justify-content-between">
									<div class="col-6">
									</div><!--//col-6-->
									<div class="col-6">
										<div class="forgot-password text-right">
											<a href="reset-password.php">Forgot password?</a>
										</div>
									</div><!--//col-6-->
								</div><!--//extra-->
							</div><!--//form-group-->
							<div class="text-center">
								<button type="submit" name="LoginSubmit" id="LoginSubmit" class="btn app-btn-primary btn-block theme-btn mx-auto">Log In</button>
                            </div>
                            <div class="alert alert-danger  alert-dismissible show fade in mt-3" role="alert" id="errorDiv" style="display:none;">
                                <strong>Error!</strong> <div id="errorText"></div>
                            </div>
						</form>
						
						<div class="auth-option text-center pt-5">No Account? Sign up <a class="text-link" href="signup.html" >here</a>.</div>
					</div><!--//auth-form-container-->	

			    </div><!--//auth-body-->
		    
			    <footer class="app-auth-footer">
				    <div class="container text-center py-3">
			            <small class="copyright">Designed with <i class="fas fa-heart" style="color: #fb866a;"></i> for language geeks</small>
				    </div>
			    </footer><!--//app-auth-footer-->	
		    </div><!--//flex-column-->   
	    </div><!--//auth-main-col-->
	    <div class="col-12 col-md-5 col-lg-6 h-100 auth-background-col">
		    <div class="auth-background-holder">
		    </div>
		    <div class="auth-background-mask"></div>
		    <div class="auth-background-overlay p-3 p-lg-5">
			    <div class="d-flex flex-column align-content-end h-100">
				    <div class="h-100"></div>
				    <div class="overlay-content p-3 p-lg-4 rounded">
					    <h5 class="mb-3 overlay-title">Welcome to LARA portal</h5>
					    <div>A collaborative open source project, whose goal is to support development of L2 language skills by reading.</div>
				    </div>
				</div>
		    </div><!--//auth-background-overlay-->
	    </div><!--//auth-background-col-->
    
    </div><!--//row-->


</body>
</html> 

