
import lara_top
import lara_abstract_html
import lara_translations
import lara_audio
import lara_utils
import lara_postags
import lara_replace_chars
import lara_extra_info
import lara_config

# ------------------------------------------------

# HTML for the main file

# Header

def hyperlinked_text_file_header(FirstMainFile, Params):
    if Params.html_style == 'old':
        return hyperlinked_text_file_header_old(FirstMainFile, Params)
    elif Params.html_style == 'new':
        return hyperlinked_text_file_header_new(FirstMainFile, Params)
    else:
        lara_utils.print_and_flush(f'*** Error: bad value for Params.html_style in call to lara_html.hyperlinked_text_file_header: {Params.html_style}')
        return False

def hyperlinked_text_file_header_old(FirstMainFile, Params):
    return [f'{html_tag_for_vocab_pages(Params)}',  
	    '<head>',
		f'<title>{hyperlinked_text_title(Params)}</title>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
		link_to_css_files(Params),
	    #'<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>',
            link_to_jquery(Params),
	    '<script language="javascript" type="text/javascript">',
            hyperlinked_text_file_scriptfunction(Params),
	    '</script>'] + \
            maphilight_scripts(Params) + \
	    ['</head>',
	    '<body class="noscroll">',
            f'{aux_frame_div(Params)}',
	    '',
            f'{div_split_main_text_tag(FirstMainFile, Params)}']

def hyperlinked_text_file_header_new(FirstMainFile, Params):
    return [f'{html_tag_for_vocab_pages(Params)}',  
	    '<head>',
		f'<title>{hyperlinked_text_title(Params)}</title>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
		link_to_css_files(Params),
		link_to_jquery(Params),
	    '<script language="javascript" type="text/javascript">',
            hyperlinked_text_file_scriptfunction(Params),
	    '</script>'] + \
            maphilight_scripts(Params) + \
	    ['</head>',
	    '<body class="noscroll">',
        #f'{aux_frame_div(Params)}',
	#    '',
        #f'{div_split_main_text_tag(FirstMainFile, Params)}'
        iframe_main_text_tag(FirstMainFile, Params)
            ]
            
##def maphilight_scripts(Params):
##    if Params.picturebook == 'yes':
##        return [
##            #"<script type='text/javascript' src='http://davidlynch.org/projects/maphilight/jquery.maphilight.js'></script>",
##            "<script type='text/javascript' src='https://cdnjs.cloudflare.com/ajax/libs/maphilight/1.4.2/jquery.maphilight.js'></script>",
##                '<script type="text/javascript">',
##                '    $(document).ready(function () {',
##                "        $('.map').maphilight({ strokeColor: '00ff00' });"
##                '    });'  
##                '</script>']
##    else:
##        return []

def maphilight_scripts(Params):
    return [
        #"<script type='text/javascript' src='http://davidlynch.org/projects/maphilight/jquery.maphilight.js'></script>",
        "<script type='text/javascript' src='https://cdnjs.cloudflare.com/ajax/libs/maphilight/1.4.2/jquery.maphilight.js'></script>",
            '<script type="text/javascript">',
            '    $(document).ready(function () {',
            "        $('.map').maphilight({ strokeColor: '00ff00' });"
            '    });'  
            '</script>']

# Closing

def hyperlinked_text_file_closing(Params):
    return ['</body>', '</html>' ]

# ------------------------------------------------

def main_text_file_header(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params):
    #lara_utils.print_and_flush(f'--- main_text_file_header: Params.html_style = {Params.html_style}')
    if Params.html_style == 'old':
        return main_text_file_header_old(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params)
    elif Params.html_style == 'new':
        return main_text_file_header_new(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params)
    elif Params.html_style == 'social_network':
        return main_text_file_header_social_network(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params)

def main_text_file_header_old(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params):
    return [f'{html_tag_for_vocab_pages(Params)}',  
	    '<head>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
	    link_to_css_files(Params),
	    link_to_jquery(Params)] + \
            maphilight_scripts(Params) + \
	    [link_to_script_files(Params),
	    '</head>',
	    '<body>',
	    #Move to close to stop text jumping when audio is accessed
	    #'<span id="audio_container" style="visibility: hidden;"></span>',
	    main_text_toolbar(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params),
        '<div class="text_content main_text_page">'
		]

def main_text_file_header_new(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params):
    return [f'{html_tag_for_vocab_pages(Params)}',  
	    '<head>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
	    link_to_css_files(Params),
	    link_to_jquery(Params)] + \
            maphilight_scripts(Params) + \
	    [link_to_script_files(Params),
	    '</head>',
	    '<body>',
	    #Move to close to stop text jumping when audio is accessed
	    #'<span id="audio_container" style="visibility: hidden;"></span>',
	    main_text_toolbar(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params),
        '<div class="split main_frame">',
        '<div class="text_content main_text_page">'
		]

