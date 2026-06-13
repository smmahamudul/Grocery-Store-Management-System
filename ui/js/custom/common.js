var productListApiUrl = '/api/getProducts';
var uomListApiUrl = '/api/getUOM';
var productSaveApiUrl = '/api/saveProduct';
var productDeleteApiUrl = '/api/deleteProduct';
var orderListApiUrl = '/api/getAllOrders';
var orderSaveApiUrl = '/api/insertOrder';
var currentUserApiUrl = '/api/me';

function callApi(method, url, data, successCallback) {
    $.ajax({
        method: method,
        url: url,
        data: data
    }).done(function (msg) {
        if (typeof successCallback === 'function') {
            successCallback(msg);
        } else {
            window.location.reload();
        }
    }).fail(function (xhr) {
        var message = 'Something went wrong';
        if (xhr && xhr.responseJSON && xhr.responseJSON.error) {
            message = xhr.responseJSON.error;
        }
        alert(message);
    });
}

function calculateValue() {
    var total = 0.0;
    $("#itemsInOrder .product-item").each(function () {
        var qty = parseFloat($(this).find('.product-qty').val()) || 0;
        var price = parseFloat($(this).find('.product-price').val()) || 0;
        var itemTotal = qty * price;
        $(this).find('.product-total').val(itemTotal.toFixed(2));
        total += itemTotal;
    });
    $("#product_grand_total").val(total.toFixed(2));
    $("#grandTotalText").text("₩" + total.toFixed(2));
}

function setCurrentUser() {
    $.getJSON(currentUserApiUrl).done(function (response) {
        $("#currentUserName").text(response && response.name ? response.name : 'Admin');
    });
}

function escapeHtml(value) {
    return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

$(function () {
    setCurrentUser();
});
