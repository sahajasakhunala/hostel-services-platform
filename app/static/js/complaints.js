/**
 * Grievance Complaints Controller
 */
document.addEventListener('DOMContentLoaded', loadComplaints);

async function loadComplaints() {
  const tableBody = document.getElementById('complaints-table-body');
  try {
    const res = await ApiClient.get('/api/complaints');
    const complaints = res.data || [];

    if (complaints.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">No student complaints filed.</td></tr>';
      return;
    }

    tableBody.innerHTML = '';
    complaints.forEach(c => {
      const isUnresolved = (c.status === 'open' || c.status === 'in_progress');
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${c.complaint_id}</td>
        <td>${c.student_name}</td>
        <td><span class="badge badge-neutral">${c.category_name}</span></td>
        <td style="font-weight: 600;">${c.subject}</td>
        <td><span class="badge ${c.priority === 'urgent' || c.priority === 'high' ? 'badge-danger' : 'badge-info'}">${c.priority}</span></td>
        <td><span class="badge ${isUnresolved ? 'badge-warning' : 'badge-success'}">${c.status}</span></td>
        <td>${c.filed_at}</td>
        <td>
          ${isUnresolved ? `<button class="btn btn-secondary" onclick="resolveComplaint(${c.complaint_id})" style="padding: 2px 8px; font-size: 11px;">Mark Resolved</button>` : '--'}
        </td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="8" class="error-state">Failed to load complaints: ${err.message}</td></tr>`;
  }
}

function openComplaintModal() { document.getElementById('complaint-modal').classList.add('active'); }
function closeComplaintModal() { document.getElementById('complaint-modal').classList.remove('active'); }

document.getElementById('complaint-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    student_id: parseInt(document.getElementById('cmp_student_id').value),
    category_id: parseInt(document.getElementById('cmp_category_id').value),
    subject: document.getElementById('cmp_subject').value.trim(),
    description: document.getElementById('cmp_description').value.trim(),
    priority: document.getElementById('cmp_priority').value
  };

  try {
    await ApiClient.post('/api/complaints', payload);
    ApiClient.showToast('Complaint filed successfully!', 'success');
    closeComplaintModal();
    loadComplaints();
  } catch (err) {
    ApiClient.showToast(err.message || 'Failed to file complaint.', 'error');
  }
});

async function resolveComplaint(complaintId) {
  try {
    await ApiClient.patch(`/api/complaints/${complaintId}/status`, {
      status: 'resolved',
      resolution_notes: 'Resolved by warden/staff via administration portal.'
    });
    ApiClient.showToast('Complaint marked as resolved!', 'success');
    loadComplaints();
  } catch (err) {
    ApiClient.showToast(err.message || 'Failed to update complaint.', 'error');
  }
}