##def hyperlinked_text_file_header_new(FirstMainFile, Params):
##    return [f'{html_tag_for_vocab_pages(Params)}',  
##	    '<head>',
##		f'<title>{hyperlinked_text_title(Params)}</title>',
##	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
##		link_to_css_files(Params),
##		link_to_jquery(Params),
##	    '<script language="javascript" type="text/javascript">',
##        hyperlinked_text_file_scriptfunction(Params),
##	    '</script>',
##	    '</head>',
##	    '<body class="noscroll">',
##        #f'{aux_frame_div(Params)}',
##	#    '',
##        #f'{div_split_main_text_tag(FirstMainFile, Params)}'
##        iframe_main_text_tag(FirstMainFile, Params)
##            ]

def main_text_file_header_social_network(PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params):
    return []


# Closing

def main_text_file_closing(PrecedingMainFile, FollowingMainFile, Params):
    if Params.html_style == 'old':
        return main_text_file_closing_old(PrecedingMainFile, FollowingMainFile, Params)
    elif Params.html_style == 'new':
        return main_text_file_closing_new(PrecedingMainFile, FollowingMainFile, Params)
    elif Params.html_style == 'social_network':
        return main_text_file_closing_social_network(PrecedingMainFile, FollowingMainFile, Params)

def main_text_file_closing_old(PrecedingMainFile, FollowingMainFile, Params):
    return [#'<span id="audio_container" style="visibility: hidden;"></span>',
            '<div id="audio_container" style="width:0;height:0;overflow:hidden"></div>',
            '</div>',
            '</body>',
            '</html>']

def main_text_file_closing_new(PrecedingMainFile, FollowingMainFile, Params):
    return ['<div id="audio_container" style="width:0;height:0;overflow:hidden"></div>',
            '</div>',
            '</div>',
            div_iframe_aux_frame_tag(Params),
            '</body>',
            '</html>']

def main_text_file_closing_social_network(PrecedingMainFile, FollowingMainFile, Params):
    return []

def links_to_preceding_and_following_main_files(Preceding, Following, FirstMainFile, Params):
    PreviousArrow = lara_extra_info.previous_arrow_html_code(Params)
    NextArrow = lara_extra_info.next_arrow_html_code(Params)
    UpArrow = lara_extra_info.up_arrow_html_code(Params)
    if not Preceding and not Following: return ''
    PrecedingLink = f'<button id="previous_page_button" class="link_as_button" title="{lara_config.get_ui_text("prev_page_title",Params)}" data-href="{Preceding}">{PreviousArrow}</button></span>' if Preceding else f'<button class="link_as_button disabled">{PreviousArrow}</button>'
    FollowingLink = f'<button id="next_page_button" class="link_as_button" title="{lara_config.get_ui_text("next_page_title",Params)}" data-href="{Following}">{NextArrow}</button></span>' if Following else f'<button class="link_as_button disabled">{NextArrow}</button>'
    FirstLink     = f'<button id="first_page_button" class="link_as_button" title="{lara_config.get_ui_text("first_page_title",Params)}" data-href="{FirstMainFile}">{UpArrow}</button>' if FirstMainFile and Preceding else f'<button class="link_as_button disabled">{UpArrow}</button>'
    return f'{PrecedingLink} {FirstLink} {FollowingLink}'

def link_to_table_of_contents(Params):
    DataTarget = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
    ButtonText = lara_config.get_ui_text('table_of_contents', Params)
    return f"<button id='button_toc' class='link_as_button' data-target='{DataTarget}' data-href='_toc_.html'>{ButtonText}</button>"

def link_to_frequency_list(FreqFile, Params):
    if Params.frequency_lists_in_main_text_page == 'yes':
        DataTarget = lara_utils.split_screen_pane_name_for_main_text_screen(Params)
    else:
        DataTarget = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
    ButtonText = lara_config.get_ui_text('frequency_index', Params)
    return f"<button id='button_toc' class='link_as_button' data-target='{DataTarget}' data-href='{FreqFile}'>{ButtonText}</button>"
    
def link_to_alphabetical_list(AlphabetFile, Params):
    if Params.frequency_lists_in_main_text_page == 'yes':
        DataTarget = lara_utils.split_screen_pane_name_for_main_text_screen(Params)
    else:
        DataTarget = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
    ButtonText = lara_config.get_ui_text('alphabetical_index', Params)
    return f"<button id='button_toc' class='link_as_button' data-target='{DataTarget}' data-href='{AlphabetFile}'>{ButtonText}</button>"

def hyperlinked_text_file_scriptfunction(Params):
    return """
        function jumpToHash() {
            var mainHash = window.location.hash ;
            // Format of the main hash: "#<pageno>[/<segmentno>]"
            var match = mainHash && mainHash.match( "^#([1-9][0-9]*)(/([1-9][0-9]*))?$" ) ;
            if ( match ) {
                var newFrameSrc = "_main_text_" + match[1] + "_.html" ;
                if ( match[3] ) newFrameSrc = newFrameSrc + "#page_" + match[1] + "_segment_" + match[3] ;
                $("#main_frame").attr( "src", newFrameSrc ) ;
            }
        }
	    $(document).ready(function() {
            var thediv = document.getElementById( "aux_frame_div" ) ; // Find the div
            document.body.appendChild(thediv); // Move it to the end of the body
            thediv.style.display = "block"; // and make it visible
            $(window).on( 'hashchange', function( e ) {
                jumpToHash() ;
            });
            jumpToHash() ;
        });
    """

