const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$(document).ready(function () {
    // Vote logic
    $('.vote-btn').on('click', function () {
        const $this = $(this);
        const action = $this.data('action');
        const $container = $this.closest('.vote-widget');
        const $counter = $container.find('.vote-count');

        const objectId = $container.data('id');
        const objectType = $container.data('type');

        if ($this.hasClass('disabled')) {
            return;
        }

        const url = `/vote/${(objectType === 'question' ? 'question' : 'answer')}/${objectId}/`;

        $.ajax({
            url: url,
            method: 'POST',
            data: {
                'type': action
            },
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (data) {
                $counter.text(data.rating);

                const $opposed = $this.siblings('.vote-btn');
                if ($this.hasClass('active')) {
                    $this.removeClass('active');
                } else {
                    $this.addClass('active');
                    $opposed.removeClass('active');
                }
            },
            error: function (xhr) {
                console.error('Error voting:', xhr.responseJSON);
                if (xhr.status === 403) {
                    alert('Пожалуйста, войдите в систему, чтобы голосовать.');
                }
            }
        });
    });

    // Mark correct logic
    $('.correct-checkbox').on('change', function () {
        const $this = $(this);
        const answerId = $this.val();
        const $card = $this.closest('.answer-card');
        const $label = $card.find('.form-check-label');

        $.ajax({
            url: `/answer/correct/${answerId}/`,
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (data) {
                if (data.is_correct) {
                    $('.answer-card').removeClass('correct-answer');
                    $('.form-check-label').removeClass('correct-label');
                    $('.correct-checkbox').not($this).prop('checked', false);

                    $card.addClass('correct-answer');
                    $label.addClass('correct-label');
                } else {
                    $card.removeClass('correct-answer');
                    $label.removeClass('correct-label');
                }
            },
            error: function (xhr) {
                console.error('Error marking correct:', xhr.responseJSON);
                $this.prop('checked', !$this.prop('checked'));
            }
        });
    });

    // Editor symbol counter
    $('#editor').on('input', function () {
        const text = $(this).val();
        const countSymbols = text.length;
        const $counter = $('#count-symbols');

        if (countSymbols >= 3000) {
            $(this).val(text.slice(0, 3000));
        }

        $counter.text(`${countSymbols}/3000`);
    }).trigger('input');

    // Centrifugo Real-time updates
    const $answersList = $('.answers-list');
    if ($answersList.length) {
        const centrifugoUrl = $answersList.data('centrifugo-url');
        const centrifugoToken = $answersList.data('centrifugo-token');
        const questionId = $answersList.data('question-id');
        const currentPage = parseInt($answersList.data('page')) || 1;

        if (centrifugoUrl && centrifugoToken && questionId) {
            const centrifuge = new Centrifuge(`${centrifugoUrl}`, {
                token: centrifugoToken
            });

            centrifuge.on('connecting', ctx => {
                console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
            }).on('connected', ctx => {
                console.log(`connected over ${ctx.transport}`);
            }).on('disconnected', ctx => {
                console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
            }).connect();

            const sub = centrifuge.newSubscription(`questions:${questionId}`);

            sub.on('publication', ctx => {
                const data = ctx.data;

                if (currentPage === 1) {
                    // Remove empty state if present
                    $('.empty-state').remove();

                    // Clone template
                    const $template = $('#answer-template .answer-card').clone();

                    // Fill data
                    $template.attr('id', `answer-${data.id}`);
                    $template.find('.vote-widget').attr('data-id', data.id);
                    $template.find('.answer-content-placeholder').text(data.content);

                    const $checkbox = $template.find('.correct-checkbox-placeholder');
                    $checkbox.attr('id', `correct${data.id}`).val(data.id);
                    $template.find('label').attr('for', `correct${data.id}`);

                    const $authorLink = $template.find('.answer-author-link');
                    $authorLink.attr('href', `/user/${data.author.username}/`);
                    $template.find('.answer-author-name').text(data.author.name);

                    if (data.author.profile_photo_url) {
                        $template.find('.answer-author-avatar').attr('src', data.author.profile_photo_url).show();
                    }

                    $template.find('.answer-date-placeholder').text(data.created_at);

                    // Insert into DOM
                    const $nav = $('.pagination').closest('nav');
                    if ($nav.length) {
                        $template.insertBefore($nav);
                    } else {
                        $answersList.append($template);
                    }

                    // Small fade-in effect
                    $template.hide().fadeIn(500);
                } else {
                    // Show Bootstrap Toast on other pages
                    const toastEl = document.getElementById('new-answer-toast');
                    if (toastEl) {
                        const toast = new bootstrap.Toast(toastEl);
                        toast.show();
                        setTimeout(() => {
                            toast.hide();
                        }, 5000);
                    }
                }
            }).on('subscribing', function (ctx) {
                console.log(`subscribing: ${ctx.code}, ${ctx.reason}`);
            }).on('subscribed', function (ctx) {
                console.log('subscribed', ctx);
            }).on('unsubscribed', function (ctx) {
                console.log(`unsubscribed: ${ctx.code}, ${ctx.reason}`);
            }).subscribe();
        }
    }
});
