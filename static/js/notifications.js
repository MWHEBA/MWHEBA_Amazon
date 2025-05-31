/**
 * نظام الإشعارات باستخدام SweetAlert2
 */

// تنفيذ الكود عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // إضافة دالة عامة للإشعارات
    window.showNotification = function(type, message, title) {
        switch (type) {
            case 'success':
                showSuccessNotification(message, title || 'تم بنجاح');
                break;
            case 'error':
                showErrorNotification(message, title || 'خطأ');
                break;
            case 'warning':
                showWarningNotification(message, title || 'تحذير');
                break;
            case 'info':
                showInfoNotification(message, title || 'معلومات');
                break;
            default:
                showInfoNotification(message, title || 'معلومات');
        }
    };
    
    // معالجة رسائل Django
    processDjangoMessages();
});

/**
 * عرض إشعار نجاح
 * @param {string} message - نص الرسالة
 * @param {string} title - عنوان الإشعار (اختياري)
 * @param {number} timer - مدة ظهور الإشعار بالمللي ثانية (اختياري)
 */
function showSuccessNotification(message, title = 'تم بنجاح', timer = 3000) {
    if (typeof Swal === 'undefined') {
        alert(title + ': ' + message);
        return;
    }
    
    Swal.fire({
        icon: 'success',
        title: title,
        text: message,
        timer: timer,
        timerProgressBar: true,
        confirmButtonText: 'حسنًا',
        confirmButtonColor: '#28a745',
        iconColor: '#28a745',
        position: 'center'
    });
}

/**
 * عرض إشعار خطأ
 * @param {string} message - نص الرسالة
 * @param {string} title - عنوان الإشعار (اختياري)
 */
function showErrorNotification(message, title = 'خطأ') {
    if (typeof Swal === 'undefined') {
        alert(title + ': ' + message);
        return;
    }
    
    Swal.fire({
        icon: 'error',
        title: title,
        text: message,
        confirmButtonText: 'حسنًا',
        confirmButtonColor: '#dc3545',
        iconColor: '#dc3545',
        position: 'center'
    });
}

/**
 * عرض إشعار تحذير
 * @param {string} message - نص الرسالة
 * @param {string} title - عنوان الإشعار (اختياري)
 */
function showWarningNotification(message, title = 'تحذير') {
    if (typeof Swal === 'undefined') {
        alert(title + ': ' + message);
        return;
    }
    
    Swal.fire({
        icon: 'warning',
        title: title,
        text: message,
        confirmButtonText: 'حسنًا',
        confirmButtonColor: '#ffc107',
        iconColor: '#ffc107',
        position: 'center'
    });
}

/**
 * عرض إشعار معلومات
 * @param {string} message - نص الرسالة
 * @param {string} title - عنوان الإشعار (اختياري)
 */
function showInfoNotification(message, title = 'معلومات') {
    if (typeof Swal === 'undefined') {
        alert(title + ': ' + message);
        return;
    }
    
    Swal.fire({
        icon: 'info',
        title: title,
        text: message,
        confirmButtonText: 'حسنًا',
        confirmButtonColor: '#17a2b8',
        iconColor: '#17a2b8',
        position: 'center'
    });
}

/**
 * عرض مربع حوار تأكيد
 * @param {string} message - نص الرسالة
 * @param {string} title - عنوان الإشعار (اختياري)
 * @param {Function} confirmCallback - دالة يتم تنفيذها عند التأكيد
 * @param {Function} cancelCallback - دالة يتم تنفيذها عند الإلغاء (اختياري)
 */
function showConfirmNotification(message, title = 'تأكيد', confirmCallback, cancelCallback = null) {
    if (typeof Swal === 'undefined') {
        const isConfirmed = confirm(title + ': ' + message);
        if (isConfirmed && typeof confirmCallback === 'function') {
            confirmCallback();
        } else if (!isConfirmed && typeof cancelCallback === 'function') {
            cancelCallback();
        }
        return;
    }
    
    Swal.fire({
        icon: 'question',
        title: title,
        text: message,
        showCancelButton: true,
        confirmButtonText: 'نعم',
        cancelButtonText: 'إلغاء',
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        focusConfirm: false,
        showCloseButton: true,
        position: 'center'
    }).then((result) => {
        if (result.isConfirmed && typeof confirmCallback === 'function') {
            confirmCallback();
        } else if (result.dismiss === Swal.DismissReason.cancel && typeof cancelCallback === 'function') {
            cancelCallback();
        }
    });
}

