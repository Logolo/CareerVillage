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

//  enable affix positioning of sidebar on the about page
    setTimeout(function () {
      var $window = $(window);
      $('.about-page .sidebar-widget').affix({
        offset: {
          top: 0
        , bottom: 270
        }
      })
    }, 200)


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
                    'trigger': 'click',
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

            /*
             * Facebook action
             */
            var facebookPermission = data['facebook-permission'];
            var facebookAskPermission = data['facebook-ask-permission'];
            var nodeId = $this.data('node-id');

            if (facebookAskPermission) {
                var shareBtn = $('<button>').addClass('btn-success btn').text('Yes, share on Facebook'),
                dontShareBtn = $('<button>').addClass('btn btn-mini').css('margin-top', '4px').text('No thanks'),
                message =  $('<p>')
                    .text("We can automatically share your likes on Facebook so your friends benefit too. How about it?")
                    .append($('<br>'))
                    .append(shareBtn)
                    .append($('<br>'))
                    .append(dontShareBtn);

                shareBtn.click(function() {
                    if (!shareBtn.hasClass('disabled')) {
                        shareBtn.addClass('disabled');
                        dontShareBtn.hide();

                        checkFacebook('email, publish_actions', facebookPermission, shareBtn,
                            function(success, response) {
                                if (success && response['like_success']) {
                                    shareBtn.text('Thanks!');
                                } else {
                                }
                            }, {
                                'node_id': nodeId
                            }
                        );
                    }
                });
                dontShareBtn.click(function(){
                    $widget.popover('hide');
                });


                $widget.popover({
                    'placement': 'right',
                    'trigger': 'manual',
                    'title': '<h5 style="margin:0">Thanks for liking this question!</h5>',
                    'html': true,
                    'content': message
                }).popover('show');
            } else {
                // For second time likers, suggest they follow this question
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
        var htmlForm = $form.find('form');

        // post the form
        $.post(htmlForm.attr('action'), htmlForm.serialize(), function(data) {
            if (data.success) {
                // animate the confirmation
                htmlForm.slideUp();
                $form.find('.confirmation').show();
            } else {
                htmlForm.find('.flag-message').html(data.error_message);
            }
        });
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

    /*
     * Check that there is an active Facebook account and is valid on the server.
     * scope -- Facebook scope.
     * setting -- Setting that enables the action (the name of an attribute of User.prop. ex. 'new_question').
     * popoverElement -- Element to which attach a popover in case something goes wrong.
     * callback -- Function called when the response is received (takes a parameter indicating success).
     */
    var checkFacebook = function(scope, setting, popoverElement, callback, parameters) {
        var save = function(authResponse) {
            if (parameters == undefined) parameters = {};
            parameters['access_token'] = authResponse.accessToken,
            parameters['setting'] = setting;

            popoverElement.addClass('btn-loading');
            $.post(FB_COMMAND_URL, addCsrf(parameters), function(response) {
                callback(response['facebook_success'], response);
                popoverElement.removeClass('btn-loading');
                if (!response['facebook_success']) {
                    // Notify the user
                    popoverElement.popover({
                        'placement': 'top',
                        'trigger': 'manual',
                        'content': FB_FAILURE
                    }).popover('show');
                    setTimeout(function() {
                        popoverElement.popover('hide');
                    }, 3000);

                    // Enable submit buton
                    popoverElement.removeClass('disabled');
                    popoverElement.removeAttr('disabled');
                }
            });
        };
        popoverElement.addClass('btn-loading');
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
                        popoverElement.removeClass('btn-loading');
                        FB.getLoginStatus(function(response) {
                            if (response.authResponse) {
                                save(response.authResponse);
                            } else {
                                callback(false);

                                // Enable submit buton
                                popoverElement.removeClass('disabled');
                                popoverElement.removeAttr('disabled');
                            }
                        }, true);
                    }
                );
            }
        }, true);
    };

    /*
     * Override submit action in the "ask question" form.
     */
    var askForm = $('#askform > form');
    var askSubmitButton = askForm.find('input[type="submit"][name="ask"]');
    var askCheckBox = askForm.find('input[type="checkbox"][name="auto-share-checkbox"]');
    if (askForm.length) {
        var post = false;
        var submitted = false;

        // Ensure that the submit button is enabled by default
        askSubmitButton.removeClass('disabled');
        askSubmitButton.removeAttr('disabled');

        askForm.submit(function(e) {
            if (post) return true;
            if (submitted) return false;
            submitted = true;

            // Disable submit button
            askSubmitButton.addClass('disabled');
            askSubmitButton.attr('disabled', '');

            // Get checkbox value
            if (askCheckBox.length && askCheckBox.is(':checked')) {
                checkFacebook('email, publish_actions', 'facebook_ask_question_story', askSubmitButton,
                    function(success) {
                        if (success) {
                            post = true;
                            askForm.submit();
                        } else {
                            submitted = false;
                            askCheckBox.removeAttr('checked');

                            // Facebook share disabled
                            askCheckBox.popover({
                                'placement': 'left',
                                'trigger': 'manual',
                                'content': FB_DISABLED
                            }).popover('show');
                            setTimeout(function() {
                                askCheckBox.popover('hide');
                            }, 3000);
                        }
                    }
                );
            } else {
                post = true;
                askForm.submit();
            }

            // Prevent default submit
            e.stopPropagation();
            e.preventDefault();
            return false;
        });
    };

    /*
     * Override submit action in the "answer question" form.
     */
    var answerForm = $('#fmanswer');
    var answerSubmitButton = answerForm.find('input[type="submit"]');
    var answerCheckBox = answerForm.find('input[type="checkbox"]');
    if (answerForm.length) {
        var post = false;
        var submitted = false;

        // Ensure that the submit button is enabled by default
        answerSubmitButton.removeClass('disabled');
        answerSubmitButton.removeAttr('disabled');

        answerForm.submit(function(e) {
            if (post) return true;
            if (submitted) return false;
            submitted = true;

            // Disable submit button
            answerSubmitButton.addClass('disabled');
            answerSubmitButton.attr('disabled', '');

            // Get checkbox value
            if (answerCheckBox.length && answerCheckBox.is(':checked')) {
                checkFacebook('email, publish_actions', 'facebook_answer_question_story', answerSubmitButton,
                    function(success) {
                        if (success) {
                            post = true;
                            answerForm.submit();
                        } else {
                            submitted = false;
                            answerCheckBox.removeAttr('checked');

                            // Facebook share disabled
                            answerCheckBox.popover({
                                'placement': 'left',
                                'trigger': 'manual',
                                'content': FB_DISABLED
                            }).popover('show');
                            setTimeout(function() {
                                answerCheckBox.popover('hide');
                            }, 3000);
                        }
                    }
                );
            } else {
                post = true;
                answerForm.submit();
            }

            // Prevent default submit
            e.stopPropagation();
            e.preventDefault();
            return false;
        });
    };

}); // end jquery enclosure