def toggle_translation_scriptfunction(Params):
	if Params.toggle_translation_button == 'yes':
		return """
	    $(document).ready(function() {
	        // add a hidden <X.seg_trans> after each <span> that has an <X> parent (i.e. the "speaker" spans)
	        $('p>span[title]').each(function(){
	            $( "<p class='seg_trans hidden'>"+$(this).attr("title")+"</p>" ).insertAfter( $(this).parent("p") );
	        });
	        $('h1>span[title]').each(function(){
	            $( "<h1 class='seg_trans hidden'>"+$(this).attr("title")+"</h1>" ).insertAfter( $(this).parent("h1") );
	        });
	        $('h2>span[title]').each(function(){
	            $( "<h2 class='seg_trans hidden'>"+$(this).attr("title")+"</h2>" ).insertAfter( $(this).parent("h2") );
	        });
	        $('#button_seg_trans_toggle').click(function() {
	            $('.seg_trans').toggleClass('hidden');
                mySettings.show_translation = ! mySettings.show_translation;
                saveSettings();
	        });
            if ( mySettings.show_translation ) {
                $('.seg_trans').removeClass('hidden');
            }
	    });
		"""
	return ''	

def bookmark_scriptfunction(Params):
    if Params.allow_bookmark != 'yes': return ''
    return f'_set_bookmark_title = "{lara_config.get_ui_text("set_bookmark", Params)}";' + \
        """
        function gotoBookmark() {
            var bookmark = mySettings.bookmark ;
            if ( bookmark ) {
                if ( bookmark != myFile() ) {
                    window.location.assign( myPath() + bookmark ) ;
                    return ;
                }
                scrollToHash();
            }
        }
	    $(document).ready(function() {
            $("#button_setbookmark").click(function() {
                mySettings.bookmark = myFile() ;
                saveSettings() ;
            });
            $("#button_gotobookmark").click(function() {
                gotoBookmark();
            });
            $("a[id]").each(function() {
                $('<a class="bookmarklink">&nbsp;</a>').
                attr('data-bookmark', myBaseFile() + "#" + $(this).attr("id")).
                attr('title', _set_bookmark_title).
                appendTo($(this).parents("p,h1,h2,td").first());
            });
            $("a.bookmarklink").click(function(){
                mySettings.bookmark = $(this).attr('data-bookmark') ;
                saveSettings() ;
                return false;
            })
            $("p:has(a[id]),h1:has(a[id]),h2:has(a[id]),td:has(a[id])").hover(
              function(){
                  $(this).find('a.bookmarklink').css('display','inline-block');
              },
              function(){
                  $(this).find('a.bookmarklink').css('display','none');
            });
        });
    """

def main_text_toolbar(PageName, PrecedingMainFile, FollowingMainFile, FirstMainFile, CountFile, AlphabeticalFile, Params):
    toolbar_left   = ( '' if Params.toggle_translation_button != 'yes' else f'<button id="button_seg_trans_toggle">{lara_config.get_ui_text("toggle_translation_button", Params)}</button>' )
    toolbar_center = links_to_preceding_and_following_main_files(PrecedingMainFile, FollowingMainFile, FirstMainFile, Params)
    if Params.allow_table_of_contents == 'yes':
        toolbar_center = toolbar_center + " " + link_to_table_of_contents( Params )
    if Params.frequency_list_link_in_nav_bar == 'yes':
        toolbar_center = toolbar_center + " " + link_to_frequency_list( CountFile, Params )
    if Params.alphabetical_list_link_in_nav_bar == 'yes':
        toolbar_center = toolbar_center + " " + link_to_alphabetical_list( AlphabeticalFile, Params )
    if Params.parallel_version_id != '' and Params.parallel_version_label != '':
        toolbar_center = toolbar_center + " " + link_to_parallel_version( PageName, Params )
    if Params.parallel_version_id2 != '' and Params.parallel_version_label2 != '':
        toolbar_center = toolbar_center + " " + link_to_parallel_version2( PageName, Params )
    if Params.parallel_version_id3 != '' and Params.parallel_version_label3 != '':
        toolbar_center = toolbar_center + " " + link_to_parallel_version3( PageName, Params )
    toolbar_right  = '' if Params.allow_bookmark != 'yes' else f'<button id="button_gotobookmark">{lara_config.get_ui_text("goto_bookmark", Params)}</button> <button id="button_setbookmark">{lara_config.get_ui_text("set_bookmark", Params)}</button>'
    if Params.for_reading_portal == 'yes' or not toolbar_left and not toolbar_center and not toolbar_right:
    #if Params.for_reading_portal == 'yes_but_commented_out_for_now' or not toolbar_left and not toolbar_center and not toolbar_right:
        return '' # no toolbar!
    return f"""
        <div id="toolbar" style="text-direction:{Params.text_direction}">
            <div style="">{toolbar_left}</div>
            <div style="text-align:center;">{toolbar_center}</div>
            <div style="text-align:right">{toolbar_right}</div>
        </div>
	    <div id="afterToolbar"></div>
        """
        # empty <p> at the end so that the fixed toolbar does not overlap with the actual text!

