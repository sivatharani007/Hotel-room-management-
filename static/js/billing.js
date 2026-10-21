/**
 * GrandStay Hotel Room Management System
 * Billing & Payment Interactive Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  initBillingHandlers();
});

function initBillingHandlers() {
  // Mark Bill As Paid Modal Trigger
  document.querySelectorAll('[data-pay-bill]').forEach(btn => {
    btn.addEventListener('click', () => {
      const paymentId = btn.getAttribute('data-pay-bill');
      const bookingCode = btn.getAttribute('data-booking-code');
      const amount = btn.getAttribute('data-amount');
      const customer = btn.getAttribute('data-customer');

      const form = document.getElementById('markPaidForm');
      if (form) {
        form.action = `/billing/${paymentId}/pay`;
        document.getElementById('pay_booking_code').textContent = bookingCode;
        document.getElementById('pay_customer_name').textContent = customer;
        document.getElementById('pay_amount_display').textContent = `$${parseFloat(amount).toFixed(2)}`;
        openModal('markPaidModal');
      }
    });
  });

  // Direct Print Invoice Trigger
  document.querySelectorAll('[data-print-invoice]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const url = btn.getAttribute('href');
      const printWindow = window.open(url, '_blank');
      printWindow.onload = () => {
        printWindow.print();
      };
    });
  });
}
