var orderCache = {};

$(function () {
    loadDashboard();
    $(document).on('click', '.view-order-btn', function () {
        var orderId = $(this).data('order-id');
        var order = orderCache[orderId];
        var rows = '';

        if (!order) {
            return;
        }

        var details = order.order_details || [];

        $('#orderDetailsModal .modal-title').text('Order #' + order.order_id);
        $('#orderDetailsMeta').html(
            '<strong>Customer:</strong> ' + escapeHtml(order.customer_name) +
            ' &nbsp; | &nbsp; <strong>Date:</strong> ' + escapeHtml(order.datetime) +
            ' &nbsp; | &nbsp; <strong>Total:</strong> ₩' + Number(order.total).toFixed(2)
        );

        if (!details.length) {
            rows = '<tr><td colspan="4" class="no-data">No order items found</td></tr>';
        } else {
            $.each(details, function (_, item) {
                rows += '<tr>' +
                    '<td>' + escapeHtml(item.product_name) + '</td>' +
                    '<td>₩' + Number(item.price_per_unit).toFixed(2) + '</td>' +
                    '<td>' + Number(item.quantity).toFixed(2) + '</td>' +
                    '<td>₩' + Number(item.total_price).toFixed(2) + '</td>' +
                '</tr>';
            });
        }

        $('#orderDetailsBody').html(rows);
        $('#orderDetailsModal').modal('show');
    });
});

function loadDashboard() {
    $.when(
        $.getJSON(orderListApiUrl),
        $.getJSON(productListApiUrl)
    ).done(function (ordersResponse, productsResponse) {
        var orders = ordersResponse[0] || [];
        var products = productsResponse[0] || [];

        $("#totalOrders").text(orders.length);
        $("#totalProducts").text(products.length);

        var totalRevenue = 0.0;
        var latestOrder = '—';
        var rows = '';

        if (orders.length) {
            latestOrder = orders[0].order_id;
        }

        $.each(orders, function (index, order) {
            totalRevenue += parseFloat(order.total) || 0;
            orderCache[order.order_id] = order;
            rows += '<tr>' +
                '<td>' + escapeHtml(order.datetime) + '</td>' +
                '<td>#' + escapeHtml(order.order_id) + '</td>' +
                '<td>' + escapeHtml(order.customer_name) + '</td>' +
                '<td>₩' + Number(order.total).toFixed(2) + '</td>' +
                '<td><button type="button" class="btn btn-sm btn-outline-green view-order-btn" data-order-id="' + order.order_id + '">View</button></td>' +
            '</tr>';
        });

        if (!orders.length) {
            rows = '<tr><td colspan="5" class="no-data">No orders available yet</td></tr>';
        }

        $("#ordersTableBody").html(rows);
        $("#totalRevenue").text("₩" + totalRevenue.toFixed(2));
        $("#latestOrder").text(latestOrder);
    }).fail(function () {
        $("#ordersTableBody").html('<tr><td colspan="5" class="no-data">Unable to load dashboard data</td></tr>');
    });
}
