<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 6/19/2020

 */

?>

<link rel="stylesheet" type="text/css" href="../SharedModules/jquery/jquery-ui.css">
<link rel="stylesheet" href="../css/TableToDiv.css">

<?php
$now = new DateTime();
echo '<link rel="stylesheet" href="../css/MainContent.css?' . $now->format('His') . '">';

echo '<script src="../js/MultiWordLexicons.js?' . $now->format('His') . '"></script>';
echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

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

    echo '<script>goToMwePage(' . $currentPage . ',' . $checkOnSubmit . ');</script>';
}

?>

<div class="multiWordLexicon" id="multiWordLexiconDiv">
    <div><img src="../img/document-add-icon.png" onclick="beforeAddNewMWE();"></div>
    <form method="POST" id="MultiWordLexiconForm" enctype='multipart/form-data'>
        <input type="hidden" id="LanguageID" name="LanguageID" value="<?php echo $languageID; ?>">
        <input type="hidden" id="CurrentPage" name="CurrentPage" value="<?php echo $currentPage; ?>">
        <table width="700" id = "tableInfo">
        </table>
    </form>
</div>

<div id="newLexiconMWEDiv" style="display: none">
    <form method="POST" id="NewMultiWordLexiconForm" enctype='multipart/form-data'>
        <input type="hidden" id="task" name="task" value="saveNewMWE">
        <input type="hidden" id="LanguageID" name="LanguageID" value="<?php echo $languageID; ?>">
        <div class="table">
            <div class="tr">
                <div class="tdTitle">Definition:</div>
                <div class="tdInput">
                    <input type="text" name="MweHeader" id="MweHeader"  size="20">
                </div>
            </div>
            <div class="tr">
                <div class="tdTitle">Multi word:</div>
                <div class="tdInput">
                    <input type="text" name="MweName" id="MweName"  size="20">
                </div>
            </div>
            <div class="tr">
                <div class="tdTitle">Multi word pos:</div>
                <div class="tdInput">
                    <input type="text" name="MwePos" id="MwePos"  size="20">
                </div>
            </div>
        </div>
    </form>
</div>