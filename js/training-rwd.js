/* 封閉 DEMO：只允許同資料夾內兩個課程頁切換，不送出資料。 */
(function () {
    'use strict';
    var form = document.getElementById('course-search');
    if (!form) return;
    var start = document.getElementById('time_start');
    var end = document.getElementById('time_end');
    var error = document.getElementById('search-error');
    var dialog = document.getElementById('demo-dialog');
    var message = document.getElementById('demo-message');

    function showDemo(label) {
        message.textContent = '「' + label + '」僅供功能展示，不會跳轉外部頁面或送出資料。';
        if (!dialog.open) dialog.showModal();
    }

    document.addEventListener('click', function (event) {
        var link = event.target.closest('a');
        if (!link) return;
        if (link.hasAttribute('data-demo-label')) {
            event.preventDefault();
            showDemo(link.getAttribute('data-demo-label'));
            return;
        }
        var raw = link.getAttribute('href') || '';
        if (raw.charAt(0) === '#') return;
        var destination = new URL(raw, window.location.href);
        var folder = new URL('.', window.location.href);
        var allowed = ['training.html', 'training-page2.html', 'index.html', 'training.php', 'training-page2.php'];
        var localPage = allowed.some(function (name) {
            return destination.href === new URL(name, folder).href;
        });
        if (!localPage) {
            event.preventDefault();
            showDemo(link.textContent.trim() || '此功能');
        }
    });

    function clearError() {
        end.setCustomValidity('');
        error.hidden = true;
        error.textContent = '';
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        clearError();
        if (start.value && end.value && start.value > end.value) {
            event.preventDefault();
            error.textContent = '結束日期不得早於開始日期，請重新選擇。';
            error.hidden = false;
            end.setCustomValidity(error.textContent);
            end.focus();
            end.reportValidity();
            return;
        }
        showDemo('課程搜尋');
    });
    form.addEventListener('reset', clearError);
    start.addEventListener('input', clearError);
    end.addEventListener('input', clearError);
}());
