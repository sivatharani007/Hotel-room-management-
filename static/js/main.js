/**
 * GrandStay Hotel Room Management System
 * Global JavaScript Utilities & Handlers
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileSidebar();
  initModals();
  initAlertDismissals();
  initQuickBookingButtons();
});

/**
 * Mobile Sidebar Toggle & Backdrop
 */
function initMobileSidebar() {
  const toggleBtn = document.getElementById('mobileSidebarToggle');
  const sidebar = document.getElementById('appSidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('mobile-open');
    });

    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
        sidebar.classList.remove('mobile-open');
      }
    });
  }
}

/**
 * Modal Handling System
 */
function initModals() {
  // Close modals on overlay click
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        closeModal(overlay.id);
      }
    });
  });

  // Close modals on ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const activeModal = document.querySelector('.modal-overlay.active');
      if (activeModal) {
        closeModal(activeModal.id);
      }
    }
  });

  // Modal close buttons
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-close-modal');
      closeModal(modalId);
    });
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

/**
 * Flash alert auto-dismiss or manual dismiss
 */
function initAlertDismissals() {
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });
}

/**
 * Quick New Booking Trigger Button
 */
function initQuickBookingButtons() {
  document.querySelectorAll('[data-trigger-booking]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      // Check if on bookings page with modal or redirect to /bookings
      const bookingModal = document.getElementById('newBookingModal');
      if (bookingModal) {
        openModal('newBookingModal');
      } else {
        window.location.href = '/bookings?open=new';
      }
    });
  });
}

/**
 * Format Currency Helper
 */
function formatCurrency(amount, currencySymbol = '$') {
  const num = parseFloat(amount || 0);
  return `${currencySymbol}${num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/**
 * Dynamic Toast Notification Dispatcher
 */
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `alert alert-${type}`;
  toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
  toast.style.marginBottom = '0.5rem';

  const iconMap = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle'
  };

  toast.innerHTML = `
    <i class="fas ${iconMap[type] || 'fa-info-circle'} alert-icon"></i>
    <span>${message}</span>
    <button type="button" class="alert-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 250);
    }
  }, 4500);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toastContainer';
  container.style.position = 'fixed';
  container.style.top = '20px';
  container.style.right = '20px';
  container.style.zIndex = '9999';
  container.style.maxWidth = '380px';
  document.body.appendChild(container);
  return container;
}
