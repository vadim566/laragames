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
</head>

<?php
require_once 'Questionnaire.data.php';
$drp_LangForm = LanguageDropBox();
?>

<body>

<div class="container">
    <div class="p-3 mb-2 bg-warning text-dark">
        <p class="lead">This app has been mostly tested in Chrome and FireFox. We recommend that you use one of those browsers.</p>
    </div>

<form method="POST" id="DemographicForm" name="DemographicForm" action="EuroCallQuestionnaire.php">
    <fieldset class="border p-2">
        <legend class="w-auto">Demographic Info</legend>

        <div class="form-group row">
            <label for="NameByUser" class="col-sm-3 col-form-label">Name:    <span class="badge bg-secondary text-white">optional</span></label>
            <div class="col-sm-5">
                <input type="text" class="form-control" id="NameByUser" name="NameByUser">
            </div>
        </div>
        <div class="form-group row">
            <label for="staticLangName" class="col-sm-3 col-form-label">Language: </label>
            <div class="col-sm-5">
                <?php echo $drp_LangForm; ?>
            </div>
        </div>
        <div class="form-group row">
            <label for="UserGender" class="col-sm-3 col-form-label">Gender:</label>
            <div class="col-sm-5">
                <select class="form-control" id="UserGender" name="UserGender" required>
                    <option value="">Please select..</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="nonBinary">Non binary</option>
                    <option value="notSaid">Prefer not to say</option>
                </select>
            </div>
        </div>
        <div class="form-group row">
            <label for="UserBirthYear" class="col-sm-3 col-form-label">Year of birth:</label>
            <div class="col-sm-5">
                <select class="form-control" id="UserBirthYear" name="UserBirthYear" required>
                    <option value="">Please select..</option>
                    <?php for($i = 1920; $i < 2021; $i++)
                        echo "<option value='$i'>$i</option>";
                    ?>
                </select>
            </div>
        </div>
        <div class="form-group row">
            <label for="EducationBackground" class="col-sm-3 col-form-label">Educational background:</label>
            <div class="col-sm-5">
                <select class="form-control" id="EducationBackground" name="EducationBackground" required>
                    <option value="">Please select..</option>
                    <option value="primary">Primary</option>
                    <option value="secondary">Secondary</option>
                    <option value="tertiary">Tertiary</option>
                    <option value="postgraduate">Postgraduate</option>
                </select>
            </div>
        </div>
        <div class="form-group row">
            <label for="LanguageExpertise" class="col-sm-3 col-form-label">Level of expertise in this language:</label>
            <div class="col-sm-5">
                <select class="form-control" id="LanguageExpertise" name="LanguageExpertise" required>
                    <option value="">Please select..</option>
                    <option value="native">Native speaker</option>
                    <option value="nearNative">Near-native</option>
                    <option value="advanced">Advanced</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="beginner">Beginner</option>
                </select>
            </div>
        </div>
        <div class="form-group row">
            <label for="TeachingExperience" class="col-sm-5 col-form-label">Do have experience with teaching this language?</label>
            <div class="col-sm-4">
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="TeachingExperience" id="TeachingExperienceY" value="yes" required>
                    <label class="form-check-label" for="TeachingExperienceY">Yes</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="TeachingExperience" id="TeachingExperienceN" value="no" required>
                    <label class="form-check-label" for="TeachingExperienceN">No</label>
                </div>
            </div>
        </div>
        <div class="form-group row">
            <label for="HearingImpairment" class="col-sm-5 col-form-label">Do you have any hearing impairments?</label>
            <div class="col-sm-4">
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="HearingImpairment" id="HearingImpairmentY" value="yes" required>
                    <label class="form-check-label" for="HearingImpairmentY">Yes</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="HearingImpairment" id="HearingImpairmentN" value="no" required>
                    <label class="form-check-label" for="HearingImpairmentN">No</label>
                </div>
            </div>
        </div>
        <div class="form-group row">
            <label for="ReadingImpairment" class="col-sm-5 col-form-label">Do you have any reading impairments?</label>
            <div class="col-sm-4">
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="ReadingImpairment" id="ReadingImpairmentY" value="yes" required>
                    <label class="form-check-label" for="ReadingImpairmentY">Yes</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="ReadingImpairment" id="ReadingImpairmentN" value="no" required>
                    <label class="form-check-label" for="ReadingImpairmentN">No</label>
                </div>
            </div>
        </div>
        <div class="form-group row">
            <div class="col-sm-4">
                <button type="submit" class="btn btn-primary">Go to the questionnaire</button>
            </div>
        </div>
    </fieldset>
</form>
<div class="p-3 mb-2 bg-warning text-dark">
    <p class="lead">Technical problems? <a href="mailto:hanieh.habibi@unige.ch">Contact us.</a></p>
</div>
</div>
</body>
</html>