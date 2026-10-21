/**
 * GrandStay Hotel Room Management System
 * Customer Management Interactive Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  initCustomerModals();
});

function initCustomerModals() {
  // Edit Customer
  document.querySelectorAll('[data-edit-customer]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const custId = btn.getAttribute('data-edit-customer');
      try {
        const res = await fetch(`/customers/${custId}`);
        const data = await res.json();
        if (data.success) {
          const c = data.customer;
          document.getElementById('editCustomerForm').action = `/customers/edit/${c.id}`;
          document.getElementById('edit_cust_name').value = c.full_name;
          document.getElementById('edit_cust_phone').value = c.phone;
          document.getElementById('edit_cust_email').value = c.email;
          document.getElementById('edit_cust_id_type').value = c.id_type || 'Passport / National ID';
          document.getElementById('edit_cust_id_number').value = c.id_number || '';
          document.getElementById('edit_cust_address').value = c.address || '';

          openModal('editCustomerModal');
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Failed to load customer profile.', 'error');
      }
    });
  });

  // Customer Booking History Viewer
  document.querySelectorAll('[data-customer-history]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const custId = btn.getAttribute('data-customer-history');
      try {
        const res = await fetch(`/customers/${custId}/history`);
        const data = await res.json();
        if (data.success) {
          document.getElementById('history_customer_name').textContent = data.customer.full_name;
          const tbody = document.getElementById('customerHistoryTableBody');
          tbody.innerHTML = '';

          if (data.bookings.length === 0) {
            tbody.innerHTML = `
              <tr>
                <td colspan="6" class="text-center" style="padding: 2rem; color: #94a3b8;">
                  <i class="fas fa-folder-open" style="font-size: 1.5rem; display: block; margin-bottom: 0.5rem;"></i>
                  No previous reservations found for this customer.
                </td>
              </tr>
            `;
          } else {
            data.bookings.forEach(b => {
              const tr = document.createElement('tr');
              tr.innerHTML = `
                <td><strong>${b.booking_code}</strong></td>
                <td>Room ${b.room_number} (${b.room_type})</td>
                <td>${b.check_in}</td>
                <td>${b.check_out}</td>
                <td><strong>$${parseFloat(b.total_amount).toFixed(2)}</strong></td>
                <td><span class="badge badge-${b.status.toLowerCase()}"><span class="badge-dot"></span> ${b.status}</span></td>
              `;
              tbody.appendChild(tr);
            });
          }

          openModal('customerHistoryModal');
        }
      } catch (err) {
        showToast('Error loading booking history.', 'error');
      }
    });
  });

  // Delete Customer Confirmation
  document.querySelectorAll('[data-delete-customer]').forEach(btn => {
    btn.addEventListener('click', () => {
      const custId = btn.getAttribute('data-delete-customer');
      const custName = btn.getAttribute('data-cust-name');
      const form = document.getElementById('deleteCustomerForm');
      if (form) {
        form.action = `/customers/delete/${custId}`;
        document.getElementById('delete_cust_text').textContent = `Are you sure you want to delete customer "${custName}"? If bookings are linked, deletion will be safely rejected.`;
        openModal('deleteCustomerModal');
      }
    });
  });
}
