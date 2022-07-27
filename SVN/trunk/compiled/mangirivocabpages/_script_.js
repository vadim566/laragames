
    !localStorage && (l = location, p = l.pathname.replace(/(^..)(:)/, "$1$$"), (l.href = l.protocol + "//127.0.0.1" + p)); /* SOME STRANGE IE HACK! */
    var mySettings = {};
    function myPath() {
        return window.location.href.substring( 0, window.location.href.lastIndexOf('/') );
    }
    function myFile() {
        return window.location.href.substring( window.location.href.lastIndexOf('/') ) ;
    }
    function myBaseFile() {
        return window.location.href.substring( window.location.href.lastIndexOf('/') ).split('#')[0] ;
    }
    function myHash() {
        return window.location.hash;
    }
    function scrollToHash() {
        var hash = myHash() ;
        if ( !hash || hash.length < 2 ) return ;
        var toolbarHeight = 0;
        $('#toolbar').each(function() { toolbarHeight = $(this).height(); } )
        $(document.body).animate( { 'scrollTop': $(myHash()).offset().top - toolbarHeight - 32}, 500 );
        var firstParent = $(hash).parents("p,h1,h2,td").first();
        if ( firstParent ) {
            firstParent.addClass("hashhighlight");
            window.setTimeout(function() { firstParent.removeClass("hashhighlight"); }, 2000 );
        }
    }
    function defaultSettings() {
        return { bookmark: '', show_translation: false } ;
    }
    function loadSettings() {
        try {
            mySettings = JSON.parse( localStorage.getItem( myPath() ) ) ;
        }
        catch(e) {
            // ignore error from corrupted local storage
        }
        if ( ! mySettings || typeof mySettings != 'object' ) {
            mySettings = defaultSettings();
        }
    }
    function saveSettings() {
        localStorage.setItem( myPath(), JSON.stringify( mySettings ) ) ;
    }
    $(document).ready(function() {
        loadSettings() ;
        $('.link_as_button').click(function() {
            var target = $(this).data('target');
            var href   = $(this).data('href');
            if ( ! href ) return ;
            if ( ! target ) target = "_self" ;
            if ( target == "_self" && window.hasOwnProperty( "leavePageFunction" ) ) {
                leavePageFunction( function() { window.open( href, target ); } );
            }
            else {
                window.open( href, target );
            }
        });
        $(window).on( 'hashchange', function( e ) {
            scrollToHash();
        });
        scrollToHash() ;
    });
    
    function playSound(soundfile) {
        document.getElementById("audio_container").innerHTML=
            "<audio id='audioFile' src='" + soundfile +"'></audio>";
		var audio = document.getElementById("audioFile");
        audio.play();
    }
    
    function playSoundPart(soundfile, fromTime, toTime) {
        document.getElementById("audio_container").innerHTML=
            "<audio id='audioFile' src='" + soundfile +"'></audio>";
		var audio = document.getElementById("audioFile");
		audio.currentTime=fromTime;
        audio.play();
		var i = setInterval(function(){
			if(audio.currentTime>toTime){
				audio.pause();
				clearInterval(i)
				}
				},5);
    }
    
