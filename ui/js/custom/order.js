var productPrices = {};
var productOptionsHtml = '<option value="">-- Select Product --</option>';
var productOptionsLoaded = false;

$(function () {
    ensureInitialRow();
    loadProductOptions();
});

function buildProductOptions(products) {
    productPrices = {};
    var options = '<option value="">-- Select Product --</option>';

    $.each(products || [], function (index, product) {
        options += '<option value="' + product.product_id + '">' + escapeHtml(product.name) + '</option>';
        productPrices[String(product.product_id)] = parseFloat(product.price_per_unit) || 0;
    });

    productOptionsHtml = options;
    productOptionsLoaded = true;
    applyProductOptionsToRows();
}

function applyProductOptionsToRows() {
    $("#itemsInOrder .cart-product").each(function () {
        var currentValue = $(this).val();
        $(this).html(productOptionsHtml);

        if (currentValue) {
            $(this).val(String(currentValue));
        }

        $(this).prop("disabled", false);
    });
}

function loadProductOptions() {
    return $.getJSON(productListApiUrl)
        .done(function (response) {
            buildProductOptions(response || []);
            calculateValue();
        })
        .fail(function () {
            productOptionsHtml = '<option value="">-- Select Product --</option>';
            productOptionsLoaded = false;
            $("#itemsInOrder .cart-product").html(productOptionsHtml).prop("disabled", false);
        });
}

function getRowTemplate() {
    return $(".product-box .product-item").first().prop("outerHTML");
}

function ensureInitialRow() {
    if ($("#itemsInOrder .product-item").length === 0) {
        addOrderRow(false);
    }
    calculateValue();
}

function addOrderRow(showRemove) {
    var rowHtml = getRowTemplate();
    var row = $(rowHtml);

    row.find(".remove-row").toggleClass("hidden", !showRemove);
    row.find(".product-price").val("0.00");
    row.find(".product-qty").val("1");
    row.find(".product-total").val("0.00");

    var select = row.find(".cart-product");
    select.html(productOptionsHtml);
    select.prop("disabled", false);

    $("#itemsInOrder").append(row);

    calculateValue();
}

$("#addMoreButton").on("click", function () {
    addOrderRow(true);
});

$(document).on("click", ".remove-row", function () {
    $(this).closest('.product-item').remove();
    if ($("#itemsInOrder .product-item").length === 0) {
        addOrderRow(false);
    }
    calculateValue();
});

$(document).on("change", ".cart-product", function () {
    var productId = String($(this).val() || "");
    var price = productPrices[productId] || 0;
    $(this).closest('.product-item').find('.product-price').val(Number(price).toFixed(2));
    calculateValue();
});

$(document).on("input change", ".product-price, .product-qty", function () {
    calculateValue();
});

$("#saveOrder").on("click", function () {
    var customerName = $("#customerName").val().trim();

    if (!customerName) {
        alert("Customer name is required.");
        return;
    }

    if (!productOptionsLoaded) {
        alert("Products are still loading. Please try again in a moment.");
        return;
    }

    var orderDetails = [];
    var valid = true;

    $("#itemsInOrder .product-item").each(function () {
        var productId = $(this).find(".cart-product").val();
        var qty = parseFloat($(this).find(".product-qty").val()) || 0;
        var price = parseFloat($(this).find(".product-price").val()) || 0;
        var total = parseFloat($(this).find(".product-total").val()) || 0;

        if (!productId) {
            valid = false;
            return false;
        }
        if (qty <= 0) {
            valid = false;
            return false;
        }

        orderDetails.push({
            product_id: productId,
            quantity: qty,
            total_price: total || (qty * price)
        });
    });

    if (!valid || !orderDetails.length) {
        alert("Please select at least one product and enter a valid quantity.");
        return;
    }

    calculateValue();
    var grandTotal = $("#product_grand_total").val();

    var requestPayload = {
        customer_name: customerName,
        grand_total: grandTotal,
        order_details: orderDetails
    };

    callApi("POST", orderSaveApiUrl, {
        data: JSON.stringify(requestPayload)
    }, function () {
        alert("Order saved successfully.");
        window.location.href = "/dashboard";
    });
});

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
