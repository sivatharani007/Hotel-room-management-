/**
 * GrandStay Hotel Room Management System
 * Room Management Interactive Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  initViewToggle();
  initRoomModals();
});

/**
 * Toggle between Room Cards Grid and Table View
 */
function initViewToggle() {
  const cardViewBtn = document.getElementById('btnViewCards');
  const tableViewBtn = document.getElementById('btnViewTable');
  const cardsContainer = document.getElementById('roomsCardsView');
  const tableContainer = document.getElementById('roomsTableView');

  if (cardViewBtn && tableViewBtn && cardsContainer && tableContainer) {
    cardViewBtn.addEventListener('click', () => {
      cardViewBtn.classList.add('active', 'btn-primary');
      cardViewBtn.classList.remove('btn-secondary');
      tableViewBtn.classList.remove('active', 'btn-primary');
      tableViewBtn.classList.add('btn-secondary');

      cardsContainer.style.display = 'grid';
      tableContainer.style.display = 'none';
      localStorage.setItem('grandstay_room_view', 'cards');
    });

    tableViewBtn.addEventListener('click', () => {
      tableViewBtn.classList.add('active', 'btn-primary');
      tableViewBtn.classList.remove('btn-secondary');
      cardViewBtn.classList.remove('active', 'btn-primary');
      cardViewBtn.classList.add('btn-secondary');

      cardsContainer.style.display = 'none';
      tableContainer.style.display = 'block';
      localStorage.setItem('grandstay_room_view', 'table');
    });

    // Restore preference
    const saved = localStorage.getItem('grandstay_room_view');
    if (saved === 'table') {
      tableViewBtn.click();
    }
  }
}

/**
 * Room Edit, View, and Delete Modals
 */
function initRoomModals() {
  // Edit Room Button Handlers
  document.querySelectorAll('[data-edit-room]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const roomId = btn.getAttribute('data-edit-room');
      try {
        const res = await fetch(`/rooms/${roomId}`);
        const data = await res.json();
        if (data.success) {
          const room = data.room;
          document.getElementById('editRoomForm').action = `/rooms/edit/${room.id}`;
          document.getElementById('edit_room_number').value = room.room_number;
          document.getElementById('edit_room_type').value = room.room_type;
          document.getElementById('edit_price_per_night').value = room.price_per_night;
          document.getElementById('edit_capacity').value = room.capacity;
          document.getElementById('edit_status').value = room.status;
          document.getElementById('edit_description').value = room.description || '';

          openModal('editRoomModal');
        } else {
          showToast(data.message, 'error');
        }
      } catch (err) {
        showToast('Failed to load room details.', 'error');
      }
    });
  });

  // View Room Details Button Handlers
  document.querySelectorAll('[data-view-room]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const roomId = btn.getAttribute('data-view-room');
      try {
        const res = await fetch(`/rooms/${roomId}`);
        const data = await res.json();
        if (data.success) {
          const room = data.room;
          document.getElementById('view_room_number').textContent = `Room ${room.room_number}`;
          document.getElementById('view_room_type').textContent = room.room_type;
          document.getElementById('view_room_price').textContent = `$${parseFloat(room.price_per_night).toFixed(2)} / night`;
          document.getElementById('view_room_capacity').textContent = `${room.capacity} Guests`;
          document.getElementById('view_room_status').textContent = room.status;
          document.getElementById('view_room_description').textContent = room.description || 'No specific description provided.';

          const statusBadge = document.getElementById('view_room_status_badge');
          if (statusBadge) {
            statusBadge.className = `badge badge-${room.status.toLowerCase()}`;
            statusBadge.innerHTML = `<span class="badge-dot"></span> ${room.status}`;
          }

          openModal('viewRoomModal');
        }
      } catch (err) {
        showToast('Error opening room details', 'error');
      }
    });
  });

  // Delete Room Confirmation
  document.querySelectorAll('[data-delete-room]').forEach(btn => {
    btn.addEventListener('click', () => {
      const roomId = btn.getAttribute('data-delete-room');
      const roomNum = btn.getAttribute('data-room-num');
      const form = document.getElementById('deleteRoomForm');
      if (form) {
        form.action = `/rooms/delete/${roomId}`;
        document.getElementById('delete_room_text').textContent = `Are you sure you want to delete Room ${roomNum}? If this room has active or historical bookings, deletion will be safely rejected.`;
        openModal('deleteRoomModal');
      }
    });
  });
}
