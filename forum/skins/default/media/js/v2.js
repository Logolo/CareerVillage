// jQuery enclosure
// any global variables should be declared avobe this comment, not that we should be using global variables...
$(function(){


    /****
     * Extend Twitter Bootstrap with a Custom Radio Elements Selector
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
     * Init Twitter Bootstrap JS and Add Minor Extensions
     */

// trigger modal dialog to open on page load if it has the class "init"
    $('.modal.init').modal('show');

// enable popovers on any element with class has-popover
    $(".has-popover").popover();

// give popovers a data attribute to close themselves at the click of a button
    $('body').on('click', '.popover [data-dismiss=popover]', function(e){
        $(this).closest('.popover').hide();
    });


    /***
     * trigger ajax and animations when the like button and follow buttons are clicked
     */

    $(".like-question-button").click(function(e){
        e.preventDefault();
        var $this = $(this);

        // prevent multiple submissions
        if ($this.hasClass('loading')) return;
        $this.addClass('loading');

        var $widget = $(this).closest('.like-widget'),
            $follow = $widget.find('.follow-question');

        // are we liking or unliking
        var liking = ($widget.hasClass('on'))? false : true;
        var $likes = $widget.find('h3');

        // number of times this user has liked a question/answer before
        var like_count = $widget.data('like-count');

        // like ajax request
        $.getJSON($this.attr('href'), function(data, e) {

            // re-enable the button
            $this.removeClass('loading');

            // respond to error
            if (!data.success && data['error_message'] != undefined) {
                $widget.popover({
                    'placement': 'right',
                    'trigger': 'hover',
                    'title': '',
                    'html': true,
                    'content': data.error_message
                }).popover('show');
                return;
            }

            // update like button, count, data-likes-count and widget status
            if (liking) {
                $this.text('Liked').addClass('disabled');
                $likes.text(parseInt($likes.text())+1);
                $widget.addClass('on');
                $('[data-like-count]').data('like-count', like_count+1);
            } else {
                $widget.popover('hide');
                $this.text('Like this').removeClass('disabled');
                $likes.text(parseInt($likes.text())-1);
                $widget.removeClass('on');
                $('[data-like-count]').data('like-count', like_count-1);
            }

            // for first time likers, suggest they share on facebook
            if (liking && like_count == 0) {

                var shareBtn = $('<button>').addClass('btn-success btn').text('Yes, share on Facebook'),
                    dontShareBtn = $('<button>').addClass('btn btn-mini').css('margin-top', '4px').text('No thanks'),
                    message =  $('<p>')
                        .text("We can automatically share your likes on Facebook so your friends benefit too. How about it?")
                        .append(shareBtn)
                        .append($('<br>'))
                        .append(dontShareBtn);

                shareBtn.click(function(){
                    $.post($this.data('publish-url'), {
                        'publish': 'true'
                    }, function(){

                    });
                });
                dontShareBtn.click(function(){
                    $.post($this.data('publish-url'), {
                        'publish': 'false'
                    }, function(){
                        $widget.popover('hide');
                    });
                });


                $widget.popover({
                    'placement': 'right',
                    'trigger': 'manual',
                    'title': '<h5 style="margin:0">Thanks for liking this question!</h5>',
                    'html': true,
                    'content': message
                }).popover('show');

            }

            // for second time likers, suggest they follow this question
            if (liking && like_count == 1) {
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
            /*
             if ($follow.length) {
             if (liking) {
             $follow.animate({'opacity': 1});
             } else {
             $follow.animate({'opacity': 0});
             }
             }
             */

        });
    });

    $(".follow-question-button").click(function(e){
        e.preventDefault();
        $this = $(this);

        // prevent multiple submissions
        if ($this.hasClass('loading')) return;
        $this.addClass('loading');

        $widget = $this.closest('.like-widget');
        $follow = $widget.find('.follow-question');
        $followButtons = $('.follow-question-button');

        // are we following or unfollowing
        var following = ($follow.hasClass('on'))? false : true;
        console.log(following);

        // follow ajax request
        $.getJSON($this.attr('href'), function(data, e) {

            // re-enable the button
            $this.removeClass('disabled');

            // respond to error
            // TODO: error handling when connected to backend
            if (!data.success && data['error_message'] != undefined) {
                $widget.popover({
                    'placement': 'right',
                    'trigger': 'hover',
                    'title': '',
                    'html': true,
                    'content': data.error_message
                }).popover('show');
                return;
            }

            // update button text
            if (following) {
                $this.find('.text').text('following');
                $this.addClass('disabled').addClass('on');
                $this.find('.icon-star').addClass('hidden');
            } else {
                $this.find('.text').text(' follow');
                $this.removeClass('disabled').removeClass('on');
                $this.find('.icon-star').removeClass('hidden');
            }

        });

        return false;

    }).hover(function(){
            var $this = $(this);
            if ($this.hasClass('on')) {
                $this.find('.text').text('unfollow');
            }
        }, function(){
            var $this = $(this);
            if ($this.hasClass('on')) {
                $(this).find('.text').text('following');
            }
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

    $('#id_revision').unbind().change(function(){
        $("#select_revision").click();
    });



    /* flag for review toggle */
    $('.flag-for-review').click(function(e){
        e.preventDefault();
        $form = $("#flag-question-form");

        // hide if already open
        if ($form.is(':visible')) {
            $form.slideUp();
            return;
        }

        $form.find('form').show();
        $form.find('.confirmation').hide();
        $form.slideDown();
    });

    /* flag for review submission and confirmation */
    $("#flag-question-form").submit(function(e){
        e.preventDefault();
        $form = $(this);

        // post the form
        $.post($form.attr('action'), $form.serialize());

        // animate the confirmation
        $form.find('form').slideUp();
        $form.find('.confirmation').show();
    });

    /* refer a friend toggle */
    $('.refer-friend').click(function(e){
        e.preventDefault();

        // scroll the user to the
        $('body').animate({scrollTop: $(this).offset().top - 240}, 300);

        $form = $("#refer-friend-form");
        if ($form.is(':visible')) {
            $form.slideUp();
        } else {
            $form.slideDown();
        }
    });

    /* validate email on refere a friend form */
    $("#fmanswer").validate({
        rules: {
            email: {
                required: true,
                email: true
            }
        },
        errorPlacement: function(error, element) {
            error.appendTo( element.parent() );
        }
    });


    /*
     * Display an error to users when they leave a page with a form partially completed
     * This is optin and handled through data attributes:
     * 1. add the attribute data-message-on-exit="your message here" to the form
     * 2. add the attribute data-message-on-exit-field="nameoffield" to the form,
     with nameoffield being the name attribute of the content to check the existance of when the user is leaving the page
     * If the user has entered data into the specified field and the page load was NOT initiated by a form submit, then show the error message
     */
    $(window).on('beforeunload', function(e){

        var message;

        // iterate through each of the flagged forms to check for partial completeness
        $('form[data-message-on-exit]').each(function(i, el){
            field = $(el).data('message-on-exit-field');
            if ( $(el).find('[name='+ field +']').val() ) {
                message = $(el).data('message-on-exit');
            }
        });

        if (message){
            if (/chrome|safari/i.test(document.userAgent)) {
                return message;
            } else {
                e.cancelBubble = true;
                e.stopPropagation();
                e.preventDefault();
                e.returnValue = message;
                return e;
            }


        }

    });
    $('form[data-message-on-exit]').submit(function(e){
        $(window).unbind('beforeunload');
    });


    /*
     * Utils
     */

    // Obtain cookie by its name
    function getCookie(name) {
        var name_eq = name + "=";
        var ca = document.cookie.split(';');
        for(var i=0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(name_eq) == 0) return c.substring(name_eq.length,c.length);
        }
        return null;
    }

    // Add CSRF token
    function addCsrf(params) {
        params['csrfmiddlewaretoken'] = getCookie('csrftoken');
        return params;
    }

    var LOADING_CLASS = 'loading';

    var ATTR_TEXT_LOADING = 'data-text-loading';
    var ATTR_TEXT_SUCCESS = 'data-text-success';
    var ATTR_TEXT_ORIGINAL = 'data-text-original';

    /*
     * Put a button in loading mode
     * button -- a button
     * loading -- true if loading
     */
    function setLoading(button, loading) {
        if (loading) {
            // Toggle status
            button.addClass('disabled');
            button.addClass(LOADING_CLASS);
            button.text(button.attr(ATTR_TEXT_LOADING));

            // Save original text
            button.attr(ATTR_TEXT_ORIGINAL, button.text());
        } else {
            // Toggle status
            button.removeClass(LOADING_CLASS);
            button.removeClass('disabled');

            // Restore original text
            button.text(button.attr(ATTR_TEXT_ORIGINAL));
        }
    }

    /*
     * Generic command callback
     * button -- the button that triggers the action
     * params -- http post parameters
     * finish -- function called when the action finishes
     */
    function handleCommand(button, params, finish) {
        if (button.hasClass('disabled')) {
            return;
        }

        var href = button.attr('href');

        // Update status
        if (button.hasClass(LOADING_CLASS)) {
            return;
        } else {
            setLoading(button, true);
        }

        // Make AJAX request
        $.post(href, addCsrf(params), function(data) {
            // Update status
            setLoading(button, false);

            // Handle result
            if (data.success) {
                button.text(button.attr(ATTR_TEXT_SUCCESS));
            } else {
                button.text(data.error_message);
            }

            button.addClass('disabled');

            // Finish
            finish(data);
        });
    }

    /*
     * ask-success (modal actions)
     * template: "_question_top.html"
     */

    var ask_success = $('#ask-success');

    if (ask_success) {
        /*
         * ACTION: Follow question's topics
         */
        var command_follow_topics = ask_success.find('#command-follow-topics').first();
        command_follow_topics.click(function(e) {
            e.preventDefault();
            handleCommand($(this), {
                // parameters here
            }, function(data) {
                // finish here
            });
        });
    }

    var checkFacebook = function(scope, setting, callback) {
        var save = function(authResponse) {
            $.get('/facebook/', {
                'access_token': authResponse.accessToken,
                'setting': setting
            }, function(response){
                callback();
            });
        };
        FB.getLoginStatus(function(response) {
            if (response.authResponse) {
                save(response.authResponse);
            } else {
                FB.ui(
                    {
                        method: 'oauth',
                        scope: scope,
                        //response_type: 'code'
                    },
                    function(response) {
                        FB.getLoginStatus(function(response) {
                            if (response.authResponse) {
                                save(response.authResponse);
                            }
                        }, true);
                    }
                );
            }
        }, true);
    };

    var askForm = $('#askform > form');
    if (askForm.length) {
        var post = false;
        askForm.submit(function(e){
            if (post) return true;
            //TODO: see checkbox before continue
            checkFacebook('email, publish_actions', 'new_question', function(){
                post = true;
                askForm.submit();
            });
            e.stopPropagation();
            e.preventDefault();
            return false;
        });
    };

    /*
    askForm.submit(function(e) {
        enviar -> return true;
        cancelar -> return false;
    });
    */


}); // end jquery enclosure