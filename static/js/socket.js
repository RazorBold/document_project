(function () {
  'use strict';

  const socket = io();
  window.appSocket = socket;

  const liveBadge = document.getElementById('live-badge');
  const connStatus = document.getElementById('connection-status');

  socket.on('connect', function () {
    if (liveBadge) liveBadge.classList.remove('hidden');
    if (connStatus) {
      connStatus.textContent = '● Online';
      connStatus.className = 'conn-status online';
    }
    if (window.CURRENT_PROJECT_ID) {
      socket.emit('join_project', { project_id: window.CURRENT_PROJECT_ID });
    }
  });

  socket.on('disconnect', function () {
    if (liveBadge) liveBadge.classList.add('hidden');
    if (connStatus) {
      connStatus.textContent = '● Offline';
      connStatus.className = 'conn-status offline';
    }
  });

  socket.on('notification', function (data) {
    var type = data.type || 'info';
    // Suppress join notifications for cleaner UX
    if (type === 'info' && data.message && data.message.startsWith('Terhubung ke project')) return;
    showToast(data.message, type);
  });

  // Mobile sidebar toggle
  var menuToggle = document.getElementById('menu-toggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', function () {
      document.body.classList.toggle('sidebar-open');
    });
    // Close sidebar on overlay click
    document.addEventListener('click', function (e) {
      if (document.body.classList.contains('sidebar-open') &&
          !document.getElementById('sidebar').contains(e.target) &&
          e.target !== menuToggle) {
        document.body.classList.remove('sidebar-open');
      }
    });
  }

  function showToast(message, type) {
    type = type || 'info';
    var container = document.getElementById('toast-container');
    if (!container) return;
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity .3s';
      setTimeout(function () { toast.remove(); }, 320);
    }, 3800);
  }

  window.showToast = showToast;
})();