/**
 * عرض مربع إدخال
 * @param {string} message - نص الرسالة
 * @param {string} title - عنوان الإشعار (اختياري)
 * @param {Function} inputCallback - دالة يتم تنفيذها عند الإدخال
 * @param {string} inputPlaceholder - نص توضيحي للإدخال (اختياري)
 * @param {string} inputType - نوع الإدخال (اختياري)
 */
function showInputNotification(message, title = 'إدخال', inputCallback, inputPlaceholder = '', inputType = 'text') {
    if (typeof Swal === 'undefined') {
        const inputValue = prompt(title + ': ' + message, inputPlaceholder);
        if (inputValue !== null && typeof inputCallback === 'function') {
            inputCallback(inputValue);
        }
        return;
    }
    
    Swal.fire({
        title: title,
        text: message,
        input: inputType,
        inputPlaceholder: inputPlaceholder,
        showCancelButton: true,
        confirmButtonText: 'تأكيد',
        cancelButtonText: 'إلغاء',
        inputValidator: (value) => {
            if (!value) {
                return 'يرجى إدخال قيمة!';
            }
        },
        showCloseButton: true,
        focusConfirm: false,
        position: 'center'
    }).then((result) => {
        if (result.isConfirmed && typeof inputCallback === 'function') {
            inputCallback(result.value);
        }
    });
}

/**
 * عرض إشعار من Django Messages
 * @param {string} message - نص الرسالة
 * @param {string} tags - فئات الرسالة (success, error, warning, info)
 */
function showDjangoMessageNotification(message, tags) {
    let icon = 'info';
    let title = 'معلومات';
    let iconColor = '#17a2b8';
    let buttonColor = '#17a2b8';

    if (tags.includes('success')) {
        icon = 'success';
        title = 'تم بنجاح';
        iconColor = '#28a745';
        buttonColor = '#28a745';
    } else if (tags.includes('error')) {
        icon = 'error';
        title = 'خطأ';
        iconColor = '#dc3545';
        buttonColor = '#dc3545';
    } else if (tags.includes('warning')) {
        icon = 'warning';
        title = 'تحذير';
        iconColor = '#ffc107';
        buttonColor = '#ffc107';
    }

    if (typeof Swal === 'undefined') {
        alert(title + ': ' + message);
        return;
    }
    
    Swal.fire({
        icon: icon,
        title: title,
        text: message,
        confirmButtonText: 'حسنًا',
        confirmButtonColor: buttonColor,
        iconColor: iconColor,
        position: 'center'
    });
}

/**
 * عرض إشعار مخصص
 * @param {Object} options - خيارات الإشعار
 */
function showCustomNotification(options) {
    if (typeof Swal === 'undefined') {
        alert(options.title + ': ' + options.text);
        return;
    }
    
    // إضافة خاصية position إذا لم تكن موجودة
    if (!options.position) {
        options.position = 'center';
    }
    
    Swal.fire(options);
}

/**
 * استبدال دالة showAlert الموجودة بالفعل
 * @param {string} message - نص الرسالة
 * @param {string} type - نوع الإشعار (success, error/danger, warning, info)
 */
function showAlert(message, type) {
    switch (type) {
        case 'success':
            showSuccessNotification(message);
            break;
        case 'danger':
        case 'error':
            showErrorNotification(message);
            break;
        case 'warning':
            showWarningNotification(message);
            break;
        case 'info':
            showInfoNotification(message);
            break;
        default:
            showInfoNotification(message);
    }
}

/**
 * معالجة رسائل Django عند تحميل الصفحة
 */
function processDjangoMessages() {
    // البحث عن حاويات رسائل Django
    const djangoMessages = document.querySelectorAll('.django-messages .alert');
    
    if (djangoMessages.length > 0) {
        // إزالة حاوية الرسائل من DOM بعد معالجتها
        const messageContainer = document.querySelector('.django-messages');
        
        djangoMessages.forEach(function(message) {
            // استخراج النص والنوع
            const messageText = message.textContent.trim();
            let messageType = 'info';
            
            if (message.classList.contains('alert-success')) {
                messageType = 'success';
            } else if (message.classList.contains('alert-danger')) {
                messageType = 'error';
            } else if (message.classList.contains('alert-warning')) {
                messageType = 'warning';
            }
            
            // عرض الإشعار
            showAlert(messageText, messageType);
        });
        
        // إزالة حاوية الرسائل من DOM
        if (messageContainer) {
            messageContainer.remove();
        }
    }
} 