<!DOCTYPE html>
<html lang="en">
<head>
    <title>LARA Evaluation Form</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script src="questionnaire.js"></script>

    <style>
        span{
            cursor: pointer;
        }
    </style>

</head>

<?php

require_once 'Questionnaire.data.php';

$temp = InsertUser();

if($temp == false)
{
    echo "Something goes wrong";
    die();
}
$userName = $temp["UserName"];
$versionOne = $temp["VersionOne"];
$questions = GetQuestions();
?>

<body>
<div class="jumbotron">
    <div class="container">
        <h1 class="display-4">Instructions</h1>
        <p class="lead">For each item, please listen to version one and version two of the audio and pick the response you think fits best.<br/>
            Try to think about whether the audio is good for teaching this language rather than your personal preferences.</p>
        <p class="lead">Technical problems? <a href="mailto:hanieh.habibi@unige.ch">Contact us.</a></p>
    </div>
</div>
<div class="container">
    <form method="post" name="EvaluationForm" id="EvaluationForm" enctype='multipart/form-data'>
    <?php
    echo "<input type='hidden' name='UserName' id='UserName' value='" . $userName . "'>";
    echo "<input type='hidden' name='QuestionnaireID' id='QuestionnaireID' value='" . $_REQUEST["QuestionnaireID"] . "'>";
    echo "<input type='hidden' name='task' value='SaveEvaluation'>";

    $callectorWebAddress = "https://www.issco.unige.ch/en/research/projects/callector/";

    for($i = 0; $i < count($questions); $i++)
    {
        $v1File = ($versionOne == 'human') ? $questions[$i]["HumanAudioDir"] . $questions[$i]["HumanAudioFile"] :
                                             $questions[$i]["TtsAudioDir"] . $questions[$i]["TtsAudioFile"];
        $v2File = ($versionOne == 'human') ? $questions[$i]["TtsAudioDir"] . $questions[$i]["TtsAudioFile"] :
                                             $questions[$i]["HumanAudioDir"] . $questions[$i]["HumanAudioFile"] ;

        $SegmentName = 'Segment**' . $questions[$i]["SegmentID"];
        $SegmentID = 'ID**Segment**' . $questions[$i]["SegmentID"];
        echo  "<div class='form-group'>";
        echo "<label>" . $questions[$i]["SegmentText"] . "</label>";
        echo "<h6>Version 1: <span class='badge badge-info' onclick=\"play('" . $callectorWebAddress . $v1File . "');\">Play &#9658;</span></h6>";
        echo "<h6>Version 2: <span class='badge badge-info' onclick=\"play('" . $callectorWebAddress . $v2File . "');\">Play &#9658;</span></h6>";
        echo "          
              <div class='form-check'>
                <input class='form-check-input' type='radio' name=$SegmentName id='1_$SegmentID' value='1' required>
                <label class='form-check-lanel' for='1_$SegmentID'>Both versions are acceptable and equally good</label>
              </div>
              <div class='form-check'>
                <input class='form-check-input' type='radio' name=$SegmentName id='2_$SegmentID' value='2' required>
                <label class='form-check-lanel' for='2_$SegmentID'>Both versions are acceptable, but version 1 is clearly better</label>
              </div>
              <div class='form-check'>
                <input class='form-check-input' type='radio' name=$SegmentName id='3_$SegmentID' value='3' required>
                <label class='form-check-lanel' for='3_$SegmentID'>Both versions are acceptable, but version 2 is clearly better</label>             
              </div>
              <div class='form-check'>
                <input class='form-check-input' type='radio' name=$SegmentName id='4_$SegmentID' value='4' required>
                <label class='form-check-lanel' for='4_$SegmentID'>Version 1 is acceptable, version 2 is not acceptable</label>             
              </div>
              <div class='form-check'>
                <input class='form-check-input' type='radio' name=$SegmentName id='5_$SegmentID' value='5' required>
                <label class='form-check-lanel' for='5_$SegmentID'>Version 1 is not acceptable, version 2 is acceptable</label>             
              </div>
              <div class='form-check'>
                <input class='form-check-input' type='radio' name=$SegmentName id='6_$SegmentID' value='6' required>
                <label class='form-check-lanel' for='6_$SegmentID'>Neither one is acceptable</label>             
              </div>";
        echo "</div>";
        echo "<hr>";
    }
