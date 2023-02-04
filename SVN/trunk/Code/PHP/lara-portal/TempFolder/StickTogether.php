<!DOCTYPE html>
<html lang="en">

<head>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

    <script type = "text/javascript">
        function StickTogether()
        {
            var data = { task: "StickTogether"};
            $.ajax({
                url         : '../data/Content.data.php',
                data        : data,
                type        : 'GET',
                contentType : 'application/json; charset=utf-8',

                success: function (response) {
                    var reqResponse = $.parseJSON(response);
                    var responseMsg = reqResponse[0].resultMsg;
                    var responseID =  reqResponse[0].id;
                    alert(responseMsg);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log(textStatus, errorThrown);
                    alert("Something is wrong here.");
                }
            });

        }
    </script>
</head>

<body>
<input type="button" id="StickTogether" name="StickTogether" onclick="StickTogether()"  value="Stick together">
</body>

<script  type="text/javascript" src="../js/jquery.min.js"></script>

</html>

