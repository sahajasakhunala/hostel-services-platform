/**
 * Visitor Gate Security Controller
 */
document.addEventListener('DOMContentLoaded', loadVisitors);

async function loadVisitors() {
  const tableBody = document.getElementById('visitors-table-body');
  try {
    const res = await ApiClient.get('/api/visitors');
    const visitors = res.data || [];

    if (visitors.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="10" class="empty-state">No gate security visitor logs.</td></tr>';
      return;
    }

    tableBody.innerHTML = '';
    visitors.forEach(v => {
      const isCheckedIn = (v.visitor_status === 'currently_checked_in' || !v.check_out_time);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${v.visitor_id}</td>
        <td style="font-weight: 600;">${v.visitor_name}</td>
        <td>${v.phone}</td>
        <td>${v.student_name}</td>
        <td>${v.registration_number}</td>
        <td>${v.purpose}</td>
        <td>${v.check_in_time}</td>
        <td>${v.check_out_time || '--'}</td>
        <td><span class="badge ${isCheckedIn ? 'badge-warning' : 'badge-neutral'}">${v.visitor_status || (isCheckedIn ? 'checked_in' : 'checked_out')}</span></td>
        <td>
          ${isCheckedIn ? `<button class="btn btn-secondary" onclick="checkoutVisitor(${v.visitor_id})" style="padding: 2px 8px; font-size: 11px;">Check-Out</button>` : '--'}
        </td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="10" class="error-state">Failed to load visitor log: ${err.message}</td></tr>`;
  }
}

function openCheckinModal() { document.getElementById('checkin-modal').classList.add('active'); }
function closeCheckinModal() { document.getElementById('checkin-modal').classList.remove('active'); }

document.getElementById('checkin-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    student_id: parseInt(document.getElementById('vis_student_id').value),
    visitor_name: document.getElementById('vis_name').value.trim(),
    phone: document.getElementById('vis_phone').value.trim(),
    id_type: document.getElementById('vis_id_type').value,
    id_number: document.getElementById('vis_id_number').value.trim(),
    purpose: document.getElementById('vis_purpose').value.trim()
  };

  try {
    await ApiClient.post('/api/visitors', payload);
    ApiClient.showToast('Visitor checked in successfully!', 'success');
    closeCheckinModal();
    loadVisitors();
  } catch (err) {
    ApiClient.showToast(err.message || 'Check-in failed.', 'error');
  }
});

async function checkoutVisitor(visitorId) {
  try {
    await ApiClient.post(`/api/visitors/${visitorId}/checkout`, {});
    ApiClient.showToast('Visitor checked out successfully!', 'success');
    loadVisitors();
  } catch (err) {
    ApiClient.showToast(err.message || 'Check-out failed.', 'error');
  }
}
