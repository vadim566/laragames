<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 6/19/2020

 */

?>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<?php
$now = new DateTime();
echo '<link rel="stylesheet" href="../css/MainContent.css?' . $now->format('His') . '">';
echo '<script src="../js/MultiWordLexicons.js?' . $now->format('His') . '"></script>';
echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';

if(!isset($_GET["languageID"]))
{
    echo '<script>showMessage("Not Valid Information!",-1, 300000);</script>';
}
else
{
    $languageID = $_GET["languageID"];
    $currentPage = isset($_GET["page"]) ? $_GET["page"] : '1';
    $checkOnSubmit = false;

    echo '<script>goToTransformPage(' . $currentPage . ',' . $checkOnSubmit . ');</script>';
}

?>
<div class="multiWordLexicon" id="multiWordLexiconDiv">
    <form method="POST" id="MultiWordLexiconForm" enctype='multipart/form-data'>
        <input type="hidden" id="LanguageID" name="LanguageID" value="<?php echo $languageID; ?>">
        <table width="700" id = "tableInfo">
        </table>
    </form>
</div>