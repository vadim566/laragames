<!DOCTYPE html>
<?php
require_once '../config.php';
require_once '../user/user.data.php';
require_once '../shared-modules/extra_modules.php';
require_once 'lara_content.data.php';

if(!isset($_SESSION[SessionIndex['UserID']]) || !isset($_REQUEST['Q1'])) {
    header("Location:../index.php");
    exit();
}

content_profile_page_visit();
$visitNumbers = content_visit::selectVisits();
$contentComments = content_comment::getCommentInfo();

$contentID = $_REQUEST['Q1'];
$contentWhere = " c.IsDeleted = 'NO' and c.ContentID = :cID";
$whereParam = array(":cID" => $contentID);
$contentInfo = lara_content_full_select($contentWhere, $whereParam);
$segmentWhere = " ContentID = :cID";
$laraSegmentInfo = search_content_segment($segmentWhere, $whereParam);
if(isset($contentInfo["DisplayName"]))
    $contentCreator = $contentInfo["DisplayName"];
else if(isset($contentInfo["FirstName"]) || isset($contentInfo["LastName"]))
    $contentCreator = $contentInfo["FirstName"] . " " . $contentInfo["LastName"];
else
    $contentCreator = $contentInfo["UserName"];

if(empty($contentInfo["CoverPictureExtension"]))
    $contentCoverImgSrc = "../images/resources/cover-img.jpg";
else
    $contentCoverImgSrc = image_to_base64(Repository . 'lara-content-cover-picture/' . $contentID . '.' . $contentInfo["CoverPictureExtension"]);

if(empty($contentInfo["ProfilePictureExtension"]))
    $contentProfileImgSrc = "../images/resources/company-profile.png";
else
    $contentProfileImgSrc = image_to_base64(Repository . 'lara-content-profile-picture/' . $contentID . '.' . $contentInfo["ProfilePictureExtension"]);

if(empty($contentInfo["CreatorProfilePictureExtension"]))
    $creatorProfileImgSrc = "../images/resources/company-pic.png";
else
    $creatorProfileImgSrc = image_to_base64(Repository . 'user-profile-picture/' . $contentInfo["CreatorID"] . '.' . $contentInfo["CreatorProfilePictureExtension"]);

?>

<html>
<head>
	<meta charset="UTF-8">
	<title><?php echo $contentInfo['ContentName']; ?></title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta name="description" content="" />
	<meta name="keywords" content="" />
	<link rel="stylesheet" type="text/css" href="../css/animate.css">
	<link rel="stylesheet" type="text/css" href="../css/bootstrap.min.css">
	<link rel="stylesheet" type="text/css" href="../css/flatpickr.min.css">
	<link rel="stylesheet" type="text/css" href="../css/line-awesome.css">
	<link rel="stylesheet" type="text/css" href="../css/line-awesome-font-awesome.min.css">
	<link href="../vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
	<link rel="stylesheet" type="text/css" href="../css/font-awesome.min.css">
	<link rel="stylesheet" type="text/css" href="../lib/slick/slick.css">
	<link rel="stylesheet" type="text/css" href="../lib/slick/slick-theme.css">
	<link rel="stylesheet" type="text/css" href="../css/style.css">
	<link rel="stylesheet" type="text/css" href="../css/responsive.css">
