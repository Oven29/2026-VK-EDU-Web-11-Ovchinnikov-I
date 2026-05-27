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
    const centrifugoUrl = $answersList.data('centrifugo-url');
    const centrifugoToken = $answersList.data('centrifugo-token');
    const questionId = $answersList.data('question-id');

    if (centrifugoUrl && centrifugoToken && questionId) {
        const centrifuge = new Centrifuge(centrifugoUrl, {
            token: centrifugoToken
        });

        centrifuge.on('connecting', function (ctx) {
            console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
        }).on('connected', function (ctx) {
            console.log(`connected over ${ctx.transport}`);
        }).on('disconnected', function (ctx) {
            console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
        }).connect();

        const sub = centrifuge.newSubscription(`question_${questionId}`);

        sub.on('publication', function (ctx) {
            const data = ctx.data;
            
            // Get current page from URL
            const urlParams = new URLSearchParams(window.location.search);
            const page = parseInt(urlParams.get('page')) || 1;

            if (page === 1) {
                $('.empty-state').remove();

                const answerHtml = `
                    <div class="answer-card" id="answer-${data.id}">
                        <div class="row g-3">
                            <div class="col-auto text-center">
                                <div class="vote-widget" data-id="${data.id}" data-type="answer">
                                    <span class="vote-btn vote-up" data-action="up">+</span>
                                    <div class="vote-count">0</div>
                                    <span class="vote-btn vote-down" data-action="down">-</span>
                                </div>
                            </div>
                            <div class="col">
                                <p>${data.content}</p>
                                <div class="form-check d-inline-block">
                                    <input class="form-check-input correct-checkbox" type="checkbox" value="${data.id}" id="correct${data.id}" disabled>
                                    <label class="form-check-label" for="correct${data.id}">Верно!</label>
                                </div>
                                <div class="d-flex justify-content-between align-items-center mt-3 flex-wrap gap-1">
                                    <div>
                                        <small>
                                            <a href="/user/${data.username}/" class="fw-medium">${data.author}</a>
                                        </small>
                                    </div>
                                    <div class="text-muted">
                                        <small>${data.created_at}</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>`;
                
                const $newAnswer = $(answerHtml);
                const $nav = $('.pagination').closest('nav');
                
                if ($nav.length) {
                    $newAnswer.insertBefore($nav);
                } else {
                    $answersList.append($newAnswer);
                }
            } else {
                alert(`Новый ответ от ${data.author}!`);
            }
        }).subscribe();
    }
});
