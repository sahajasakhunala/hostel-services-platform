/**
 * Finance & Fee Collection Controller
 */
document.addEventListener('DOMContentLoaded', loadFeeDues);

async function loadFeeDues() {
  const tableBody = document.getElementById('finance-table-body');
  try {
    const res = await ApiClient.get('/api/finance/dues');
    const dues = res.data || [];

    if (dues.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="9" class="empty-state">No outstanding fee dues. All resident accounts are clear.</td></tr>';
      return;
    }

    tableBody.innerHTML = '';
    dues.forEach(d => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${d.invoice_id}</td>
        <td style="font-weight: 600;">${d.student_name}</td>
        <td>${d.registration_number}</td>
        <td>${d.room_type}</td>
        <td>₹${(d.total_amount || 0).toLocaleString()}</td>
        <td>₹${(d.paid_amount || 0).toLocaleString()}</td>
        <td style="font-weight: 700; color: var(--danger);">₹${(d.outstanding_balance || 0).toLocaleString()}</td>
        <td>${d.due_date}</td>
        <td><span class="badge ${d.days_overdue > 0 ? 'badge-danger' : 'badge-neutral'}">${d.days_overdue} days</span></td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="9" class="error-state">Failed to load fee dues: ${err.message}</td></tr>`;
  }
}

function openPaymentModal() { document.getElementById('payment-modal').classList.add('active'); }
function closePaymentModal() { document.getElementById('payment-modal').classList.remove('active'); }

document.getElementById('payment-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    invoice_id: parseInt(document.getElementById('pay_invoice_id').value),
    amount: parseFloat(document.getElementById('pay_amount').value),
    payment_method: document.getElementById('pay_method').value,
    receipt_number: document.getElementById('pay_receipt_no').value.trim()
  };

  try {
    await ApiClient.post('/api/finance/payments', payload);
    ApiClient.showToast('Payment processed successfully!', 'success');
    closePaymentModal();
    loadFeeDues();
  } catch (err) {
    ApiClient.showToast(err.message || 'Payment processing failed.', 'error');
  }
});