</head>
<body>	

	<div class="wrapper">
        <?php include_once('../header.php'); ?>
        <section class="cover-sec">
            <?php
                echo '<img src="' . $contentCoverImgSrc . '" height="400">';
                if($_SESSION[SessionIndex['UserID']] == $contentInfo["CreatorID"])
                {
            ?>
            <div class="add-pic-box">
                <div class="container">
                    <div class="row no-gutters">
                        <div class="col-lg-12 col-sm-12">
                            <form method="POST" id="ContentCoverPicture" enctype='multipart/form-data'>
                                <input type="file" id="ContentCoverPictureFile" name="ContentCoverPictureFile" onchange="save_content_picture('#ContentCoverPicture')">
                                <label for="ContentCoverPictureFile">Change Image</label>
                                <input type="hidden" id="ContentID" name="ContentID" value=<?php echo '"' . $contentID . '"'; ?>>
                                <input type="hidden" id="task" name="task" value="save_content_cover_picture">
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            <?php } ?>
        </section>
        <main>
        <div class="main-section">
            <div class="container">
                <div class="main-section-data">
                    <div class="row">
                        <div class="col-lg-3">
                            <div class="main-left-sidebar">
                                <div class="user_profile">
                                    <div class="user-pro-img">
                                        <?php
                                            echo '<img src="' . $contentProfileImgSrc . '" width="170" height="170">';
                                        if($_SESSION[SessionIndex['UserID']] == $contentInfo["CreatorID"])
                                        {
                                        ?>
                                        <div class="add-dp" id="OpenImgUpload">
                                            <form method="POST" id="ContentProfilePicture" enctype='multipart/form-data'>
                                                <input type="file" id="ContentProfilePictureFile" name="ContentProfilePictureFile"
                                                       onchange="save_content_picture('#ContentProfilePicture')">
                                                <label for="ContentProfilePictureFile"><i class="fas fa-camera"></i></label>
                                                <input type="hidden" id="ContentID" name="ContentID" value=<?php echo '"' . $contentID . '"'; ?>>
                                                <input type="hidden" id="task" name="task" value="save_content_profile_picture">
                                            </form>
                                        </div>
                                        <?php } ?>
                                    </div><!--user-pro-img end-->
                                    <div class="user_pro_status">
                                        <ul class="flw-hr">
                                            <li><a href="#" title="" class="flww"><i class="la la-plus"></i> Follow</a></li>
                                        </ul>
                                        <ul class="flw-status">
                                            <li>
                                                <span>Reads</span>
                                                <b>
                                                    <?php
                                                        if(!empty($visitNumbers["snPage"]))
                                                            echo $visitNumbers["snPage"];
                                                        else
                                                            echo "0";
                                                    ?>
                                                </b>
                                            </li>
                                            <li>
                                                <span>Full text reads</span>
                                                <b>
                                                    <?php
                                                        if(!empty($visitNumbers["webPage"]))
                                                            echo $visitNumbers["webPage"];
                                                        else
                                                            echo "0";
                                                    ?>
                                                </b>
                                            </li>
                                        </ul>
                                    </div><!--user_pro_status end-->
                                    <ul class="social_links">
                                        <li>
                                            <?php if(!empty($contentInfo['webAddress']))
                                                echo '<a href="' . $contentInfo['webAddress'] . '" 
                                                            id="FullTextVisitTag" target="_blank">
                                                        <i class="la la-globe"></i>
                                                        Full content
                                                        </a>';
                                            else
                                                echo 'Pages are not available yet.';
                                            ?>
                                        </li>
                                    </ul>
                                </div><!--user_profile end-->
                                <!--div class="suggestions full-width">
                                    <div class="sd-title">
                                        <h3>Suggestions</h3>
                                        <i class="la la-ellipsis-v"></i>
                                    </div><! --sd-title end-- >
                                    <div class="suggestions-list">
                                        <div class="suggestion-usd">
                                            <img src="../images/resources/s1.png" alt="">
                                            <div class="sgt-text">
                                                <h4>Jessica William</h4>
                                                <span>Graphic Designer</span>
                                            </div>
                                            <span><i class="la la-plus"></i></span>
                                        </div>
                                        <div class="view-more">
                                            <a href="#" title="">View More</a>
                                        </div>
                                    </div><! --suggestions-list end-- >
                                </div><! --suggestions end-->
                            </div><!--main-left-sidebar end-->
                        </div>
                        <div class="col-lg-7">
                            <div class="main-ws-sec">
                                <div class="user-tab-sec">
                                    <h3><?php echo $contentInfo['ContentName']; ?></h3>
                                    <div class="star-descp">
                                        <ul>
                                            <li><i class="fa fa-star"></i></li>
                                            <li><i class="fa fa-star"></i></li>
                                            <li><i class="fa fa-star"></i></li>
                                            <li><i class="fa fa-star"></i></li>
                                            <li><i class="fa fa-star-half-o"></i></li>
                                        </ul>
                                    </div><!--star-descp end-->
                                    <div class="tab-feed">
                                        <ul>
                                            <li data-tab="feed-dd" class="active">
                                                <a href="#" title="">
                                                    <img src="../images/ic1.png" alt="">
                                                    <span>Feed</span>
                                                </a>
                                            </li>
                                            <li data-tab="info-dd">
                                                <a href="#" title="">
                                                    <img src="../images/ic2.png" alt="">
                                                    <span>Info</span>
                                                </a>
                                            </li>
                                        </ul>
                                    </div><!-- tab-feed end-->
                                </div><!--user-tab-sec end-->
                                <div class="product-feed-tab current" id="feed-dd">
                                    <div class="posts-section">
                                        <div class="post-bar">
                                            <div class="post_topbar">
                                                <div class="usy-dt">
                                                    <?php echo '<img src="' . $creatorProfileImgSrc . '" width="50" height="50">';?>
                                                    <div class="usy-name">
                                                        Created by <h3><?php echo $contentCreator; ?></h3>
                                                        <span><img src="../images/clock.png" alt="">3 min ago</span>
                                                    </div>
                                                </div>
                                                <div class="ed-opts">
                                                    <a href="#" title="" class="ed-opts-open"><i class="la la-ellipsis-v"></i></a>
                                                    <ul class="ed-options">
                                                        <li><a href="#" title="">Edit Post</a></li>
                                                        <li><a href="#" title="">Unsaved</a></li>
                                                        <li><a href="#" title="">Unbid</a></li>
                                                        <li><a href="#" title="">Close</a></li>
                                                        <li><a href="#" title="">Hide</a></li>
                                                    </ul>
                                                </div>
                                            </div>
                                            <div class="job_descp">
                                                <?php
                                                for($j=1; $j <= count($laraSegmentInfo); $j++)
                                                {
                                                    echo "<ul class='segment-info'><li><span>" . $laraSegmentInfo[$j]["SegmentInL2"] . "</span></li>";
                                                    if(!empty($laraSegmentInfo[$j]["RecordingFileName"]))
                                                        echo "<li><img src='../images/ic7.png' 
                                                                            onclick='play_segment_voice(\"" . $laraSegmentInfo[$j]["RecordingFileName"] . "\")'></li>";
                                                    echo "</ul>";
                                                    if(!empty($laraSegmentInfo[$j]["SegmentInL1"]))
                                                    {
                                                        echo "<ul class='segment-info'>
                                                                        <li><img src='../images/ic8.png' onclick='manage_translation(\"" . $contentID . "_" . $j . "\")'></li>
                                                                        <li><span id='" . $contentID . "_" . $j . "' style='display: none'>" . $laraSegmentInfo[$j]["SegmentInL1"] . "</span></li>
                                                                        </ul>";
                                                    }
                                                    echo "<br />";
                                                }
                                                ?>
                                                <a href="#" target="_blank">view more(loading more segments maybe?!)</a>
                                            </div>

                                            <!-- comment pattern div class="comment-area">
                                                <i class="la la-plus-circle"></i>
                                                <div class="post_topbar">
                                                    <div class="usy-dt">
                                                        <img src="../images/resources/bg-img1.png" alt="">
                                                        <div class="usy-name">
                                                            <h3>John Doe</h3>
                                                            <span><img src="../images/clock.png" alt="">3 min ago</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="reply-area">
                                                    <p>First Comment</p>
                                                    <span><i class="la la-mail-reply"></i>Reply</span>
                                                </div>
                                            </div-->

                                            <?php
                                            if(count($contentComments) != 0) {
                                                for ($commentCounter = 0; $commentCounter < count($contentComments); $commentCounter++) { ?>
                                                    <div class="comment-area">
                                                        <div class="post_topbar">
                                                            <div class="usy-dt">
                                                                <img src="../images/resources/bg-img1.png" alt="">
                                                                <div class="usy-name">
                                                                    <h3><?php echo $contentComments[$commentCounter]["UserName"]; ?></h3>
                                                                    <span><img src="../images/clock.png" alt="">
                                                                        <?php echo $contentComments[$commentCounter]["CommentTime"]; ?>
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <div class="reply-area">
                                                            <p><?php echo $contentComments[$commentCounter]["CommentText"]; ?></p>
                                                        </div>
                                                    </div>
                                                <?php }
                                            }  ?>

                                            <div class="postcomment">
                                                <span><i class="la"></i>&nbsp;</span>

                                                <div class="row">
                                                    <div class="col-md-2">
                                                        <img src="../images/resources/bg-img4.png" alt="">
                                                    </div>
                                                    <div class="col-md-8">
                                                        <form method="POST" id="CommentForm">
                                                            <div class="form-group">
                                                                <input type="text" class="form-control"
                                                                       name="CommentText" id="CommentText" placeholder="Post a comment">
                                                                <input type="hidden" id="ContentID" name="ContentID" value=<?php echo '"' . $contentID . '"'; ?>>
                                                                <input type="hidden" id="task" name="task" value="save_comment">
                                                            </div>
                                                        </form>
                                                    </div>
                                                    <div class="col-md-2">
                                                        <a onclick="save_comment()">Send</a>
                                                    </div>
                                                </div>
                                            </div>




                                        </div><!--post-bar end-->
                                    </div><!--posts-section end-->
                                </div><!--product-feed-tab end-->
                                <div class="product-feed-tab" id="info-dd">
                                    <div class="user-profile-ov">
                                        <h3>
                                            <a href="#" title="" class="overview-open">Overview</a>
                                            <a href="#" title="" class="overview-open"><i class="fa fa-pencil"></i></a>
                                        </h3>
                                        <p>Here is the overview.</p>
                                    </div><!--user-profile-ov end-->
                                    <div class="user-profile-ov st2">
                                        <h3>
                                            <a href="#" title="" class="esp-bx-open">Establish Since </a>
                                            <a href="#" title="" class="esp-bx-open"><i class="fa fa-pencil"></i></a>
                                            <a href="#" title="" class="esp-bx-open"><i class="fa fa-plus-square"></i></a>
                                        </h3>
                                        <span>February 2004</span>
                                    </div><!--user-profile-ov end-->
                                </div><!--product-feed-tab end-->
                                <div id="audio_container" style="width:0;height:0;overflow:hidden"></div>


                            </div><!--main-ws-sec end-->
                        </div>
                        <div class="col-lg-2">
                            <div class="right-sidebar">
                                <div class="message-btn">
                                    <a href="#" title="" onclick="open_email_to_creator_box('<?php echo $contentID;?>')">
                                        <i class="fa fa-envelope"></i> Message</a>
                                </div>
                            </div><!--right-sidebar end-->
                        </div>
                    </div>
                </div><!-- main-section-data end-->
            </div>
        </div>
    </main>

        <?php include_once('../footer.php'); ?>

        <div class="overview-box" id="overview-box">
            <div class="overview-edit">
                <h3>Overview</h3>
                <span>5000 character left</span>
                <form>
                    <textarea></textarea>
                    <button type="submit" class="save">Save</button>
                    <button type="submit" class="cancel">Cancel</button>
                </form>
                <a href="#" title="" class="close-box"><i class="la la-close"></i></a>
            </div><!--overview-edit end-->
        </div><!--overview-box end-->

		<div class="overview-box" id="establish-box">
			<div class="overview-edit">
				<h3>Establish Since</h3>
				<form>
					<div class="daty">
						<input type="text" name="establish" placeholder="Select Date" class="datepicker">
						<i class="fa fa-calendar"></i>
					</div>
					<button type="submit" class="save">Save</button>
					<button type="submit" class="cancel">Cancel</button>
				</form>
				<a href="#" title="" class="close-box"><i class="la la-close"></i></a>
			</div><!--overview-edit end-->
		</div><!--overview-box end-->

        <div class="overview-box" id="email-to-creator-box">
            <div class="overview-edit">
                <h3>Your message</h3>
                <form method="POST" id="SendEmailToCreator">
                    <input type="hidden" id="ContentID" name="ContentID" value="<?php echo $contentID;?>">
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
<script type="text/javascript" src="../js/flatpickr.min.js"></script>
<script type="text/javascript" src="../lib/slick/slick.min.js"></script>
<script type="text/javascript" src="../js/script.js"></script>
<script type="text/javascript" src="content.js"></script>
</body>
</html>