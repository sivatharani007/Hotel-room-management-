/**
 * GrandStay Hotel Room Management System
 * Reports & Analytics Chart.js Visualizations
 */

document.addEventListener('DOMContentLoaded', () => {
  loadReportsAnalytics();
});

async function loadReportsAnalytics() {
  try {
    const res = await fetch('/reports/api/charts');
    const data = await res.json();

    if (!data.success) return;

    // 1. Revenue Analytics Chart
    const revCtx = document.getElementById('reportRevenueChart');
    if (revCtx) {
      new Chart(revCtx, {
        type: 'bar',
        data: {
          labels: data.revenue.labels,
          datasets: [{
            label: 'Monthly Revenue ($)',
            data: data.revenue.data,
            backgroundColor: '#2563eb',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { callback: v => '$' + v.toLocaleString() }
            }
          }
        }
      });
    }

    // 2. Booking Volume Trends
    const trendsCtx = document.getElementById('reportTrendsChart');
    if (trendsCtx) {
      new Chart(trendsCtx, {
        type: 'line',
        data: {
          labels: data.trends.labels,
          datasets: [{
            label: 'Monthly Bookings',
            data: data.trends.data,
            borderColor: '#0d9488',
            backgroundColor: 'rgba(13, 148, 136, 0.1)',
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 1, precision: 0 } }
          }
        }
      });
    }

    // 3. Popular Room Types (Horizontal Bar)
    const typesCtx = document.getElementById('reportTypesChart');
    if (typesCtx) {
      new Chart(typesCtx, {
        type: 'bar',
        indexAxis: 'y',
        data: {
          labels: data.popular_types.labels,
          datasets: [{
            label: 'Total Times Booked',
            data: data.popular_types.data,
            backgroundColor: ['#2563eb', '#0d9488', '#f59e0b', '#8b5cf6'],
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { beginAtZero: true, ticks: { stepSize: 1, precision: 0 } }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    // 4. Room Status Distribution
    const statusCtx = document.getElementById('reportStatusChart');
    if (statusCtx) {
      new Chart(statusCtx, {
        type: 'doughnut',
        data: {
          labels: data.room_status.labels,
          datasets: [{
            data: data.room_status.data,
            backgroundColor: ['#10b981', '#ef4444', '#f97316'],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      });
    }

  } catch (err) {
    console.error("Error loading analytics:", err);
  }
}
