/**
 * الكود الرئيسي للتطبيق
 */

// تنفيذ الكود عند اكتمال تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // إخفاء رسائل التنبيه تلقائيًا بعد 5 ثوانٍ
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.display = 'none';
            }
        });
    }, 5000);

    // تفعيل جميع tooltips
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // معالج زر تسجيل البيع
    const saleButtons = document.querySelectorAll('.sale-button');
    if (saleButtons) {
        saleButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const productId = this.getAttribute('data-product-id');
                const productName = this.getAttribute('data-product-name');
                
                // التحقق من وجود دالة showInputNotification
                if (typeof showInputNotification === 'function') {
                    // استخدام SweetAlert2 لإدخال كمية البيع
                    showInputNotification(
                        `أدخل كمية البيع للمنتج "${productName}":`,
                        'تسجيل بيع',
                        function(quantity) {
                            recordSale(productId, parseInt(quantity));
                        },
                        '1',
                        'number'
                    );
                } else {
                    // استخدام الدالة الأصلية إذا لم تكن دالة showInputNotification موجودة
                    const quantity = prompt(`أدخل كمية البيع للمنتج "${productName}":`, "1");
                    if (quantity !== null && quantity.trim() !== '') {
                        recordSale(productId, parseInt(quantity));
                    }
                }
            });
        });
    }
});

/**
 * تسجيل عملية بيع عبر AJAX
 * @param {number} productId - معرف المنتج
 * @param {number} quantity - الكمية المباعة
 */
function recordSale(productId, quantity) {
    // التحقق من صحة المدخلات
    if (isNaN(quantity) || quantity <= 0) {
        if (typeof showErrorNotification === 'function') {
            showErrorNotification('يجب إدخال كمية صحيحة وموجبة');
        } else {
            alert('خطأ: يجب إدخال كمية صحيحة وموجبة');
        }
        return;
    }

    // إرسال طلب AJAX
    fetch('/inventory/record-sale/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // تحديث كمية المنتج في الواجهة
            const quantityElement = document.querySelector(`#product-quantity-${productId}`);
            if (quantityElement) {
                quantityElement.textContent = data.new_quantity;
            }
            
            // عرض رسالة نجاح
            let message = `تم تسجيل بيع ${quantity} وحدة بنجاح.`;
            if (data.sync_success) {
                message += ' تمت مزامنة الكمية مع أمازون.';
                if (typeof showSuccessNotification === 'function') {
                    showSuccessNotification(message);
                } else {
                    alert(message);
                }
            } else {
                message += ' فشلت مزامنة الكمية مع أمازون.';
                if (typeof showWarningNotification === 'function') {
                    showWarningNotification(message);
                } else {
                    alert(message);
                }
            }
            
            // إعادة تحميل الصفحة بعد ثانيتين
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            if (typeof showErrorNotification === 'function') {
                showErrorNotification(`خطأ: ${data.error}`);
            } else {
                alert(`خطأ: ${data.error}`);
            }
        }
    })
    .catch(error => {
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(`خطأ في الاتصال: ${error}`);
        } else {
            alert(`خطأ في الاتصال: ${error}`);
        }
    });
}

/**
 * الحصول على رمز CSRF من ملفات تعريف الارتباط
 * @returns {string} رمز CSRF
 */
function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken='.length) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken='.length));
                break;
            }
        }
    }
    return cookieValue;
} 