# <button id='button_toc' class='link_as_button' data-href='../le_petit_prince_abcvocabpages/_main_text_le_petit_prince_abc_2.html'>Semantic version</button>

def link_to_parallel_version(PageName, Params):
    RelativeDir = f"../{lara_top.lara_short_compiled_dir_for_id('word_pages_directory', Params.parallel_version_id)}"
    FileName = lara_abstract_html.short_name_of_main_text_file(Params.parallel_version_id, PageName)
    return f"<button id='button_toc' class='link_as_button' data-href='{RelativeDir}/{FileName}'>{Params.parallel_version_label}</button>"

def link_to_parallel_version2(PageName, Params):
    RelativeDir = f"../{lara_top.lara_short_compiled_dir_for_id('word_pages_directory', Params.parallel_version_id2)}"
    FileName = lara_abstract_html.short_name_of_main_text_file(Params.parallel_version_id2, PageName)
    return f"<button id='button_toc' class='link_as_button' data-href='{RelativeDir}/{FileName}'>{Params.parallel_version_label2}</button>"

def link_to_parallel_version3(PageName, Params):
    RelativeDir = f"../{lara_top.lara_short_compiled_dir_for_id('word_pages_directory', Params.parallel_version_id3)}"
    FileName = lara_abstract_html.short_name_of_main_text_file(Params.parallel_version_id3, PageName)
    return f"<button id='button_toc' class='link_as_button' data-href='{RelativeDir}/{FileName}'>{Params.parallel_version_label3}</button>"

def init_scriptfunction(Params):
    return """
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
    """ ;

##def playsound_scriptfunction(Params):
##    return """
##    function playSound(soundfile) {
##        document.getElementById("audio_container").innerHTML=
##            "<embed src='" + soundfile +"' autostart='true' loop='false' />";
##    }
##    """
def playsound_scriptfunction(Params):
    return """
    function playSound(soundfile) {
        document.getElementById("audio_container").innerHTML=
            "<audio id='audioFile' src='" + soundfile +"'></audio>";
		var audio = document.getElementById("audioFile");
        audio.play();
    }
    """

def playsound_part_scriptfunction(Params):
    return """
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
    """

def get_audio_tracking_data(Params):
    AudioTrackingDataFile = audio_tracking_data_file(Params)
    if Params.audio_tracking \
        and 'enabled' in Params.audio_tracking \
        and Params.audio_tracking['enabled'] == 'yes' \
        and 'element_to_trackingpoints' in Params.audio_tracking:
        return Params.audio_tracking['element_to_trackingpoints']
    elif AudioTrackingDataFile:
        if not lara_utils.file_exists(AudioTrackingDataFile):
            lara_utils.print_and_flush(f'*** Warning: file not found: {AudioTrackingDataFile}')
            return False
        Content = lara_utils.read_json_file(AudioTrackingDataFile)
        if not Content:
            lara_utils.print_and_flush(f'*** Warning: unable to read file: {AudioTrackingDataFile}')
            return False
        else:
            return Content
    else:
        return False

def audio_tracking_data_file(Params):
    if 'audio_tracking_file' in Params and Params.audio_tracking_file:
        return Params.audio_tracking_file
    elif lara_audio.get_audio_tracking_file_from_tmp_resources(Params):
        return lara_audio.get_audio_tracking_file_from_tmp_resources(Params)
    else:
        return False

