/**
 * BI Reports & Analytics Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  loadOccupancyReport();
  loadBlockRankingReport();
  loadFeeRankingReport();
  loadVisitorTrendsReport();
});

async function loadOccupancyReport() {
  const body = document.getElementById('rpt-occupancy-body');
  try {
    const res = await ApiClient.get('/api/reports/occupancy');
    const data = res.data || [];

    if (data.length === 0) {
      body.innerHTML = '<tr><td colspan="6" class="empty-state">No occupancy report data.</td></tr>';
      return;
    }

    body.innerHTML = '';
    data.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: 600;">${r.hostel_name}</td>
        <td><span class="badge badge-neutral">${r.gender_type}</span></td>
        <td>${r.total_beds}</td>
        <td>${r.occupied_beds}</td>
        <td>${r.vacant_beds}</td>
        <td><span class="badge ${r.occupancy_percentage >= 85 ? 'badge-success' : 'badge-warning'}">${r.occupancy_percentage}%</span></td>
      `;
      body.appendChild(tr);
    });
  } catch (err) {
    body.innerHTML = `<tr><td colspan="6" class="error-state">Failed: ${err.message}</td></tr>`;
  }
}

async function loadBlockRankingReport() {
  const body = document.getElementById('rpt-block-rank-body');
  try {
    const res = await ApiClient.get('/api/reports/occupancy/blocks');
    const data = res.data || [];

    if (data.length === 0) {
      body.innerHTML = '<tr><td colspan="5" class="empty-state">No block ranking data.</td></tr>';
      return;
    }

    body.innerHTML = '';
    data.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.hostel_name}</td>
        <td style="font-weight: 600;">${r.block_name}</td>
        <td>${r.total_beds}</td>
        <td>${r.occupancy_percentage}%</td>
        <td><span class="badge badge-info">Rank #${r.block_rank_within_hostel}</span></td>
      `;
      body.appendChild(tr);
    });
  } catch (err) {
    body.innerHTML = `<tr><td colspan="5" class="error-state">Failed: ${err.message}</td></tr>`;
  }
}

async function loadFeeRankingReport() {
  const body = document.getElementById('rpt-fee-rank-body');
  try {
    const res = await ApiClient.get('/api/reports/fees/ranking');
    const data = res.data || [];

    if (data.length === 0) {
      body.innerHTML = '<tr><td colspan="6" class="empty-state">No outstanding fee debtors.</td></tr>';
      return;
    }

    body.innerHTML = '';
    data.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><span class="badge badge-danger">#${r.fee_due_rank}</span></td>
        <td style="font-weight: 600;">${r.student_name}</td>
        <td>${r.registration_number}</td>
        <td>${r.room_type}</td>
        <td style="font-weight: 700; color: var(--danger);">₹${(r.outstanding_balance || 0).toLocaleString()}</td>
        <td>${r.days_overdue} days</td>
      `;
      body.appendChild(tr);
    });
  } catch (err) {
    body.innerHTML = `<tr><td colspan="6" class="error-state">Failed: ${err.message}</td></tr>`;
  }
}

async function loadVisitorTrendsReport() {
  const body = document.getElementById('rpt-visitors-body');
  try {
    const res = await ApiClient.get('/api/reports/visitors');
    const data = res.data || [];

    if (data.length === 0) {
      body.innerHTML = '<tr><td colspan="5" class="empty-state">No visitor trend data.</td></tr>';
      return;
    }

    body.innerHTML = '';
    data.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: 600;">${r.hostel_name}</td>
        <td>${r.total_visitors}</td>
        <td><span class="badge badge-warning">${r.currently_checked_in_visitors}</span></td>
        <td><span class="badge badge-success">${r.checked_out_visitors}</span></td>
        <td>${r.avg_visit_duration_minutes || 0} mins</td>
      `;
      body.appendChild(tr);
    });
  } catch (err) {
    body.innerHTML = `<tr><td colspan="5" class="error-state">Failed: ${err.message}</td></tr>`;
  }
}
