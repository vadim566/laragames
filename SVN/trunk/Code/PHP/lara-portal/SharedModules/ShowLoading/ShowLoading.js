
function showLoading(DivID)  {

    var indicatorID;
    var settings = {
        'addClass': '',
        'beforeShow': '',
        'afterShow': '',
        'hPos': 'center',
        'vPos': 'center',
        'indicatorZIndex' : 5001,
        'overlayZIndex': 5000,
        'parent': '',
        'marginTop': 0,
        'marginLeft': 0,
        'overlayWidth': null,
        'overlayHeight': null
    };

    var loadingDiv = $('<div style="text-align:center"></div>');
    var overlayDiv = $('<div></div>');

    // Set up ID and classes
    if ( settings.indicatorID ) {
        indicatorID = settings.indicatorID;
    }
    else {
        indicatorID = $(DivID).attr('id');
    }

    $(loadingDiv).attr('id', 'loading-indicator-' + indicatorID );
    $(loadingDiv).addClass('loading-indicator');

    if ( settings.addClass ){
        $(loadingDiv).addClass(settings.addClass);
    }

    // Create the overlay
    $(overlayDiv).css('display', 'none');

    // Append to body, otherwise position() doesn't work on Webkit-based browsers
    $(document.body).append(overlayDiv);

    // Set overlay classes
    $(overlayDiv).attr('id', 'loading-indicator-' + indicatorID + '-overlay');
    $(overlayDiv).addClass('loading-indicator-overlay');

    if ( settings.addClass ){
        $(overlayDiv).addClass(settings.addClass + '-overlay');
    }

    // Set overlay position
    var overlay_width;
    var overlay_height;
    var border_top_width = $(DivID).css('border-top-width');
    var border_left_width = $(DivID).css('border-left-width');

    // IE will return values like 'medium' as the default border,
    border_top_width = isNaN(parseInt(border_top_width)) ? 0 : border_top_width;
    border_left_width = isNaN(parseInt(border_left_width)) ? 0 : border_left_width;

    var overlay_left_pos = $(DivID).offset().left + parseInt(border_left_width);
    var overlay_top_pos = $(DivID).offset().top + parseInt(border_top_width);

    if ( settings.overlayWidth !== null ) {
        overlay_width = settings.overlayWidth;
    }
    else {
        overlay_width = parseInt($(DivID).width()) + parseInt($(DivID).css('padding-right')) + parseInt($(DivID).css('padding-left'));
    }

    if ( settings.overlayHeight !== null ) {
        overlay_height = settings.overlayWidth;
    }
    else {
        overlay_height = parseInt($(DivID).height()) + parseInt($(DivID).css('padding-top')) + parseInt($(DivID).css('padding-bottom'));
    }

    $(overlayDiv).css('width', overlay_width.toString() + 'px');
    $(overlayDiv).css('height', overlay_height.toString() + 'px');
    $(overlayDiv).css('left', overlay_left_pos.toString() + 'px');
    $(overlayDiv).css('position', 'absolute');
    $(overlayDiv).css('top', overlay_top_pos.toString() + 'px' );
    $(overlayDiv).css('z-index', settings.overlayZIndex);

    // Set any custom overlay CSS
    if ( settings.overlayCSS ) {
        $(overlayDiv).css ( settings.overlayCSS );
    }


    // We have to append the element to the body first
    // or .width() won't work in Webkit-based browsers (e.g. Chrome, Safari)
    $(loadingDiv).css('display', 'none');
    $(document.body).append(loadingDiv);
    $(loadingDiv).css('position', 'absolute');
    $(loadingDiv).css('z-index', settings.indicatorZIndex);

    // Set top margin
    var indicatorTop = overlay_top_pos;
    if ( settings.marginTop ) {
        indicatorTop += parseInt(settings.marginTop);
    }

    var indicatorLeft = overlay_left_pos;
    if ( settings.marginLeft ) {
        indicatorLeft += parseInt(settings.marginTop);
    }


    // set horizontal position
    if ( settings.hPos.toString().toLowerCase() == 'center' ) {
        $(loadingDiv).css('left', (indicatorLeft + (($(overlayDiv).width() - parseInt($(loadingDiv).width())) / 2)).toString()  + 'px');
    }
    else if ( settings.hPos.toString().toLowerCase() == 'left' ) {
        $(loadingDiv).css('left', (indicatorLeft + parseInt($(overlayDiv).css('margin-left'))).toString() + 'px');
    }
    else if ( settings.hPos.toString().toLowerCase() == 'right' ) {
        $(loadingDiv).css('left', (indicatorLeft + ($(overlayDiv).width() - parseInt($(loadingDiv).width()))).toString()  + 'px');
    }
    else {
        $(loadingDiv).css('left', (indicatorLeft + parseInt(settings.hPos)).toString() + 'px');
    }

    // set vertical position
    if ( settings.vPos.toString().toLowerCase() == 'center' ) {
        $(loadingDiv).css('top', (indicatorTop + (($(overlayDiv).height() - parseInt($(loadingDiv).height())) / 2)).toString()  + 'px');
    }
    else if ( settings.vPos.toString().toLowerCase() == 'top' ) {
        $(loadingDiv).css('top', indicatorTop.toString() + 'px');
    }
    else if ( settings.vPos.toString().toLowerCase() == 'bottom' ) {
        $(loadingDiv).css('top', (indicatorTop + ($(overlayDiv).height() - parseInt($(loadingDiv).height()))).toString()  + 'px');
    }
    else {
        $(loadingDiv).css('top', (indicatorTop + parseInt(settings.vPos)).toString() + 'px' );
    }

    // Set any custom css for loading indicator
    if ( settings.css ) {
        $(loadingDiv).css ( settings.css );
    }


    // Set up callback options
    var callback_options =
        {
            'overlay': overlayDiv,
            'indicator': loadingDiv,
            'element': DivID
        };

    // beforeShow callback
    if ( typeof(settings.beforeShow) == 'function' ) {
        settings.beforeShow( callback_options );
    }

    // Show the overlay
    $(overlayDiv).show();

    // Show the loading indicator
    $(loadingDiv).show();

    // afterShow callback
    if ( typeof(settings.afterShow) == 'function' ) {
        settings.afterShow( callback_options );
    }

    return DivID;
};


function hideLoading (DivID) {
    var settings = {};

    if ( settings.indicatorID ) {
        indicatorID = settings.indicatorID;
    }
    else {
        indicatorID = $(DivID).attr('id');
    }

    $(document.body).find('#loading-indicator-' + indicatorID ).remove();
    $(document.body).find('#loading-indicator-' + indicatorID + '-overlay' ).remove();

    return DivID;
};
