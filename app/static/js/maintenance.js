/**
 * Facility Repair & Maintenance Controller
 */
document.addEventListener('DOMContentLoaded', loadMaintenanceRequests);

async function loadMaintenanceRequests() {
  const tableBody = document.getElementById('maintenance-table-body');
  try {
    const res = await ApiClient.get('/api/maintenance');
    const requests = res.data || [];

    if (requests.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="9" class="empty-state">No facility repair requests logged.</td></tr>';
      return;
    }

    tableBody.innerHTML = '';
    requests.forEach(r => {
      const isPending = (r.status !== 'completed');
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.request_id}</td>
        <td style="font-weight: 600;">${r.room_number}</td>
        <td>${r.hostel_name}</td>
        <td><span class="badge badge-neutral">${r.category}</span></td>
        <td><span class="badge ${r.priority === 'urgent' || r.priority === 'high' ? 'badge-danger' : 'badge-info'}">${r.priority}</span></td>
        <td><span class="badge ${isPending ? 'badge-warning' : 'badge-success'}">${r.status}</span></td>
        <td>₹${(r.cost || 0).toLocaleString()}</td>
        <td>${r.reported_at}</td>
        <td>
          ${isPending ? `<button class="btn btn-secondary" onclick="completeMaintenance(${r.request_id})" style="padding: 2px 8px; font-size: 11px;">Mark Completed</button>` : '--'}
        </td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="9" class="error-state">Failed to load maintenance requests: ${err.message}</td></tr>`;
  }
}

function openMaintenanceModal() { document.getElementById('maint-modal').classList.add('active'); }
function closeMaintenanceModal() { document.getElementById('maint-modal').classList.remove('active'); }

document.getElementById('maint-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    room_id: parseInt(document.getElementById('mnt_room_id').value),
    category: document.getElementById('mnt_category').value.trim(),
    description: document.getElementById('mnt_description').value.trim(),
    priority: document.getElementById('mnt_priority').value
  };

  try {
    await ApiClient.post('/api/maintenance', payload);
    ApiClient.showToast('Repair request created successfully!', 'success');
    closeMaintenanceModal();
    loadMaintenanceRequests();
  } catch (err) {
    ApiClient.showToast(err.message || 'Failed to create request.', 'error');
  }
});

async function completeMaintenance(requestId) {
  try {
    await ApiClient.patch(`/api/maintenance/${requestId}/status`, {
      status: 'completed',
      cost: 500.00
    });
    ApiClient.showToast('Maintenance request marked completed!', 'success');
    loadMaintenanceRequests();
  } catch (err) {
    ApiClient.showToast(err.message || 'Failed to update maintenance request.', 'error');
  }
}