##def audio_tracking_scriptfunction(Params):
##    Data = get_audio_tracking_data(Params)
def audio_tracking_scriptfunction(Data):
    if not Data:
        return ''
    script = ''    
    for id in Data:
        script = script + """
    $(document).ready(function() {{
        var tracking_points_{0} = {1} ;
        var playing_p_{0} = null;
        var audio_segments_{0} = [] ;
        var num_segments_{0} = tracking_points_{0}.length - 1 ;
        var audio_element_{0} = document.getElementById( '{0}' ) ;
        if ( ! audio_element_{0} ) return ;
		// 1: find element to track by AUDIOID_line
        var audio_lines_{0} = $('.{0}_line');
		// 2: find <p> or <td> starting with "_{0}_:" (and remove this prefix!)
		if ( audio_lines_{0}.length == 0 ) {{
			audio_lines_{0} = $('p,td').filter( function() {{ return $(this).text().match( "_{0}_:" ) ; }}) ;
			audio_lines_{0}.each( function() {{ 
				$(this).html( $(this).html().replace( /_(<a[^>]*>)?{0}(<\/a>)?_:/, "" ) ); 
			}}) ;
		}}
		// 3: Find all <p> under <audio>'s parent
		if ( audio_lines_{0}.length == 0 ) {{
			audio_lines_{0} = $(audio_element_{0}).parent().nextAll('p') ;
		}}
        var index_{0} = 0;
        audio_lines_{0}.each( function() {{
            var cont = true;
            if ( ! $(this).hasClass('{0}_line') ) {{
                anchor = $(this).find('a[id^=page_]').first();
                if ( ! anchor || anchor.length == 0 ) cont = false ;
            }}
            if ( cont ) {{
			  if ( tracking_points_{0}[index_{0}] >= 0 ) {{
                audio_segments_{0}.push( {{ element: $(this), time: tracking_points_{0}[index_{0}] }} ) ;
              }}  
              index_{0} ++;
              if ( index_{0} == num_segments_{0} ) {{
                audio_segments_{0}.push( {{ time: tracking_points_{0}[tracking_points_{0}.length-1] }} ) ;
                return false ;
              }}
            }}
        }});
        audio_element_{0}.ontimeupdate = function() {{
          if ( audio_element_{0}.paused || audio_element_{0}.ended ) return ;
          if ( playing_p_{0} ) playing_p_{0}.removeClass( 'audio_playing' ) ;
          playing_p_{0} = null ;
          for ( var index = 0 ; index < audio_segments_{0}.length-1 ; index++) {{
            if ( audio_element_{0}.currentTime >= audio_segments_{0}[index].time && audio_element_{0}.currentTime < audio_segments_{0}[index+1].time ) {{
              playing_p_{0} = audio_segments_{0}[index].element;
              playing_p_{0}.addClass( 'audio_playing' ) ;
            }}
          }}
        }};
        audio_element_{0}.onpause = audio_element_{0}.onended = function() {{
          if ( playing_p_{0} ) playing_p_{0}.removeClass( 'audio_playing' ) ;
          playing_p_{0} = null;
        }}
        var audio_{0}_collected_times = [] ;
        $(document).click(function(ev) {{
            if (! playing_p_{0} ) return ;
            if ( ev.altKey ) {{
				if ( ev.ctrlKey ) {{
					audio_{0}_collected_times = [] ;
				}}
				else {{
	                audio_{0}_collected_times.push( audio_element_{0}.currentTime ) ;
				}}
                console.log( '"audio_{0}": ' + JSON.stringify( audio_{0}_collected_times) ) ;
            }}
        }});
    }});""".format( id, Data[id] )
    return script

# ------------------------------------------------

# In a right-to-left language, we want to float things right
def float_left_or_right(Params):
    if Params.text_direction == 'rtl':
        return 'right'
    else:
        return 'left'

def aux_frame_div(Params):
    return f'<div id="aux_frame_div" style="display:none" class="split aux_frame"><iframe id="aux_frame" name="aux_frame" frameborder="0" width="100%" height="100%"></iframe></div>'

# In a right-to-left language, we have the main text on the right and the word pages on the left.
def div_split_main_text_tag(FirstMainFile, Params):
    MainFile = '_MAIN_FILE_PLACEHOLDER_' if Params.for_reading_portal == 'yes' else FirstMainFile
    #MainFile = '_MAIN_FILE_PLACEHOLDER_' if Params.for_reading_portal == 'yes_but_commented_out_for_now' else FirstMainFile
    return f'<div class="split main_frame"><iframe id="main_frame" src="{MainFile}" id="main_frame" name="main_frame" frameborder="0" width="100%" height="100%"></iframe></div>'

def iframe_main_text_tag(FirstMainFile, Params):
    MainFile = '_MAIN_FILE_PLACEHOLDER_' if Params.for_reading_portal == 'yes' else FirstMainFile
    return f'<iframe id="main_frame" src="{MainFile}" id="main_frame" name="main_frame" frameborder="0" width="100%" height="100%"></iframe>'

def div_iframe_aux_frame_tag(Params):
    return f'<div id="aux_frame_div" class="split aux_frame"><iframe id="aux_frame" name="aux_frame" frameborder="0" width="100%" height="100%"></iframe></div>'

def hyperlinked_text_title(Params):
    if Params.title != '':
        return Params.title # Custom Title from config
    return f'LARA &ndash; {Params.id}' # Default Title "LARA - ID"

def link_to_jquery(Params):
    jQuerySource = Params.jquery_downloaded_from
    if not jQuerySource in lara_config._jquery_source_values:
        lara_utils.print_and_flush(f'*** Error: unknown value "{jQuerySource}" for Params.jquery_downloaded_from. Permitted values: {lara_config._jquery_source_values}')
        return ''
    if jQuerySource == 'google':
        return '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>'
    elif jQuerySource == 'cloudflare':
        return '<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>'
    # Shouldn't get here
    else:
        lara_utils.print_and_flush(f'*** Error: unknown value "{jQuerySource}" for Params.jquery_downloaded_from. Permitted values: {lara_config._jquery_source_values}')
        return ''

def link_to_css_files(Params):
    cssFiles = '<link rel="stylesheet" type="text/css" href="_styles_.css" media="screen" />'
    if Params.css_file != '':
        cssFiles = cssFiles + '<link rel="stylesheet" type="text/css" href="_custom_styles_.css" media="screen" />'
    if Params.css_file_for_page != '':
        cssFiles = cssFiles + f'<link rel="stylesheet" type="text/css" href="{css_file_for_page(Params)}" media="screen" />'
    return cssFiles

