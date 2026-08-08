/**
 * Allocation Lifecycle Controller
 */
document.addEventListener('DOMContentLoaded', loadAllocations);

async function loadAllocations() {
  const tableBody = document.getElementById('allocations-table-body');
  try {
    const res = await ApiClient.get('/api/allocations');
    const allocs = res.data || [];

    if (allocs.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="9" class="empty-state">No active bed allocations.</td></tr>';
      return;
    }

    tableBody.innerHTML = '';
    allocs.forEach(a => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${a.allocation_id}</td>
        <td style="font-weight: 600;">${a.student_name}</td>
        <td>${a.registration_number}</td>
        <td>${a.hostel_name}</td>
        <td>${a.block_name}</td>
        <td>${a.room_number}</td>
        <td>${a.bed_number}</td>
        <td>${a.start_date}</td>
        <td><span class="badge badge-success">${a.allocation_status}</span></td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="9" class="error-state">Failed to load allocations: ${err.message}</td></tr>`;
  }
}

function openAllocateModal() { document.getElementById('allocate-modal').classList.add('active'); }
function openTransferModal() { document.getElementById('transfer-modal').classList.add('active'); }
function openVacateModal() { document.getElementById('vacate-modal').classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

document.getElementById('allocate-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    student_id: parseInt(document.getElementById('alloc_student_id').value),
    bed_id: parseInt(document.getElementById('alloc_bed_id').value),
    start_date: document.getElementById('alloc_start_date').value
  };

  try {
    await ApiClient.post('/api/allocations', payload);
    ApiClient.showToast('Bed allocated successfully!', 'success');
    closeModal('allocate-modal');
    loadAllocations();
  } catch (err) {
    ApiClient.showToast(err.message || 'Allocation failed.', 'error');
  }
});

document.getElementById('transfer-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    student_id: parseInt(document.getElementById('trans_student_id').value),
    new_bed_id: parseInt(document.getElementById('trans_new_bed_id').value),
    transfer_date: document.getElementById('trans_date').value,
    reason: document.getElementById('trans_reason').value.trim()
  };

  try {
    await ApiClient.post('/api/allocations/transfer', payload);
    ApiClient.showToast('Student transferred successfully!', 'success');
    closeModal('transfer-modal');
    loadAllocations();
  } catch (err) {
    ApiClient.showToast(err.message || 'Transfer failed.', 'error');
  }
});

document.getElementById('vacate-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    student_id: parseInt(document.getElementById('vac_student_id').value),
    vacating_date: document.getElementById('vac_date').value,
    clearance_status: document.getElementById('vac_clearance').value,
    reason: document.getElementById('vac_reason').value.trim()
  };

  try {
    await ApiClient.post('/api/allocations/vacate', payload);
    ApiClient.showToast('Student check-out processed successfully!', 'success');
    closeModal('vacate-modal');
    loadAllocations();
  } catch (err) {
    ApiClient.showToast(err.message || 'Vacate failed.', 'error');
  }
});