?>
        <p class="h4">
            What did you think of the Version 1 voice as a whole? (1-5, 1 is strongly disagree, 5 is strongly agree)
        </p>
        <div class='form-group'>
            <label>Individual words were correctly pronounced.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__1" id="1__11" value="1" required>
                <label class="form-check-label" for="1__11">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__1" id="1__12" value="2" required>
                <label class="form-check-label" for="1__12">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__1" id="1__13" value="3" required>
                <label class="form-check-label" for="1__13">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__1" id="1__14" value="4" required>
                <label class="form-check-label" for="1__14">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__1" id="1__15" value="5" required>
                <label class="form-check-label" for="1__15">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>Each sentence as a whole was correctly pronounced.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__2" id="1__21" value="1" required>
                <label class="form-check-label" for="1__21">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__2" id="1__22" value="2" required>
                <label class="form-check-label" for="1__22">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__2" id="1__23" value="3" required>
                <label class="form-check-label" for="1__23">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__2" id="1__24" value="4" required>
                <label class="form-check-label" for="1__24">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__2" id="1__25" value="5" required>
                <label class="form-check-label" for="1__25">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>Speed of speech was appropriate.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__3" id="1__31" value="1" required>
                <label class="form-check-label" for="1__31">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__3" id="1__32" value="2" required>
                <label class="form-check-label" for="1__32">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__3" id="1__33" value="3" required>
                <label class="form-check-label" for="1__33">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__3" id="1__34" value="4" required>
                <label class="form-check-label" for="1__34">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__3" id="1__35" value="5" required>
                <label class="form-check-label" for="1__35">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>The voice sounded natural.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__4" id="1__41" value="1" required>
                <label class="form-check-label" for="1__41">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__4" id="1__42" value="2" required>
                <label class="form-check-label" for="1__42">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__4" id="1__43" value="3" required>
                <label class="form-check-label" for="1__43">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__4" id="1__44" value="4" required>
                <label class="form-check-label" for="1__44">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__4" id="1__45" value="5" required>
                <label class="form-check-label" for="1__45">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>The voice was pleasant to listen to.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__5" id="1__51" value="1" required>
                <label class="form-check-label" for="1__51">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__5" id="1__52" value="2" required>
                <label class="form-check-label" for="1__52">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__5" id="1__53" value="3" required>
                <label class="form-check-label" for="1__53">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__5" id="1__54" value="4" required>
                <label class="form-check-label" for="1__54">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__5" id="1__55" value="5" required>
                <label class="form-check-label" for="1__55">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>The voice would be acceptable for teaching purposes.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__6" id="1__61" value="1" required>
                <label class="form-check-label" for="1__61">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__6" id="1__62" value="2" required>
                <label class="form-check-label" for="1__62">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__6" id="1__63" value="3" required>
                <label class="form-check-label" for="1__63">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__6" id="1__64" value="4" required>
                <label class="form-check-label" for="1__64">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__6" id="1__65" value="5" required>
                <label class="form-check-label" for="1__65">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>I would recommend learners to use this voice as a model for imitating.  </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__7" id="1__71" value="1" required>
                <label class="form-check-label" for="1__71">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__7" id="1__72" value="2" required>
                <label class="form-check-label" for="1__72">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__7" id="1__73" value="3" required>
                <label class="form-check-label" for="1__73">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__7" id="1__74" value="4" required>
                <label class="form-check-label" for="1__74">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="1__7" id="1__75" value="5" required>
                <label class="form-check-label" for="1__75">5</label>
            </div>
        </div>
        <div class="form-group">
            <label for="OverallV1">In your own words, how did you experience this voice?</label>
            <input type="text" class="form-control" id="OverallV1" name="OverallV1">
        </div>
        <hr>
        <p class="h4">
            What did you think of the Version 2 voice as a whole? (1-5, 1 is strongly disagree, 5 is strongly agree)
        </p>
        <div class='form-group'>
            <label>Individual words were correctly pronounced.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__1" id="2__11" value="1" required>
                <label class="form-check-label" for="2__11">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__1" id="2__12" value="2" required>
                <label class="form-check-label" for="2__12">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__1" id="2__13" value="3" required>
                <label class="form-check-label" for="2__13">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__1" id="2__14" value="4" required>
                <label class="form-check-label" for="2__14">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__1" id="2__15" value="5" required>
                <label class="form-check-label" for="2__15">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>Each sentence as a whole was correctly pronounced.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__2" id="2__21" value="1" required>
                <label class="form-check-label" for="2__21">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__2" id="2__22" value="2" required>
                <label class="form-check-label" for="2__22">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__2" id="2__23" value="3" required>
                <label class="form-check-label" for="2__23">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__2" id="2__24" value="4" required>
                <label class="form-check-label" for="2__24">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__2" id="2__25" value="5" required>
                <label class="form-check-label" for="2__25">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>Speed of speech was appropriate.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__3" id="2__31" value="1" required>
                <label class="form-check-label" for="2__31">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__3" id="2__32" value="2" required>
                <label class="form-check-label" for="2__32">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__3" id="2__33" value="3" required>
                <label class="form-check-label" for="2__33">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__3" id="2__34" value="4" required>
                <label class="form-check-label" for="2__34">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__3" id="2__35" value="5" required>
                <label class="form-check-label" for="2__35">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>The voice sounded natural.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__4" id="2__41" value="1" required>
                <label class="form-check-label" for="2__41">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__4" id="2__42" value="2" required>
                <label class="form-check-label" for="2__42">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__4" id="2__43" value="3" required>
                <label class="form-check-label" for="2__43">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__4" id="2__44" value="4" required>
                <label class="form-check-label" for="2__44">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__4" id="2__45" value="5" required>
                <label class="form-check-label" for="2__45">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>The voice was pleasant to listen to.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__5" id="2__51" value="1" required>
                <label class="form-check-label" for="2__51">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__5" id="2__52" value="2" required>
                <label class="form-check-label" for="2__52">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__5" id="2__53" value="3" required>
                <label class="form-check-label" for="2__53">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__5" id="2__54" value="4" required>
                <label class="form-check-label" for="2__54">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__5" id="2__55" value="5" required>
                <label class="form-check-label" for="2__55">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>The voice would be acceptable for teaching purposes.   </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__6" id="2__61" value="1" required>
                <label class="form-check-label" for="2__61">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__6" id="2__62" value="2" required>
                <label class="form-check-label" for="2__62">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__6" id="2__63" value="3" required>
                <label class="form-check-label" for="2__63">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__6" id="2__64" value="4" required>
                <label class="form-check-label" for="2__64">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__6" id="2__65" value="5" required>
                <label class="form-check-label" for="2__65">5</label>
            </div>
        </div>
        <div class='form-group'>
            <label>I would recommend learners to use this voice as a model for imitating.  </label>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__7" id="2__71" value="1" required>
                <label class="form-check-label" for="2__71">1</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__7" id="2__72" value="2" required>
                <label class="form-check-label" for="2__72">2</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__7" id="2__73" value="3" required>
                <label class="form-check-label" for="2__73">3</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__7" id="2__74" value="4" required>
                <label class="form-check-label" for="2__74">4</label>
            </div>
            <div class='form-check form-check-inline'>
                <input class="form-check-input" type="radio" name="2__7" id="2__75" value="5" required>
                <label class="form-check-label" for="2__75">5</label>
            </div>
        </div>
        <div class="form-group">
            <label for="OverallV2">In your own words, how did you experience this voice?</label>
            <input type="text" class="form-control" id="OverallV2" name="OverallV2">
        </div>
        <div class="p-3 mb-2 bg-warning text-dark">
            <p class="lead">Please press the "Submit results" button in order to save your answers.</p>
        </div>
        <div class='form-group'>
            <button type="submit" class="btn btn-primary">Submit results</button>
        </div>
</form>
</div>
<div id="audio_container" style="width:0;height:0;overflow:hidden"></div></div>
</body>
</html>
