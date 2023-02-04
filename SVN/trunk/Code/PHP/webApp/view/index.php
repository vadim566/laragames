
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="description" content="LARA">
    <meta name=viewport content="width=device-width, initial-scale=1">
    <title>LARA portal</title>

    <link rel="stylesheet" href="../css/index.css">
</head>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script src="../js/index.js"></script>

<body>

<?php
require 'header.html';
require_once '../Config.php';
?>

    <main>
      <div class="wrapper-main" id="mainBody">
        <section class="section-default">
        <?php
            if(isset($_REQUEST['status']) && $_REQUEST['status'] == 'logout')
            {
                echo '<p class="login-status" id="mainContent">' . LogoutMsg . '</p>';
            }
            else if(isset($_REQUEST['status']) && $_REQUEST['status'] == 'sessionExpired')
            {
                echo '<p class="login-status" id="mainContent">Session expired. Please login again to continue.</p>';
            }
            else if(isset($_REQUEST['status']) && $_REQUEST['status'] == 'createNewPassword')
            {
                echo '<p class="login-status" id="mainContent">';
                require 'CreateNewPassword.php';
                echo '</p>';
            }
            else
            {
                echo '<p class="login-status" id="mainContent">' . WelcomeMsg . '</p>';
            }
        ?>
        </section>
      </div>
    </main>


</body>
</html