def link_to_script_files(Params):
    scriptFiles = '<script src="_script_.js"></script>'
    if Params.script_file != '':
        scriptFiles = scriptFiles + '<script src="_custom_script_.js"></script>'
    if Params.script_file_for_page != '':
        scriptFiles = scriptFiles + f'<script src="{script_file_for_page(Params)}"></script>'
    return scriptFiles

def css_file_for_page(Params):
    if Params.css_file_for_page != '':
        OrigCSSFile = Params.css_file_for_page
        ( BaseFile, Extension ) = lara_utils.file_to_base_file_and_extension(OrigCSSFile)
        ShortName = BaseFile.split('/')[-1]
        return f'_custom_styles_{ShortName}_.css'
    else:
        return False

def script_file_for_page(Params):
    if Params.script_file_for_page != '':
        return Params.script_file_for_page
    else:
        return False

# ------------------------------------------------

def segment_translation_lines_header(Params):
    return word_page_lines_header('', Params)

def segment_translation_lines_closing(Params):
    return ['</div>',
            '</body>']

# HTML for the word pages

def word_page_lines_header(Word, Params):
    if Params.html_style != 'social_network':
        return word_page_lines_header_standalone(Word, Params)
    else:
        return word_page_lines_header_social_network(Word, Params)

def word_page_lines_header_standalone(Word, Params):
    return [f'{html_tag_for_vocab_pages(Params)}',  
	    '<head>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
	    link_to_css_files(Params),
	    '<script language="javascript" type="text/javascript">',
            playsound_scriptfunction(Params),
            playsound_part_scriptfunction(Params),
	    '</script>',
	    '</head>',
	    '<body>',
        '<div class="text_content word_page">'
	    '',
	    f'{word_page_header_for_word(Word, Params)}']

def word_page_lines_header_social_network(Word, Params):
    return []

def word_page_lines_closing(CountFile, AlphabeticalFile, NotesFile, Params):
    if Params.html_style != 'social_network':
        return word_page_lines_closing_standalone(CountFile, AlphabeticalFile, NotesFile, Params)
    else:
        return word_page_lines_closing_social_network(CountFile, AlphabeticalFile, NotesFile, Params)

def word_page_lines_closing_standalone(CountFile, AlphabeticalFile, NotesFile, Params):
    if Params.frequency_lists_in_main_text_page == 'yes':
        ScreenName = lara_utils.split_screen_pane_name_for_main_text_screen(Params)
    else:
        ScreenName = lara_utils.split_screen_pane_name_for_word_page_screen(Params)
    if NotesFile == False or not lara_translations.notes_are_defined():
        NotesLine = ''
    else:
        NotesLine = f'<p><a href="{NotesFile}" target="{ScreenName}"><i><u>{lara_config.get_ui_text("notes", Params)}</u></i></a></p>'
    if Params.frequency_lists_hidden == 'no':
        CountFileLine = f'<p><a href="{CountFile}" target="{ScreenName}"><i><u>{lara_config.get_ui_text("frequency_index", Params)}</u></i></a></p>'
        AlphabeticalFileLine = f'<p><a href="{AlphabeticalFile}" target="{ScreenName}"><i><u>{lara_config.get_ui_text("alphabetical_index", Params)}</u></i></a></p>'
    else:
        CountFileLine = ''
        AlphabeticalFileLine = ''
    return [NotesLine,
            CountFileLine,
            AlphabeticalFileLine,
            #'<span id="audio_container" style="visibility: hidden;"></span>',
            '<div id="audio_container" style="width:0;height:0;overflow:hidden"></div>',
            '</div>',
            '</body>']

def word_page_lines_closing_social_network(CountFile, AlphabeticalFile, NotesFile, Params):
    RelDir = Params.relative_compiled_directory
    if Params.frequency_lists_in_main_text_page == 'yes':
        LoadFunction = 'load_main_text'
    else:
        LoadFunction = 'load_word_concordance'
    if lara_translations.notes_are_defined():
        #<span onclick="load_word_concordance('Hanii_Hello_world_editedvocabpages/word_hello.html');">
        NotesLine = f'<p><span onclick="{LoadFunction}(\'{RelDir}/{NotesFile}\');">{lara_config.get_ui_text("notes", Params)}</u></i></span></p>'
    else:
        NotesLine = ''
    return [NotesLine,
            #f'<p><a href="{CountFile}" target="{ScreenName}"><i><u>{lara_config.get_ui_text("frequency_index", Params)}</u></i></a></p>',
            f'<p><span onclick="{LoadFunction}(\'{RelDir}/{CountFile}\');">{lara_config.get_ui_text("frequency_index", Params)}</u></i></span></p>',
            #f'<p><a href="{AlphabeticalFile}" target="{ScreenName}"><i><u>{lara_config.get_ui_text("alphabetical_index", Params)}</u></i></a></p>',
            f'<p><span onclick="{LoadFunction}(\'{RelDir}/{AlphabeticalFile}\');">{lara_config.get_ui_text("alphabetical_index", Params)}</u></i></span></p>'
            ]

