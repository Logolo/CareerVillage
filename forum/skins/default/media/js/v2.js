// jQuery enclosure
// any global variables should be declared avobe this comment, not that we should be using global variables...
$(function(){
    
    // trigger animations when the like question button is clicked
    $(".like-question-button").click(function(e){
        e.preventDefault();
                
        // like page
        // TODO wrap in ajax success function
        if (!$(this).hasClass('disabled')) {
            $(this).addClass('btn-primary disabled').removeClass('btn-success').text('Liked!');
            $num = $(this).closest('.like-widget').find('h3');
            $num.text(parseInt($num.text())+1);            
        }

        // reveal the follow question button
        $('.follow-question').animate({'opacity': '1'});


    });

});
