<!DOCTYPE html>
<?php
require_once '../config.php';
require_once '../user/user.data.php';
require_once 'lara_content.data.php';

if(!isset($_SESSION[SessionIndex['UserID']])) {
    header("Location:../index.php");
    exit();
}
?>
<html>
<head>
    <meta charset="UTF-8">
    <title>Lara contents</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="" />
    <meta name="keywords" content="" />
    <link rel="stylesheet" type="text/css" href="../css/animate.css">
    <link rel="stylesheet" type="text/css" href="../css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="../css/line-awesome.css">
    <link rel="stylesheet" type="text/css" href="../css/line-awesome-font-awesome.min.css">
    <link href="../vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" type="text/css" href="../css/font-awesome.min.css">
    <link rel="stylesheet" type="text/css" href="../css/jquery.mCustomScrollbar.min.css">
    <link rel="stylesheet" type="text/css" href="../lib/slick/slick.css">
    <link rel="stylesheet" type="text/css" href="../lib/slick/slick-theme.css">
    <link rel="stylesheet" type="text/css" href="../css/style.css">
    <link rel="stylesheet" type="text/css" href="../css/responsive.css">
</head>

<body>	
	<div class="wrapper">
        <?php include_once('../header.php'); ?>

        <!--Revised till here-->
		<section class="companies-info">
			<div class="container">
				<div class="company-search-bar">
                    <div class="search-bar">
                        <form method="POST" id="ContentSearchForm">
                            <input type="text" placeholder="Search contents..." id="ContentSearchText" name="ContentSearchText">
                            <input type="hidden" id="task" name="task" value="search_all_content">
                            <button type="button" onclick="filter_data()"><i class="la la-search"></i></button>
                        </form>
                    </div>
                </div><!--company-search-bar end-->
                <div class="process-comm" id="content-spinner" style="display: none">
                    <div class="spinner">
                        <div class="bounce1"></div>
                        <div class="bounce2"></div>
                        <div class="bounce3"></div>
                    </div>
                </div><!--process-comm end-->
				<div class="companies-list" id="content-body">

				</div><!--companies-list end-->
			</div>
		</section><!--companies-info end-->
        <?php include_once('../footer.php'); ?>

        <div class="overview-box" id="email-to-creator-box">
            <div class="overview-edit">
                <h3>Your message</h3>
                <form method="POST" id="SendEmailToCreator">
                    <input type="hidden" id="ContentID" name="ContentID">
                    <input type="hidden" id="From" name="From" value="<?php echo $_SESSION[SessionIndex['UserID']];?>">
                    <input type="hidden" id="task" name="task" value="send_email_to_creator">
                    <textarea id="EmailBody" name="EmailBody"></textarea>
                    <button type="button" class="save" onclick="send_email_to_creator()">Send</button>
                    <button type="reset" class="cancel">Cancel</button>
                </form>
                <a href="../#" title="" class="close-box"><i class="la la-close"></i></a>
            </div><!--overview-edit end-->
        </div>

    </div><!--theme-layout end-->


<script type="text/javascript" src="../js/jquery.min.js"></script>
<script type="text/javascript" src="../js/popper.js"></script>
<script type="text/javascript" src="../js/bootstrap.min.js"></script>
<script type="text/javascript" src="../js/jquery.mCustomScrollbar.js"></script>
<script type="text/javascript" src="../lib/slick/slick.min.js"></script>
<script type="text/javascript" src="../js/scrollbar.js"></script>
<script type="text/javascript" src="../js/script.js"></script>
<script type="text/javascript" src="content.js"></script>
<script>
    $(document).ready(function(){
        filter_data();
    });
</script>
</body>
</html>