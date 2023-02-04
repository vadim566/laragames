<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 6/6/2019

 */

?>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<?php
    $now = new DateTime();
    echo '<link rel="stylesheet" href="../css/MainContent.css?' . $now->format('His') . '">';
    echo '<script src="../js/DataTranslation.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';

if(!isset($_GET["contentID"]))
{
        echo '<script>showMessage("Not Valid Information!",-1, 300000);</script>';
}
else
{
    $contentID = $_GET["contentID"];
    $justNote = isset($_GET["justNote"]) ? 'yes' : 'no';
    $currentPage = isset($_GET["page"]) ? $_GET["page"] : '1';
    $checkOnSubmit = false;

    echo '<script>goToLemmaPage(' . $currentPage . ',' . $checkOnSubmit . ');</script>';
}

?>
<div class="dataTranslation" id="dataTranslationDiv">
    <form method="POST" id="dataTranslationForm" enctype='multipart/form-data'>
        <input type="hidden" id="ContentID" name="ContentID" value="<?php echo $contentID; ?>">
        <input type="hidden" id="JustNote" name="JustNote" value="<?php echo $justNote; ?>">
        <input type="hidden" id="task" name="task" value="loadLemmaPage">
        <table width="700" id = "tableInfo">
        </table>
    </form>
</div>