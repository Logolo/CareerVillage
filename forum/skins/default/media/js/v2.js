// jQuery enclosure
// any global variables should be declared avobe this comment, not that we should be using global variables...
$(function(){
    

/****
 * Custom radio elements
 * toggle hidden radio buttons by clicking on other elements
 * 1. add "radio-el" class to an element that you want to toggle a radio button
 * 2. add "custom-radio-elements" class to an ancestor
 * 3. add "rel='whatever'" if the id of the input field is "whatever", every input field needs a unique id so we know which one to check
 */

$(".custom-radio-elements .radio-el").click(function(e){
/*
    id = $(this).data('rel');
    if (!id) return false;

    $el = $("#"+ id);
    if (!$el.length) return false;

    // check the input field associated with this element
    $el.attr('checked', true);
*/
    // set the clicked element's class to active
    $(this).closest('.custom-radio-elements').find('.radio-el').removeClass('active');
    $(this).addClass('active');
        
});


/*** 
 * trigger animations when the like button is clicked
 */

// trigger animations when the like question button is clicked
$(".like-question-button").click(function(e){
    e.preventDefault();
    $this = $(this);

    // disable the button prevent multiple likes
    $this.addClass('disabled');                 

    $widget = $(this).closest('.like-widget');
    $follow = $widget.find('.follow-question');

    // are we liking or unliking
    var liking = ($widget.hasClass('on'))? false : true;
    var $likes = $widget.find('h3');

    // like ajax request
    $.getJSON($this.attr('href'), function(data, e) {

        // re-enable the button
        $this.removeClass('disabled');

        // respond to error
        if (!data.success && data['error_message'] != undefined) {
            console.log(data.error_message);
            return;
        }
        
        // update like button, count and widget status
        if (liking) {
            $this.text('Liked');
            $likes.text(parseInt($likes.text())+1);
            $widget.addClass('on');
        } else {
            $this.text('Like this');
            $likes.text(parseInt($likes.text())-1);
            $widget.removeClass('on');
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