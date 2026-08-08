/**
 * Student Directory Controller
 */
document.addEventListener('DOMContentLoaded', loadStudents);

async function loadStudents() {
  const tableBody = document.getElementById('students-table-body');
  try {
    const res = await ApiClient.get('/api/students');
    const students = res.data || [];

    if (students.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="9" class="empty-state">No student records found.</td></tr>';
      return;
    }

    tableBody.innerHTML = '';
    students.forEach(s => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${s.student_id}</td>
        <td style="font-weight: 600;">${s.registration_number}</td>
        <td>${s.full_name}</td>
        <td>${s.email}</td>
        <td>${s.phone}</td>
        <td><span class="badge badge-neutral">${s.department_code}</span></td>
        <td>${s.course_name}</td>
        <td>${s.academic_year}</td>
        <td><span class="badge ${s.status === 'active' ? 'badge-success' : 'badge-danger'}">${s.status}</span></td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="9" class="error-state">Failed to load students: ${err.message}</td></tr>`;
  }
}

function openRegisterModal() {
  document.getElementById('register-modal').classList.add('active');
}

function closeRegisterModal() {
  document.getElementById('register-modal').classList.remove('active');
}

document.getElementById('register-student-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    registration_number: document.getElementById('reg_no').value.trim(),
    first_name: document.getElementById('first_name').value.trim(),
    last_name: document.getElementById('last_name').value.trim(),
    dob: document.getElementById('dob').value,
    gender: document.getElementById('gender').value,
    email: document.getElementById('email').value.trim(),
    phone: document.getElementById('phone').value.trim(),
    department_id: parseInt(document.getElementById('department_id').value),
    course_id: parseInt(document.getElementById('course_id').value),
    academic_year_id: parseInt(document.getElementById('academic_year_id').value)
  };

  try {
    await ApiClient.post('/api/students', payload);
    ApiClient.showToast('Student registered successfully!', 'success');
    closeRegisterModal();
    loadStudents();
  } catch (err) {
    ApiClient.showToast(err.message || 'Registration failed.', 'error');
  }
});
