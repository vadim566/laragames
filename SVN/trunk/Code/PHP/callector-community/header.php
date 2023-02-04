<?php
if(empty($_SESSION[SessionIndex["UserInfo"]]["ProfilePictureExtension"]))
    $profileImgSrc = "../images/resources/profile-icon-tiny.png";
else
    $profileImgSrc = image_to_base64(Repository . 'user-profile-picture/' .
        $_SESSION[SessionIndex['UserID']] . '.' . $_SESSION[SessionIndex["UserInfo"]]["ProfilePictureExtension"]);
?>
<header>
    <div class="container">
        <div class="header-data">
            <div class="logo">
                <img src="../images/logo.png" alt="">
            </div><!--logo end-->
            <div class="search-bar">
            <!-- todo add search for person here -->
                <form>
                    <input type="text" name="search" placeholder="Search...">
                    <button type="submit"><i class="la la-search"></i></button>
                </form>
            </div><!--search-bar end-->
            <nav>
                <ul>
                    <!--li>
                        <a href="../user/log_in.php" title="">
                            <span><img src="../images/icon1.png" alt=""></span>
                            Home
                        </a>
                    </li-->
                    <li>
                        <a href="../lara-content/contents.php" title="">
                            <span><img src="../images/icon3.png" alt=""></span>
                            LARA contents
                        </a>
                    </li>
                    <!--li>
                        <a href="../user/friends.php" title="">
                            <span><img src="../images/icon4.png" alt=""></span>
                            Friends
                        </a>
                    </li-->
                    <!--li>
                        <a href="#" title="" class="not-box-openm">
                            <span><img src="../images/icon6.png" alt=""></span>
                            Messages
                        </a>
                        <div class="notification-box msg" id="message">
                            <div class="nt-title">
                                <h4>Setting</h4>
                                <a href="#" title="">Clear all</a>
                            </div>
                            <div class="nott-list">
                                <div class="notfication-details">
                                    <div class="noty-user-img">
                                        <img src="../images/resources/ny-img1.png" alt="">
                                    </div>
                                    <div class="notification-info">
                                        <h3><a href="messages.html" title="">Jassica William</a> </h3>
                                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do.</p>
                                        <span>2 min ago</span>
                                    </div>< !--notification-info -- >
                                </div>
                                <div class="notfication-details">
                                    <div class="noty-user-img">
                                        <img src="../images/resources/ny-img2.png" alt="">
                                    </div>
                                    <div class="notification-info">
                                        <h3><a href="messages.html" title="">Jassica William</a></h3>
                                        <p>Lorem ipsum dolor sit amet.</p>
                                        <span>2 min ago</span>
                                    </div>< !--notification-info -- >
                                </div>
                                <div class="notfication-details">
                                    <div class="noty-user-img">
                                        <img src="../images/resources/ny-img3.png" alt="">
                                    </div>
                                    <div class="notification-info">
                                        <h3><a href="messages.html" title="">Jassica William</a></h3>
                                        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempo incididunt ut labore et dolore magna aliqua.</p>
                                        <span>2 min ago</span>
                                    </div>< !--notification-info -- >
                                </div>
                                <div class="view-all-nots">
                                    <a href="messages.html" title="">View All Messsages</a>
                                </div>
                            </div>< !--nott-list end-- >
                        </div>< !--notification-box end-- >
                    </li>
                    <li>
                        <a href="#" title="" class="not-box-open">
                            <span><img src="../images/icon7.png" alt=""></span>
                            Notification
                        </a>
                        <div class="notification-box noti" id="notification">
                            <div class="nt-title">
                                <h4>Setting</h4>
                                <a href="#" title="">Clear all</a>
                            </div>
                            <div class="nott-list">
                                <div class="notfication-details">
                                    <div class="noty-user-img">
                                        <img src="../images/resources/ny-img1.png" alt="">
                                    </div>
                                    <div class="notification-info">
                                        <h3><a href="#" title="">Jassica William</a> Comment on your project.</h3>
                                        <span>2 min ago</span>
                                    </div>< !--notification-info -- >
                                </div>
                                <div class="notfication-details">
                                    <div class="noty-user-img">
                                        <img src="../images/resources/ny-img2.png" alt="">
                                    </div>
                                    <div class="notification-info">
                                        <h3><a href="#" title="">Jassica William</a> Comment on your project.</h3>
                                        <span>2 min ago</span>
                                    </div>< !--notification-info -- >
                                </div>
                                <div class="notfication-details">
                                    <div class="noty-user-img">
                                        <img src="../images/resources/ny-img3.png" alt="">
                                    </div>
                                    <div class="notification-info">
                                        <h3><a href="#" title="">Jassica William</a> Comment on your project.</h3>
                                        <span>2 min ago</span>
                                    </div>< !--notification-info -- >
                                </div>
                                <div class="notfication-details">
                                    <div class="noty-user-img">
                                        <img src="../images/resources/ny-img2.png" alt="">
                                    </div>
                                    <div class="notification-info">
                                        <h3><a href="#" title="">Jassica William</a> Comment on your project.</h3>
                                        <span>2 min ago</span>
                                    </div>< !--notification-info -- >
                                </div>
                                <div class="view-all-nots">
                                    <a href="#" title="">View All Notification</a>
                                </div>
                            </div>< !--nott-list end-- >
                        </div>< !--notification-box end-->
                    </li>
                </ul>
            </nav><!--nav end-->
            <div class="menu-btn">
                <a href="#" title=""><i class="fa fa-bars"></i></a>
            </div><!--menu-btn end-->
            <div class="user-account">
                <div class="user-info">
                    <?php echo '<img src="' . $profileImgSrc . '" width="30" height="30">'; ?>
                    <a href="#" title=""><?php echo $_SESSION[SessionIndex['UserName']]; ?></a>
<i class="la la-sort-down"></i>
</div>
<div class="user-account-settingss" id="users">
    <h3><?php echo $_SESSION[SessionIndex["UserInfo"]]["DisplayName"]; ?></h3>
    <ul class="us-links">
        <li><a href=<?php echo "../user/user-profile.php?id=" . $_SESSION[SessionIndex['UserID']]; ?> title="">Profile</a></li>
        <li><a href="../user/user-setting.php" title="">Account Setting</a></li>
        <!--li><a href="#" title="">Faqs</a></li>
        <li><a href="#" title="">Terms & Conditions</a></li-->
    </ul>
    <h3 class="tc" onclick="user_logout()">Logout</h3>
</div><!--user-account-settingss end-->
</div>
</div><!--header-data end-->
</div>
</header><!--header end-->

<script type="text/javascript">
    function user_logout()
    {
        data = "task=user_logout";
        $.ajax({
            url: "../account/account.data.php",
            type: "post",
            data: data ,
            success: function (response) {
                window.location = "../index.php";
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        });
    }
</script>