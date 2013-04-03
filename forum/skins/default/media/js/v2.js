// jQuery enclosure
// any global variables should be declared avobe this comment, not that we should be using global variables...
$(function(){
    



/*** 
 * trigger animations when the like button is clicked
 */

// trigger animations when the like question button is clicked
$(".like-question-button").click(function(e){
    e.preventDefault();

    // disable the button prevent multiple likes
    $(this).addClass('disabled');                 

    $widget = $(this).closest('.like-widget');
    $follow = $widget.find('.follow-question');

    // are we liking or unliking
    var liking = ($widget.hasClass('on'))? true : false;
    var $likes = $widget.find('h3');

    // like ajax request
    $.getJSON($(this).attr('href'), function(data, e) {

        // re-enable the button
        $(this).removeClass('disabled');

        // respond to error
        if (!data.success && data['error_message'] != undefined) {
            console.log(data.error_message);
            return;
        } 
        
        // increase/decrease likes count
        if (liking) {
            $likes.text(parseInt($likes.text())+1);
        } else {
            $likes.text(parseInt($likes.text())-1);
        }

        // show/hide the follow button if exists in this context
        if ($follow.length) {
            if (liking) {
                $('.follow-question').animate({'opacity': 1});
            } else {
                $('.follow-question').animate({'opacity': .2});
            }            
        }

    });
});


// legacy from question page - should be rewritten to not be so obtuse
// commented out for now to prevent conflicts with templates that may have the same function
// hard-coded into their template
/*
function submitClicked(e, f) {
    window.removeEventListener('beforeunload', beforeUnload, true);
    if (f) {
        f.submit();
    }
}

function beforeUnload(e) {
    if($("textarea#editor")[0].value != "") {
        return yourWorkWillBeLost(e);
    }
    var commentBoxes = $("textarea.commentBox");
    for(var index = 0; index < commentBoxes.length; index++) {
        if(commentBoxes[index].value != "") {
            return yourWorkWillBeLost(e);
        }
    }
}
window.addEventListener('beforeunload', beforeUnload, true);
*/




}); // end jquery enclosure