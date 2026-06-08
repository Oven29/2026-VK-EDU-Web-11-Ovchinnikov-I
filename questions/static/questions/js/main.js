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
                'id': objectId,
                'type': action
            },
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (data) {
                $counter.text(data.rating);

                // Optional: toggle active classes for visual feedback
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
                    // Remove correct status from other cards
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
                // Revert checkbox state on error
                $this.prop('checked', !$this.prop('checked'));
            }
        });
    });

    $('#editor').on('input', function () {
        const text = $(this).val();
        const countSymbols = text.length;
        const $counter = $('#count-symbols');

        if (countSymbols >= 3000) {
            $(this).val(text.slice(0, 3000));
        }

        $counter.text(`${countSymbols}/3000`);
    }).trigger('input');
});