def word_page_header_for_word(Word0, Params):
    if Word0 == '':
        return ''
    Word = lara_replace_chars.restore_reserved_chars(Word0)
    Parts = Word.split('/')
    PosSpan = ''
    if len(Parts) > 1 and Parts[1] != '':
        PosText = lara_postags.translate_postag(Parts[1], Params)
        if PosText != '':
            PosSpan = f'<br/><span class="pos_tag">({PosText})</span>'
    return f'<h1>{Parts[0]}{PosSpan}</h1>'


# Note: this only applies to _main_text*.html, not to _hyperlinked_text or word_*.html
def default_script( Params ): 
    return init_scriptfunction(Params) + \
            playsound_scriptfunction(Params) + \
            playsound_part_scriptfunction(Params) + \
	    toggle_translation_scriptfunction(Params) + \
	    bookmark_scriptfunction(Params)

# I removed the following element from default_styles, since it messes up
# the formatting on prose texts like 'Alice' and 'Peter Rabbit' by introducing
# linebreaks after anchors.
# - Manny, 20190623
#
#        a[id] {{
#            display: block;
#            position: relative;
#            top: {-toolbarHeight - 32}px;
#            visibility: hidden;
#        }}
        
# Note: applies to ALL pages
def default_styles( Params ):
	toolbarHeight = 56    
	return f"""
        .disabled {{
            color: #AAA
        }}
        .hashhighlight {{
            background: #FFE0FF;
        }}
        .hidden {{
            display: none;
        }}
        .seg_trans {{
            background: #E0FFE0;
            margin-top: -1em;
            padding-top: 0;
        }}
        a {{
            text-decoration: none;
        }}
        a:link, a:visited {{
            color: black;
        }}
        a.bookmarklink {{
            display:none;
            cursor:pointer;
            color: #AAA;
            font-weight:bold;
            height: 20px;
            width: 20px;
            background-image: url(data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAACXBIWXMAAA7EAAAOxAGVKw4bAAACIElEQVQ4y82U32tSYRjHv+/xaEwy7RclbjEhitWJCIPNLqTA3QRdxDiDEe0vCNqOdRXRVRCEWhF0YUSjXelFN9IWbVCL1IUyJgoWkZGDWBd2dKMDvsfzdDOXDKkjjOiBBx4eXj487/t9vi8jImxniNjm+DdAIpJbNWMs0RWRiNqzT2/U4/mpeZqamKXp+8tUbeiRLWf+mKxdlCb/EX9/NyUXCwKcQzug5TQ0vG6M3DgZ3W21KF1NaBhN5dOzFxQbn6WZpVqFc+6vF1OV6fEkxW7lqMabipkJNwtdV+NvbyYp9rhEnHM/EYFzrtSzb+jJWJJmljmZAW6KIgiOhPuIIJdefcGczx0PStX0wkRR/u7t6UqTzm/4QUTvFQkHl/LIvjaAPftwLiyt7K+tKyq3weN2wSJ0Vp9tdcpvYTYaDgFYM2BxAM21jZ7kwcj1Ex2FYp2sR4Yuq99W5VXNikN9P+VMqIjPVcAW6EfAp2LhoYrG0c5Q9jcv6/l39PROHU6fiFp5F4L3fKG9hcXJ51G1F8MDuHzJO9q+/KatZz87iItX7VFRFCO6NJg4HXj5NfVRxToRHIyZ9zIbOBY6LqXCxQdpzE365aBkj2qFxXB2HrCdd2FnG8zUlVtCpW+n5FJZhNNnhZbR0JA8uHBNWjlgE88AqHQFbEFzj7JyqWyg51Q/hscOZ1xWy2g7rCsgABiGoRDREGMsIwhCxNQe/ncf7C/NzHVp+0tYVAAAAABJRU5ErkJggg==);
            background-repeat: no-repeat;
            background-position: center center;
        }}
    	body {{ 
	    	padding:0; 
		    margin: 0; 
    		color: black; 
	    	background: white; 
		    font-family: {Params.font};
		    font-size: {Params.font_size}; 
            overflow-y: scroll;
            overflow-x: hidden;
	    }}
	th, td {{  
		    font-family: {Params.font};
		    font-size: {Params.font_size}; 
	    }}
        body.noscroll {{ 
            overflow: hidden;
        }}
        button {{
            cursor: pointer;
            font-family: sans-serif;
        }}
        div.split {{ 
            padding:0; 
            margin: 0; 
            overflow-x: hidden; 
        }}
        @media (orientation:landscape) {{
            div.split {{ 
                height: 100%; 
                width: 50%; 
                float: {float_left_or_right(Params)};
            }}
        }}
        @media (orientation:portrait) {{
            div.split {{ 
                border-top: 1px solid #AAA;
                width: 100%; 
                height: 50%; 
            }}
        }}
        div.text_content {{
            padding: 1em;
        }}
        div#toolbar {{
            position: fixed;
            top:0; /* needed for FF */
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            height: {toolbarHeight}px;
            width: 100%;
            overflow-y: auto;
            background: #F8F8F8;
        }}
        div#aftertoolbar {{
            height: {toolbarHeight}px;
        }}
        div#toolbar > div {{
            padding-left: .5em;
            padding-right: .5em;
        }}
        div#toolbar button {{
            font-size: 11pt;
            border: none;
            border-radius: .5em;
            padding: .5em;
            background: none;
        }}
        div#toolbar button:hover {{
            background: #E8E8E8;
        }}
        h1.toc {{
            text-align: left;
        }}
        h2.toc {{
            text-align: left;
            margin-left: 2em;
        }}
        iframe {{
            padding: 0;
            margin: 0;
            overflow-y: scroll;
        }}
        p {{
            word-wrap: break-word;
            white-space: pre-wrap;
        }}
        .audio_playing {{
            font-weight: bold;
            background: #FFFFA0;
        }}
        span.red  {{
            color: #ff0033;
        }}
        span.light_red {{
            color: #ff6666;
        }}
        span.pink {{
            color: #FFC0CB;
        }}
        span.green {{
            color: #00cc44;
        }}
        span.light_green {{
            color: #90EE90;
        }}
        span.blue {{
            color: #0000FF;
        }}
        span.light_blue {{
            color: #ADD8E6;
        }}
        span.burgundy {{
            color: #800020;
        }}
        span.yellow {{
            color: #FFFF00;
        }}
        span.orange {{
            color: #FFA500;
        }}
        span.purple {{
            color: #800080;
        }}
        span.violet {{
            color: #EE82EE;
        }}
        span.gray {{
            color: #808080;
        }}
        span.brown {{
            color: #A52A2A;
        }}
        span.black {{
            color: #000000;
        }}
        span.sound {{
            cursor: pointer;
        }}
        span.pos_tag {{
            font-size: 50%;
            color: #AAA;
            font-weight: normal;
        }}
        table.indexpage {{
            border-collapse: collapse;
        }}
        table.indexpage td {{
            padding: .3em;
        }}
        table.indexpage tr:nth-child(1) {{
            font-weight: bold;
        }}
        table.indexpage tr:nth-child(even) {{
            background: #EEE;
        }}
        """ 
		
