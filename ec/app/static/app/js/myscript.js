$(document).ready(function () {
$('.plus-cart').click(function (e) {
  e.preventDefault();
  const id = $(this).attr('pid');
  const qtyElement = this.parentNode.querySelector('.quantity');

  $.ajax({
    type: 'GET',
    url: '/pluscart/',
    data: { prod_id: id },
    success: function (data) {
      if (qtyElement) qtyElement.innerText = data.quantity;

      const amountEl = document.getElementById('amount');
      const totalEl = document.getElementById('totalamount');

      if (amountEl) amountEl.innerText = `${Number(data.amount).toFixed(2)} DH`;
      if (totalEl) totalEl.innerHTML = `<strong>${Number(data.totalamount).toFixed(2)} DH</strong>`;
    },
    error: function (xhr) {
      console.error('Plus-cart failed:', xhr.status, xhr.responseText);
      if (xhr.status === 401) {
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
      }
    }
  });
});

$('.minus-cart').click(function (e) {
  e.preventDefault();
  const id = $(this).attr('pid');
  const qtyElement = this.parentNode.querySelector('.quantity');

  $.ajax({
    type: 'GET',
    url: '/minuscart/',
    data: { prod_id: id },
    success: function (data) {
      if (qtyElement) {
        if (data.quantity > 0) {
          qtyElement.innerText = data.quantity;
        } else {
          // Reload if item was deleted (quantity became 0)
          location.reload();
        }
      }

      const amountEl = document.getElementById('amount');
      const totalEl = document.getElementById('totalamount');
      if (amountEl) amountEl.innerText = `${Number(data.amount).toFixed(2)} DH`;
      if (totalEl) totalEl.innerHTML = `<strong>${Number(data.totalamount).toFixed(2)} DH</strong>`;

      if (data.empty) location.reload();
    },
    error: function (xhr) {
      console.error('Minus-cart failed:', xhr.status, xhr.responseText);
      if (xhr.status === 401) {
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
      }
    }
  });
});


// Remove item
$(document).on('click', '.remove-cart', function (e) {
  e.preventDefault();

  const id = $(this).data('pid');
  const itemRow = $(this).closest('.row.align-items-start.g-3'); // exact item block

  $.ajax({
    type: 'GET',
    url: '/removecart/',
    data: { prod_id: id },
    success: function (data) {
      // ✅ Remove only the clicked item visually
      if (itemRow.length) itemRow.remove();

      // ✅ Update totals
      $('#amount').text(`${Number(data.amount).toFixed(2)} DH`);
      $('#totalamount').html(`<strong>${Number(data.totalamount).toFixed(2)} DH</strong>`);

      // ✅ Reload if cart is now empty
      if (data.empty) location.reload();
    },
    error: function (xhr) {
      console.error('Remove-cart error:', xhr.status, xhr.responseText);
    }
  });
});


});