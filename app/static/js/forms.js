var submitText = $('input[name=submit]').val();
var formGroup = $('.form-group');

$(function() {
    $(document).on('click', function (e) {
        var isFullScreen = false;
        if ($(window).width() > 767) isFullScreen = true;

        displayEntryFields(e, isFullScreen)
    });
});

function displayEntryFields(e,isFullScreen) {
    var submitButton = $('input[name=submit]');
    var animationTime = 500;
    var numFields = $('.form > .form-group').length + 1;
    var fieldWidth = (100/numFields).toString() + '%';

    if (isFullScreen) {
        if (e.target.id === 'submit') {
            if ($('.form-group').width() > 0) return;
            formGroup.animate({width:fieldWidth},animationTime,'swing')
        }

    } else {
        if (e.target.id === 'submit' || $(e.target).hasClass('form-control')) {
            // submitButton.val('+');
            formGroup.slideDown()
        } else {
            formGroup.slideUp();
            // submitButton.val(submitText);
        }
    }

}


// || $(e.target).hasClass('form-control')
            // submitButton.val('+');
            // if ($(e.target).hasClass('form-control')) {
            //     return
            // }

 // } else {
        //     formGroup.animate({width:'0'},animationTime,'swing');
        //     // submitButton.val(submitText);
        // }