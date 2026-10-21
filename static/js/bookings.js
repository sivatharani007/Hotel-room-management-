/**
 * GrandStay Hotel Room Management System
 * Booking Wizard, Cancellation & Check-out Handlers
 */

let selectedRoom = null;
let currentCalculation = { nights: 0, price: 0, total: 0 };

document.addEventListener('DOMContentLoaded', () => {
  initBookingWizard();
  initCancelModal();
  initCheckoutModal();
  initCodeQuickSearch();

  // Check URL param ?open=new
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('open') === 'new') {
    openModal('newBookingModal');
  }
});

/**
 * 11-Step Interactive Booking Wizard
 */
function initBookingWizard() {
  const checkInInput = document.getElementById('book_check_in');
  const checkOutInput = document.getElementById('book_check_out');
  const guestsSelect = document.getElementById('book_guests');
  const roomTypeFilter = document.getElementById('book_room_type_filter');
  const roomsContainer = document.getElementById('availableRoomsGrid');
  const bookingForm = document.getElementById('newBookingForm');

  if (!checkInInput || !checkOutInput) return;

  // Set min check-in to today
  const today = new Date().toISOString().split('T')[0];
  checkInInput.min = today;
  if (!checkInInput.value) {
    checkInInput.value = today;
  }

  // Set tomorrow as default check-out
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const tomorrowStr = tomorrow.toISOString().split('T')[0];
  checkOutInput.min = tomorrowStr;
  if (!checkOutInput.value) {
    checkOutInput.value = tomorrowStr;
  }

  // Re-fetch rooms when dates or guest count change
  const triggerAvailabilityCheck = () => {
    // Ensure check-out is after check-in
    if (checkInInput.value && checkOutInput.value) {
      if (checkOutInput.value <= checkInInput.value) {
        const nextDay = new Date(checkInInput.value);
        nextDay.setDate(nextDay.getDate() + 1);
        checkOutInput.value = nextDay.toISOString().split('T')[0];
      }
      fetchAvailableRooms();
    }
  };

  checkInInput.addEventListener('change', triggerAvailabilityCheck);
  checkOutInput.addEventListener('change', triggerAvailabilityCheck);
  if (guestsSelect) guestsSelect.addEventListener('change', triggerAvailabilityCheck);
  if (roomTypeFilter) roomTypeFilter.addEventListener('change', triggerAvailabilityCheck);

  // Initial fetch
  fetchAvailableRooms();

  // Wizard Tab Navigation (Step 1: Details -> Step 2: Confirmation)
  const btnNext = document.getElementById('btnWizardNext');
  const btnBack = document.getElementById('btnWizardBack');
  const step1 = document.getElementById('wizardStep1');
  const step2 = document.getElementById('wizardStep2');

  if (btnNext && btnBack && step1 && step2) {
    btnNext.addEventListener('click', () => {
      // Validate customer and room selection
      const custId = document.getElementById('book_customer_id').value;
      const roomId = document.getElementById('book_selected_room_id').value;

      if (!custId) {
        showToast('Please select a customer or register a new one.', 'warning');
        return;
      }
      if (!roomId || !selectedRoom) {
        showToast('Please select an available room from the list.', 'warning');
        return;
      }

      // Populate summary step 2
      populateBookingSummary();

      step1.style.display = 'none';
      step2.style.display = 'block';
      document.getElementById('stepPill1').classList.remove('active');
      document.getElementById('stepPill1').classList.add('completed');
      document.getElementById('stepPill2').classList.add('active');
    });

    btnBack.addEventListener('click', () => {
      step2.style.display = 'none';
      step1.style.display = 'block';
      document.getElementById('stepPill2').classList.remove('active');
      document.getElementById('stepPill1').classList.remove('completed');
      document.getElementById('stepPill1').classList.add('active');
    });
  }

  // Handle Form Submission with AJAX
  if (bookingForm) {
    bookingForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('btnConfirmBooking');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Confirming Reservation...';

      const formData = new FormData(bookingForm);
      formData.append('ajax', '1');

      try {
        const res = await fetch('/bookings/create', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();

        if (data.success) {
          showToast(`Reservation Confirmed! Reference: ${data.booking.booking_code}`, 'success');
          closeModal('newBookingModal');
          setTimeout(() => {
            window.location.href = data.redirect_url || '/bookings';
          }, 1200);
        } else {
          showToast(data.message || 'Booking failed.', 'error');
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fas fa-check"></i> Complete &amp; Save Booking';
        }
      } catch (err) {
        showToast('Server communication error during booking.', 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-check"></i> Complete &amp; Save Booking';
      }
    });
  }

  // Quick Customer Registration inside Booking Wizard
  const quickCustForm = document.getElementById('quickAddCustomerForm');
  if (quickCustForm) {
    quickCustForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(quickCustForm);
      formData.append('ajax', '1');

      try {
        const res = await fetch('/customers/add', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Customer ${data.customer.full_name} added!`, 'success');
          // Add to select dropdown
          const custSelect = document.getElementById('book_customer_id');
          const opt = document.createElement('option');
          opt.value = data.customer.id;
          opt.textContent = `${data.customer.full_name} (${data.customer.phone})`;
          opt.selected = true;
          custSelect.appendChild(opt);

          closeModal('quickCustomerModal');
          quickCustForm.reset();
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Error registering customer.', 'error');
      }
    });
  }
}

/**
 * Fetch and Render Available Rooms for Selected Dates
 */
async function fetchAvailableRooms() {
  const checkIn = document.getElementById('book_check_in').value;
  const checkOut = document.getElementById('book_check_out').value;
  const guests = document.getElementById('book_guests')?.value || 1;
  const roomType = document.getElementById('book_room_type_filter')?.value || 'ALL';
  const container = document.getElementById('availableRoomsGrid');

  if (!container || !checkIn || !checkOut) return;

  container.innerHTML = `
    <div style="grid-column: 1/-1; text-align: center; padding: 1.5rem; color: #94a3b8;">
      <i class="fas fa-spinner fa-spin" style="font-size: 1.5rem;"></i>
      <p style="margin-top: 0.5rem;">Checking room availability in database...</p>
    </div>
  `;

  try {
    const res = await fetch(`/rooms/api/available?check_in=${checkIn}&check_out=${checkOut}&guests=${guests}&room_type=${roomType}`);
    const data = await res.json();

    if (!data.success || data.rooms.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 2rem; background: #fff7ed; border-radius: 12px; border: 1px dashed #fdba74;">
          <i class="fas fa-bed" style="font-size: 2rem; color: #ea580c; margin-bottom: 0.5rem;"></i>
          <h4 style="color: #9a3412;">No Available Rooms Found</h4>
          <p style="font-size: 0.85rem; color: #c2410c;">No rooms match your requested dates (${checkIn} to ${checkOut}). Try adjusting the dates or guest count.</p>
        </div>
      `;
      selectedRoom = null;
      document.getElementById('book_selected_room_id').value = '';
      return;
    }

    container.innerHTML = '';
    data.rooms.forEach(room => {
      const card = document.createElement('div');
      card.className = 'selectable-room-card';
      card.id = `room-select-${room.id}`;
      card.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.85rem;">
          <div style="width: 40px; height: 40px; border-radius: 8px; background: #eff6ff; color: #2563eb; display: flex; align-items: center; justify-content: center; font-weight: 800;">
            ${room.room_number}
          </div>
          <div>
            <h4 style="font-size: 0.95rem; font-weight: 700; color: #0f172a;">${room.room_type}</h4>
            <span style="font-size: 0.75rem; color: #64748b;"><i class="fas fa-user-friends"></i> Up to ${room.capacity} Guests</span>
          </div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 1.15rem; font-weight: 800; color: #0f172a;">$${parseFloat(room.price_per_night).toFixed(2)}</div>
          <span style="font-size: 0.72rem; color: #94a3b8;">per night</span>
        </div>
      `;

      card.addEventListener('click', () => {
        document.querySelectorAll('.selectable-room-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedRoom = room;
        document.getElementById('book_selected_room_id').value = room.id;
        updateDynamicBillEstimate();
      });

      container.appendChild(card);
    });

    // Auto-select first room
    if (data.rooms.length > 0) {
      container.firstChild.click();
    }
  } catch (err) {
    container.innerHTML = '<div style="color: #ef4444; padding: 1rem;">Failed to load room availability.</div>';
  }
}

/**
 * Calculate Stay Duration & Live Estimate
 */
function updateDynamicBillEstimate() {
  const checkIn = new Date(document.getElementById('book_check_in').value);
  const checkOut = new Date(document.getElementById('book_check_out').value);

  if (!selectedRoom || isNaN(checkIn) || isNaN(checkOut)) return;

  const diffTime = checkOut - checkIn;
  const nights = Math.max(1, Math.round(diffTime / (1000 * 60 * 60 * 24)));
  const price = parseFloat(selectedRoom.price_per_night);
  const total = (nights * price).toFixed(2);

  currentCalculation = { nights, price, total };

  const nightsDisplay = document.getElementById('displayNights');
  const totalDisplay = document.getElementById('displayTotal');
  if (nightsDisplay) nightsDisplay.textContent = `${nights} night${nights > 1 ? 's' : ''}`;
  if (totalDisplay) totalDisplay.textContent = `$${parseFloat(total).toFixed(2)}`;
}

/**
 * Populate Summary Step 2
 */
function populateBookingSummary() {
  const custSelect = document.getElementById('book_customer_id');
  const custText = custSelect.options[custSelect.selectedIndex].text;
  const checkIn = document.getElementById('book_check_in').value;
  const checkOut = document.getElementById('book_check_out').value;
  const guests = document.getElementById('book_guests').value;

  document.getElementById('sumCustomer').textContent = custText;
  document.getElementById('sumDates').textContent = `${checkIn} → ${checkOut} (${currentCalculation.nights} nights)`;
  document.getElementById('sumRoom').textContent = `Room ${selectedRoom.room_number} (${selectedRoom.room_type}) - ${guests} Guest(s)`;
  document.getElementById('sumRate').textContent = `$${currentCalculation.price.toFixed(2)} / night`;
  document.getElementById('sumTotal').textContent = `$${parseFloat(currentCalculation.total).toFixed(2)}`;
}

/**
 * Cancellation Management Handlers
 */
function initCancelModal() {
  document.querySelectorAll('[data-cancel-booking]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const bookingId = btn.getAttribute('data-cancel-booking');
      try {
        const res = await fetch(`/bookings/${bookingId}`);
        const data = await res.json();
        if (data.success) {
          const b = data.booking;
          document.getElementById('cancelBookingForm').action = `/bookings/${b.id}/cancel`;
          document.getElementById('cancel_booking_code').textContent = b.booking_code;
          document.getElementById('cancel_customer_name').textContent = b.customer_name;
          document.getElementById('cancel_room_info').textContent = `Room ${b.room_number} (${b.room_type})`;
          document.getElementById('cancel_dates').textContent = `${b.check_in} to ${b.check_out}`;
          document.getElementById('cancel_amount').textContent = `$${parseFloat(b.total_amount).toFixed(2)}`;

          openModal('cancelBookingModal');
        }
      } catch (err) {
        showToast('Error preparing cancellation.', 'error');
      }
    });
  });
}

/**
 * Check-Out Management Handlers
 */
function initCheckoutModal() {
  document.querySelectorAll('[data-checkout-booking]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const bookingId = btn.getAttribute('data-checkout-booking');
      try {
        const res = await fetch(`/bookings/${bookingId}`);
        const data = await res.json();
        if (data.success) {
          const b = data.booking;
          document.getElementById('checkoutBookingForm').action = `/bookings/${b.id}/checkout`;
          document.getElementById('checkout_booking_code').textContent = b.booking_code;
          document.getElementById('checkout_customer_name').textContent = b.customer_name;
          document.getElementById('checkout_room_info').textContent = `Room ${b.room_number}`;
          document.getElementById('checkout_dates').textContent = `${b.check_in} to ${b.check_out} (${b.total_nights} nights)`;
          document.getElementById('checkout_amount').textContent = `$${parseFloat(b.total_amount).toFixed(2)}`;
          document.getElementById('checkout_payment_status').textContent = b.payment_status || 'Pending';

          openModal('checkoutBookingModal');
        }
      } catch (err) {
        showToast('Error preparing check-out.', 'error');
      }
    });
  });
}

/**
 * Quick Code Search in Header / Bookings page
 */
function initCodeQuickSearch() {
  const searchBtn = document.getElementById('btnSearchBookingCode');
  const codeInput = document.getElementById('searchBookingCodeInput');

  if (searchBtn && codeInput) {
    const performSearch = async () => {
      const code = codeInput.value.trim();
      if (!code) return;

      try {
        const res = await fetch(`/api/bookings/code/${code}`);
        const data = await res.json();
        if (data.success) {
          // Open details modal
          const b = data.booking;
          showToast(`Found reservation for ${b.customer_name}`, 'info');
          // If active, give option to checkout or view
          window.location.href = `/bookings?search=${encodeURIComponent(b.booking_code)}`;
        } else {
          showToast(data.message, 'warning');
        }
      } catch (err) {
        showToast('Booking code search failed.', 'error');
      }
    };

    searchBtn.addEventListener('click', performSearch);
    codeInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        performSearch();
      }
    });
  }
}
