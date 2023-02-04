$( document ).ready(function() {
    $('#cssmenu ul ul li:odd').addClass('odd');
    $('#cssmenu ul ul li:even').addClass('even');
    $('#cssmenu > ul > li > a').click(function() {
        $('#cssmenu li').removeClass('active');
        $(this).closest('li').addClass('active');
        var checkElement = $(this).next();
        if((checkElement.is('ul')) && (checkElement.is(':visible'))) {
            $(this).closest('li').removeClass('active');
            checkElement.slideUp('normal');
        }
        if((checkElement.is('ul')) && (!checkElement.is(':visible'))) {
            $('#cssmenu ul ul:visible').slideUp('normal');
            checkElement.slideDown('normal');
        }
        if($(this).closest('li').find('ul').children().length == 0) {
            return true;
        } else {
            return false;
        }
    });

    $('#cssmenu > ul > li > ul > li > a').click(function() {

        $('#cssmenu ul ul li ').removeClass('active');
        $(this).closest('li').addClass('active');
        event.preventDefault();
        $("#mainContentDIV").load(this.getAttribute('href'));
    });


    $("#LogoutForm").submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.
        var form = $(this);
        var url = form.attr('action');
        var type = form.attr('method');
        var data = "task=userLogout";

        $.ajax({
            type: type,
            url: url,
            data: data,
            success: function(response) {
                window.location = "../view/index.php?status=logout";
            }
        });
    });
});


