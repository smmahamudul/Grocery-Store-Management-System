var productModal = $("#productModal");

$(function () {
    loadProducts();

    productModal.on('show.bs.modal', function () {
        loadUoms();
    });

    productModal.on('hidden.bs.modal', function () {
        resetProductForm();
        productModal.removeData('selected-unit');
    });
});

function loadProducts() {
    $.getJSON(productListApiUrl, function (response) {
        var rows = '';
        if (response && response.length) {
            $.each(response, function (index, product) {
                rows += '<tr data-id="' + product.product_id + '" data-name="' + escapeHtml(product.name) + '" data-unit="' + product.uom_id + '" data-price="' + product.price_per_unit + '">' +
                    '<td>' + escapeHtml(product.name) + '</td>' +
                    '<td>' + escapeHtml(product.uom_name) + '</td>' +
                    '<td>₩' + Number(product.price_per_unit).toFixed(2) + '</td>' +
                    '<td>' +
                        '<button type="button" class="btn btn-sm btn-outline-green edit-product mr-2">Edit</button> ' +
                        '<button type="button" class="btn btn-sm btn-danger delete-product">Delete</button>' +
                    '</td>' +
                '</tr>';
            });
        } else {
            rows = '<tr><td colspan="4" class="no-data">No products found</td></tr>';
        }
        $("#productsTableBody").html(rows);
    });
}

function loadUoms() {
    $.getJSON(uomListApiUrl, function (response) {
        if (response) {
            var options = '<option value="">-- Select --</option>';
            $.each(response, function (index, uom) {
                options += '<option value="' + uom.uom_id + '">' + escapeHtml(uom.uom_name) + '</option>';
            });
            $("#uoms").html(options);
            var selectedUnit = productModal.data('selected-unit');
            if (selectedUnit) {
                $("#uoms").val(String(selectedUnit));
            }
        }
    });
}

function resetProductForm() {
    $("#product_id").val('0');
    $("#name").val('');
    $("#uoms").val('');
    $("#price").val('');
    productModal.find('.modal-title').text('Add New Product');
}

$("#saveProduct").on("click", function () {
    var productId = $("#product_id").val().trim();
    var productName = $("#name").val().trim();
    var uomId = $("#uoms").val();
    var price = $("#price").val().trim();

    if (!productName || !uomId || !price) {
        alert("Please fill in all product fields.");
        return;
    }

    var requestPayload = {
        product_id: productId,
        product_name: productName,
        uom_id: uomId,
        price_per_unit: price
    };

    callApi("POST", productSaveApiUrl, {
        data: JSON.stringify(requestPayload)
    }, function () {
        productModal.modal('hide');
        loadProducts();
    });
});

$(document).on("click", ".edit-product", function () {
    var tr = $(this).closest('tr');
    $("#product_id").val(tr.data('id'));
    $("#name").val(tr.data('name'));
    $("#price").val(tr.data('price'));
    productModal.data('selected-unit', tr.data('unit'));
    productModal.find('.modal-title').text('Edit Product');
    productModal.modal('show');
});

$(document).on("click", ".delete-product", function () {
    var tr = $(this).closest('tr');
    var isDelete = confirm("Are you sure you want to delete " + tr.data('name') + "?");
    if (isDelete) {
        callApi("POST", productDeleteApiUrl, {
            product_id: tr.data('id')
        }, function () {
            loadProducts();
        });
    }
});
