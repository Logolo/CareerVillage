// jQuery enclosure
// any global variables should be declared avobe this comment, not that we should be using global variables...
$(function(){
    

/****
 * Custom radio elements
 * toggle hidden radio buttons by clicking on other elements
 * 1. add "radio-el" class to an element that you want to toggle a radio button
 * 2. add "custom-radio-elements" class to an ancestor
 * 3. add "rel='whatever'" if the id of the hidden input field is "whatever"
 */

$(".custom-radio-elements .radio-el").click(function(e){

    id = $(this).attr('rel');
    if (!id) return false;

    $el = $("#"+ id);
    if (!$el.length) return false;    

    // set the input field associated with this element
    val = $(this).data('value');
    $el.val(val);

    // set the clicked element's class to active
    $(this).closest('.custom-radio-elements').find('.radio-el').removeClass('active');
    $(this).addClass('active');
    
    // add some animation to the save button
    if ($submit = $el.closest('form').find('input[type=submit]')) {
        $submit.removeClass('animated wobble');
        $submit.addClass('animated wobble');
    }
    
    
});


/*** 
 * trigger modal dialog to open on page load if it has the class "init"
 */ 
 $('.modal.init').modal('show'); 


 /*** 
  * give popovers a data attribute to close themselves at the click of a button
  */
 $('body').on('click', '.popover [data-dismiss=popover]', function(e){
   $(this).closest('.popover').hide();
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

/* user type selector for login/register page */
$('.user-type-selection a[data-toggle=tab]').click(function(e){
  $('body').animate({scrollTop: $(this).offset().top - 10}, 300);
});

/* avatar selector for student registration */
$("#signup-student").find(".modal li.avatar-preview").click(function(){
    $("li.avatar-preview").removeClass('selected');
    $(this).addClass('selected');
});


$("#signup-signin").find('ul.nav li').click(function(e){
    e.stopPropagation();

    $('ul.nav li').removeClass('active');
    $(this).addClass('active');

    var $signinTab = $('.signin-tab'),
        $signupTab = $('.signup-tab');
    if ($signinTab.is(':visible')) {
        $signinTab.hide();
        $signupTab.show();
    } else {
        $signinTab.show();
        $signupTab.hide();
    }

    return false
});

$("#signup-student").find(".modal li.avatar-preview").click(function(){
    $("li.avatar-preview").removeClass('selected');
    $(this).addClass('selected');
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