/**
 * GrandStay Hotel Room Management System
 * Dashboard Chart.js Visualizations
 */

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardCharts();
});

async function loadDashboardCharts() {
  try {
    const res = await fetch('/api/dashboard/charts');
    const data = await res.json();

    if (!data.success) {
      console.warn("Chart data unavailable:", data.error);
      return;
    }

    renderOccupancyChart(data.occupancy);
    renderRoomTypesChart(data.room_types);
    renderRevenueChart(data.revenue);
    renderTrendsChart(data.trends);
  } catch (err) {
    console.error("Failed to load dashboard charts:", err);
  }
}

/**
 * 1. Room Occupancy Doughnut Chart
 */
function renderOccupancyChart(occupancy) {
  const ctx = document.getElementById('occupancyChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: occupancy.labels,
      datasets: [{
        data: occupancy.data,
        backgroundColor: [
          '#10b981', // Available (Green)
          '#ef4444', // Occupied (Red)
          '#f97316'  // Maintenance (Orange)
        ],
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: '600' },
            padding: 15
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          padding: 10,
          cornerRadius: 8,
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif" }
        }
      }
    }
  });
}

/**
 * 2. Room Type Distribution Chart
 */
function renderRoomTypesChart(roomTypes) {
  const ctx = document.getElementById('roomTypesChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: roomTypes.labels,
      datasets: [{
        data: roomTypes.data,
        backgroundColor: [
          '#2563eb', // Standard (Royal Blue)
          '#0d9488', // Deluxe (Teal)
          '#f59e0b', // Suite (Gold)
          '#8b5cf6'  // Family Room (Purple)
        ],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: '600' },
            padding: 15
          }
        }
      }
    }
  });
}

/**
 * 3. Monthly Revenue Bar Chart
 */
function renderRevenueChart(revenue) {
  const ctx = document.getElementById('revenueChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: revenue.labels,
      datasets: [{
        label: 'Revenue ($)',
        data: revenue.data,
        backgroundColor: 'rgba(37, 99, 235, 0.85)',
        hoverBackgroundColor: '#2563eb',
        borderRadius: 8,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#f1f5f9' },
          ticks: {
            callback: value => '$' + value.toLocaleString(),
            font: { family: "'Plus Jakarta Sans', sans-serif" }
          }
        },
        x: {
          grid: { display: false },
          ticks: { font: { family: "'Plus Jakarta Sans', sans-serif" } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => ` Revenue: $${context.parsed.y.toLocaleString()}`
          }
        }
      }
    }
  });
}

/**
 * 4. Booking Trends Line Chart
 */
function renderTrendsChart(trends) {
  const ctx = document.getElementById('trendsChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: trends.labels,
      datasets: [{
        label: 'Reservations',
        data: trends.data,
        borderColor: '#0d9488',
        backgroundColor: 'rgba(13, 148, 136, 0.12)',
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#0d9488',
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            precision: 0,
            font: { family: "'Plus Jakarta Sans', sans-serif" }
          },
          grid: { color: '#f1f5f9' }
        },
        x: {
          grid: { display: false },
          ticks: { font: { family: "'Plus Jakarta Sans', sans-serif" } }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}
