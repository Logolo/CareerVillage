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
// enable popovers on any element with class has-popover
$(".has-popover").popover(); 
 $('body').on('click', '.popover [data-dismiss=popover]', function(e){
   $(this).closest('.popover').hide();
 });
 

/*** 
 * trigger ajax and animations when the like button and follow buttons are clicked
 */

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
    
    // is this your first or second time liking
    // TODO connect this to backend somehow
    var first_like = false;
    var second_like = false;

    // like ajax request
    $.getJSON($this.attr('href'), function(data, e) {

        // re-enable the button
        $this.removeClass('disabled');

        // respond to error
        if (!data.success && data['error_message'] != undefined) {
            console.log(data.error_message);
            //return;
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

        // for first time likers, suggest they share on facebook
        if (liking && first_like) {
          
          message =  "We can automatically share your likes on Facebook so your friends benefit too. How about it?</p> \
                      <button class='btn-success btn'>Yes, share on Facebook</button><br /> \
                      <button style='margin-top:4px' class='btn btn-mini' data-dismiss='popover'>No thanks</button><br /> \
                      ";
          $widget.popover({
            'placement': 'right',
            'trigger': 'manual',
            'title': '<h5 style="margin:0">Thanks for liking this question!</h5>',
            'html': true,
            'content': message
          }).popover('show');          

        }
        
        // for second time likers, suggest they follow this question
        if (liking && second_like) {
          message =  "Get an email when there's new content for this question. Just click the follow button!</p> \
                      <button style='margin-top:4px' class='btn' data-dismiss='popover'>Ok</button> \
                      ";
          $follow.popover({
            'placement': 'right',
            'trigger': 'manual',
            'title': '<h5 style="margin:0">Thanks for liking another question!</h5>',
            'html': true,
            'content': message
          }).popover('show');
        }

        // show/hide the follow button if exists in this context
        if ($follow.length) {
            if (liking) {
                $follow.animate({'opacity': 1});
            } else {
                $follow.animate({'opacity': .2});
            }            
        }

    });
});

$(".follow-question-button").click(function(e){
    e.preventDefault();
    $this = $(this);

    // disable the button prevent multiple follows
    $this.addClass('disabled');

    $widget = $this.closest('.like-widget');
    $followButtons = $('.follow-question-button');

    // are we following or unfollowing
    var following = ($this.hasClass('on'))? false : true;

    // follow ajax request
    // TODO: connect this to the backend
    //$.getJSON($this.attr('href'), function(data, e) {

    // re-enable the button
    $this.removeClass('disabled');

    // respond to error
    /* TODO: error handling when connected to backend
    if (!data.success && data['error_message'] != undefined) {
        console.log(data.error_message);
        return;
    }*/
    
    // update button text
    if (following) {
        $followButtons.find('.text').text('following');
        $followButtons.addClass('on');
        $followButtons.find('.icon-star').hide();
    } else {
        $followButtons.find('.text').text(' follow');
        $followButtons.removeClass('on');
        $followButtons.find('.icon-star').show();
    }

  //});
  
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

/* preview avatar selection for student registration*/
$("#signup-student").find(".modal li.avatar-preview").click(function(){
    $("li.avatar-preview").removeClass('selected');
    $(this).addClass('selected');
});

/* flag for review toggle */
$('.flag-for-review').click(function(e){
    e.preventDefault();
    $form = $("#flag-question-form");

    if ($form.is(':visible')) {
        $form.slideUp();
    } else {
        $form.slideDown();
    }
});

    }

    }




}); // end jquery enclosure