/**
 * HostelFlow Authentication & RBAC UI Visibility Manager
 */
const AuthHelper = {
  currentUser: null,

  async init() {
    try {
      const res = await ApiClient.get('/api/auth/me');
      this.currentUser = res.data;
      this.applyRBACNavigation();
      this.updateHeaderProfile();
    } catch (err) {
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
  },

  hasRole(roleName) {
    if (!this.currentUser || !this.currentUser.roles) return false;
    const target = roleName.toLowerCase();
    return this.currentUser.roles.some(r => {
      const rLower = r.toLowerCase();
      if (rLower === target) return true;
      if (target === 'admin' && rLower === 'administrator') return true;
      if (target === 'warden' && rLower === 'hostel manager') return true;
      return false;
    });
  },

  applyRBACNavigation() {
    if (!this.currentUser) return;
    const navItems = document.querySelectorAll('.nav-item[data-roles]');
    navItems.forEach(item => {
      const allowedRoles = item.getAttribute('data-roles').split(',').map(r => r.trim());
      const hasPermission = allowedRoles.some(r => this.hasRole(r));
      if (!hasPermission) {
        item.style.display = 'none';
      } else {
        item.style.display = 'flex';
      }
    });
  },

  updateHeaderProfile() {
    if (!this.currentUser) return;
    const usernameEl = document.getElementById('header-username');
    const roleBadgeEl = document.getElementById('header-role-badge');
    if (usernameEl) usernameEl.textContent = this.currentUser.username;
    if (roleBadgeEl && this.currentUser.roles.length > 0) {
      roleBadgeEl.textContent = this.currentUser.roles[0];
    }
  },

  async logout() {
    try {
      await ApiClient.post('/api/auth/logout', {});
      ApiClient.showToast('Logged out successfully.', 'info');
      setTimeout(() => { window.location.href = '/login'; }, 500);
    } catch (err) {
      window.location.href = '/login';
    }
  }
};
