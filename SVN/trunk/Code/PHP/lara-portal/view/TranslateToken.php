<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 2/11/2020
 */

?>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<?php
$now = new DateTime();
echo '<link rel="stylesheet" href="../css/MainContent.css?' . $now->format('His') . '">';
echo '<script src="../js/DataTranslation.js?' . $now->format('His') . '"></script>';
echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';

?>

<?php
require_once '../class/ContentToken.class.php';
require_once '../class/Content.class.php';
require_once '../class/Language.class.php';
require_once '../Config.php';

$trCount = 0;

if(!isset($_GET["contentID"]))
{
    echo '<script>showMessage("Not Valid Information!",-1, 300000);</script>';
}
else
{
    $contentID = $_GET["contentID"];
    $currentPage = isset($_GET["pageToLoad"]) ? $_GET["pageToLoad"] : '1';
    $checkOnSubmit = false;
    $editMode = (isset($_REQUEST["mode"])) ? $_REQUEST["mode"] : "editable";

    echo '<script>goToTokenPage(' . $currentPage . ',' . $checkOnSubmit . ');</script>';
}
?>

<div class="dataTranslation" id="dataTranslationDiv">
    <form method="POST" id="dataTranslationForm" enctype='multipart/form-data'>
        <input type="hidden" id="ContentID" name="ContentID" value="<?php echo $contentID; ?>">
        <input type="hidden" id="EditMode" name="EditMode" value="<?php echo $editMode; ?>">
        <input type="hidden" id="task" name="task" value="loadTokenPage">
        <table width="700" id = "tableInfo">
        </table>
    </form>
</div>
