
var url_path = window.location.pathname.split('/'); // url of the current page as an array
var exercise = url_path[url_path.length - 1]; // get the very last bit of the URL
var clicks = 0; // varialbe for storing clicks, used for deleting progressions
var del_button = $('.delete-button'); // get the delete button handler
var progression = $('.progression'); // get the progression handler

var holdStarter = null;
var holdDelay = 600;
var holdActive = false;

$(document).ready(function(){

   $('.notSelectable').disableSelection();

});

$.fn.extend({
    disableSelection: function() {
        this.each(function() {
            this.onselectstart = function() {
                return false;
            };
            this.unselectable = "on";
            $(this).css('-moz-user-select', 'none');
            $(this).css('-webkit-user-select', 'none');
        });
    }
});

var onlongtouch;
var timer;
var touchduration = 500; //length of time we want the user to touch before we do something

function touchstart() {
    timer = setTimeout(onlongtouch, touchduration);
}

function touchend() {
    //stops short touches from firing the event
    if (timer)
        clearTimeout(timer); // clearTimeout, not cleartimeout..
}

onlongtouch = function() { alert('touch')};

del_button.click(function() {
    if (clicks == 0) {
        $(this).addClass('delete-button-clicked-once');
        $(this).text('Confirm?');
        clicks++;
    } else {
        var toDelete = [];
        $('.progression-to-delete').each(function () {
            toDelete.push($(this).attr('id'));
        });
        if (toDelete.length == 0) {
            $.ajax({
            url: '/delete_exercise',
            data: {exercise_name: exercise},
            type: 'GET',
            success: function (response) {
                window.location.replace(response)
            }
            });
        } else {
            $.ajax({
            url: '/delete_progression',
            data: {toDelete_ids: toDelete, exercise: exercise},
            type: 'GET',
            success: function (response) {
                window.location.replace(window.location.pathname)
            }
            });
        }

    }
});

del_button.mouseleave(function () {
    $(this).text('Delete');
    clicks = 0;
    $(this).removeClass('delete-button-clicked-once')
});

// MouseDown

$('.delete-tag').click(function () {
    handler = $(this);
    id = handler.attr('id').split('-');
    id = id[id.length - 1];
    targetProgression = $('#progression-' + id.toString());
    targetProgression.toggleClass('progression-to-delete');
    handler.toggleClass('delete-tag-clicked');
});

progression.click(function () {
    handler = $(this);
    handler.toggleClass('progression-completed');
    id = handler.attr('id')

    $.ajax({
            url: '/complete_progression',
            data: {progression_id : id},
            type: 'GET',
            success: function (response) {
                // window.location.replace(response)
                console.log(response);
            },
            error: function (error) {
                console.log(error);
            }
    });
});


// progression.mousedown(function (){
//     handler = $(this);
//     holdStarter = setTimeout(function() {
//         holdStarter = null;
//         holdActive = true;
//     }, holdDelay);
// });

// MouseUp
// progression.mouseup(function () {
//     // If the mouse is released immediately (i.e., a click), before the
//     //  holdStarter runs, then cancel the holdStarter and do the click
//     if (holdStarter) {
//         clearTimeout(holdStarter);
//         id = $(this).attr('id')
//         $(this).toggleClass('progression-completed');
//         $.ajax({
//             url: '/complete_progression',
//             data: {progression_id : id},
//             type: 'GET',
//             success: function (response) {
//                 // window.location.replace(response)
//                 console.log(response);
//             },
//             error: function (error) {
//                 console.log(error);
//             }
//         });
//     }
//     // Otherwise, if the mouse was being held, end the hold
//     else if (holdActive) {
//         holdActive = false;
//     }
// });

// var resizeTimer;
// $(window).resize(function() {
//     $(function(){
//         $("body a").each(function(){
//             $(this).attr("rel","external");
//         });
//     });
//
//     if ($(window).width() <= 800) {
//         $(function() {
//             $(".progression").on("taphold", function () {
//                 $(this).toggleClass('progression-to-delete')
//             });
//         });
//     }
// });