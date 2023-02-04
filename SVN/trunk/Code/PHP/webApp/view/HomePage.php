<!DOCTYPE html>

<?php
require_once '../Config.php';
?>
<html>
<head>
    <meta charset="utf-8">
    <meta name="description" content="LARA">
    <meta name=viewport content="width=device-width, initial-scale=1">
    <title>LARA PORTAL</title>
    <link rel="stylesheet" href="../css/HomePage.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script src="../js/HomePage.js"></script>

</head>

<body>
<div  class="homePageHeader">
    <header>
        <div class="headerLogout">
            <form action="../data/User.data.php" method="post" id="LogoutForm" name="LogoutForm">
                <button type="submit" name="LogoutSubmit">Logout</button>
            </form>
        </div>
        <div class="headerText">
            Logged in as : <?php echo $_SESSION[SessionIndex['UserName']]; ?>

        </div>
    </header>
</div>
<div class="homePageSlidebar" >
    <div id="cssmenu">
    <ul>

        <li class='has-sub'><a><span>About LARA</span></a>
            <ul>
                <li><a><span>LARA is the best :)</span></a></li>
            </ul>
        </li>
        <li class='has-sub'><a><span>Creating texts</span></a>
            <ul>
                <li><a href='LARAContents.php'><span>My LARA texts</span></a></li>
                <li><a href='NewLARAContent.php'><span>Add new text</span></a></li>
                <li><a href='../SharedModules/ChunkUploader/ExternalTextChunkUploader.php'><span>Import external text</span></a></li>
            </ul>
        </li>
        <li class='has-sub'><a><span>Crowdsourcing dashboard</span></a>
            <ul>
                <li><a href='AvailableTasks.php'><span>Available tasks</span></a></li>
                <li><a href='CrowdsourcedTasks.php'><span>My crowdsourced tasks</span></a></li>
            </ul>
        </li>
        <li class='has-sub'><a><span>Reading texts</span></a>
            <ul>
                <li><a href='ReadingHistories.php'><span>Read</span></a></li>
                <li><a href='NewReadingHistory.php'><span>Add new reading history</span></a></li>
            </ul>
        </li>
        <li class='has-sub'><a><span>Exercises</span></a>
            <ul>
                <li><a href='FlashcardContents.php'><span>Flashcards</span></a></li>
            </ul>
        </li>
        <li class='has-sub'><a><span>Available texts</span></a>
            <ul>
                <li><a href='DistributedResourcesList.php?rType=Content'><span>All published texts</span></a></li>
                <li><a href='NewDistributedResource.php'><span>Add external resource (advanced)</span></a></li>
            </ul>
        </li>
        <li class='has-sub'><a><span>Lexicon Resources</span></a>
            <ul>
                <li><a href='MultiWordLexicons.php'><span>Multi words lexicons (advanced)</span></a></li>
                <li><a href='DistributedResourcesList.php?rType=Language'><span>Language resources (advanced)</span></a></li>
                <li><a href='../SharedModules/ChunkUploader/ExternalLexiconChunkUploader.php'><span>Import language resource</span></a></li>
            </ul>
        </li>
        <li class='has-sub'><a><span>Log data</span></a>
            <ul>
                <li><a href='ContentLoggingData.php'><span>Contents log data</span></a></li>
                <li><a href='ReadingLoggingData.php'><span>Reading log data</span></a></li>
                <li><a href='FlashcardsLoggingData.php'><span>Flashcards log data</span></a></li>
            </ul>
        </li>
    </ul>
    </div>
</div>
<div class="mainContent" id="mainContentDIV">
    <div class="welcome">
        Welcome to your LARA portal
    </div>
</div>

</body>
</html>