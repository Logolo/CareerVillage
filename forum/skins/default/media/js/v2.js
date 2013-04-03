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