# --------------------------------------------------------

def print_lara_html_table(Caption, Header, List, File, Params):
    List1 = [ Header ] + List 
    write_out_html_table(Caption, List1, File, Params)

def write_out_html_table(Caption, Lines, File, Params):
    HTMLLines = table_lines_to_html_lines(Caption, Lines, Params)
    lara_utils.write_unicode_text_file('\n'.join(HTMLLines), File)
    lara_utils.print_and_flush(f'--- Written file ({len(Lines)} lines) to {File}')

def table_lines_to_html_lines(Caption, Lines, Params):
    Intro = table_lines_intro(Caption, Params)
    Body = table_lines_to_html_lines1(Lines)
    Closing = table_lines_closing()
    return Intro + Body + Closing

def table_lines_intro(Caption, Params):
    return [f'{html_tag_for_vocab_pages(Params)}',  
	    '<head>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
	    '<style type="text/css">',
	    '   a {text-decoration:none;}',
	    '   a:link, a:visited {color: black;}',
	    '</style>',
            #'<link rel="stylesheet" type="text/css" href="_styles_.css" media="screen" />',
            #'' if not Params.css_file else '<link rel="stylesheet" type="text/css" href="_custom_styles_.css" media="screen" />',
            link_to_css_files(Params),
	    '</head>',
	    '<body>',
        '<div class="text_content index_page">',
        f'<h2>{Caption}</h2>', 
	    '<table class="indexpage">']

def toc_lines_intro(Caption, Params):
    return [f'{html_tag_for_vocab_pages(Params)}',  
	    '<head>',
	    '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">',
	    '<style type="text/css">',
	    '   a {text-decoration:none;}',
	    '   a:link, a:visited {color: black;}',
	    '</style>',
            #'<link rel="stylesheet" type="text/css" href="_styles_.css" media="screen" />',
            #'' if not Params.css_file else '<link rel="stylesheet" type="text/css" href="_custom_styles_.css" media="screen" />',
            link_to_css_files(Params),
	    '</head>',
	    '<body>',
        '<div class="text_content toc_page">',
        f'<h2>{Caption}</h2>', 
        ]


def table_lines_to_html_lines1(TableLines):
    ListsOfLines = [ table_line_to_html_lines(TableLine) for TableLine in TableLines ]
    return [ HTMLLine for HTMLLines in ListsOfLines for HTMLLine in HTMLLines ]

def table_line_to_html_lines(TableLine):
    Opening = line_opening()
    Body = [ table_line_item_to_html_line(Item) for Item in TableLine ]
    Closing = line_closing()
    return Opening + Body + Closing

def line_opening():
    return ['<tr>']

def table_line_item_to_html_line(Element):
    return f'<td>{Element}</td>'

def line_closing():
    return ['</tr>']

def table_lines_closing():
    return ['</div>',
        '</table>',
	    '</body>',
	    '</html>']

def toc_lines_closing():
    return ['</div>',
	    '</body>',
	    '</html>']

def html_tag_for_vocab_pages(Params):
    if Params.text_direction == 'rtl':
        return '<html dir="rtl">'
    else:
        return '<html>'
  
