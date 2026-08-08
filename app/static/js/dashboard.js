/**
 * HostelFlow Main Dashboard Controller
 */
document.addEventListener('DOMContentLoaded', async () => {
  const tableBody = document.getElementById('summary-table-body');

  try {
    const res = await ApiClient.get('/api/reports/hostel-summary');
    const data = res.data || [];

    if (data.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">No hostel operational summary data available.</td></tr>';
      return;
    }

    let totalBeds = 0;
    let totalOccupied = 0;
    let totalDues = 0;
    let totalComplaints = 0;
    let totalMaintenance = 0;

    tableBody.innerHTML = '';
    data.forEach(h => {
      totalBeds += h.total_beds || 0;
      totalOccupied += h.occupied_beds || 0;
      totalDues += h.total_outstanding_dues || 0;
      totalComplaints += h.unresolved_complaints_count || 0;
      totalMaintenance += h.pending_maintenance_count || 0;

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-weight: 600;">${h.hostel_name}</td>
        <td><span class="badge badge-neutral">${h.gender_type}</span></td>
        <td>${h.total_beds}</td>
        <td>${h.occupied_beds}</td>
        <td><span class="badge ${h.occupancy_pct >= 85 ? 'badge-success' : 'badge-warning'}">${h.occupancy_pct}%</span></td>
        <td>₹${(h.total_outstanding_dues || 0).toLocaleString()}</td>
        <td><span class="badge ${h.unresolved_complaints_count > 0 ? 'badge-danger' : 'badge-success'}">${h.unresolved_complaints_count}</span></td>
        <td><span class="badge ${h.pending_maintenance_count > 0 ? 'badge-warning' : 'badge-success'}">${h.pending_maintenance_count}</span></td>
      `;
      tableBody.appendChild(tr);
    });

    // Populate KPI Stat Cards
    const overallOccupancy = totalBeds > 0 ? ((totalOccupied / totalBeds) * 100).toFixed(1) : 0;
    document.getElementById('kpi-total-beds').textContent = totalBeds;
    document.getElementById('kpi-occupied-beds').textContent = `${totalOccupied} Occupied`;
    document.getElementById('kpi-occupancy-rate').textContent = `${overallOccupancy}%`;
    document.getElementById('kpi-vacant-beds').textContent = `${totalBeds - totalOccupied} Vacant`;
    document.getElementById('kpi-outstanding-fees').textContent = `₹${totalDues.toLocaleString()}`;
    document.getElementById('kpi-unresolved-issues').textContent = totalComplaints + totalMaintenance;
    document.getElementById('kpi-pending-maint').textContent = `${totalComplaints} Complaints / ${totalMaintenance} Maint`;

  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="8" class="error-state">Failed to load dashboard data: ${err.message}</td></tr>`;
  }
});
