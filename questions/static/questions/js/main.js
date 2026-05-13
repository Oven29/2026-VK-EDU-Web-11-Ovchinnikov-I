const validEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    return emailRegex.test(email);
}

$(document).ready(function () {
    $('.vote-btn').on('click', function () {
        const $this = $(this);
        const action = $this.data('action');
        const $container = $this.closest('.vote-widget');
        const $counter = $container.find('.vote-count');
        const $opposed = $this.siblings('.vote-btn');

        let currentVotes = parseInt($counter.text());

        if ($this.hasClass('active')) {
            $this.removeClass('active');
            $counter.text(action === 'up' ? currentVotes - 1 : currentVotes + 1);
            return;
        }

        if ($opposed.hasClass('active')) {
            $opposed.removeClass('active');
            currentVotes = action === 'up' ? currentVotes + 1 : currentVotes - 1;
        }

        $this.addClass('active');
        if (action === 'up') {
            $this.addClass('');
            $counter.text(currentVotes + 1);
        } else {
            $this.addClass('');
            $counter.text(currentVotes - 1);
        }
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

    $('.email-input').on('input', function () {
        const text = $(this).val();
        $('.error-msg').text(!validEmail(text) && text ? 'Invalid email address' : '');
    }).trigger('input');
});
