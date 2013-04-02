// jQuery enclosure
// any global variables should be declared avobe this comment, not that we should be using global variables...
$(function(){
    
    // trigger animations when the like question button is clicked
    $(".like-question-button").click(function(e){
        e.preventDefault();
                
        // reveal the follow question button
        $('.follow-question').animate({'opacity': '1'});


    });

});
