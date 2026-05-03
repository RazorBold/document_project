(function () {
  'use strict';

  if (!window.appSocket) return;

  window.appSocket.on('progress_update', function (data) {
    var card = document.querySelector('.project-card[data-id="' + data.project_id + '"]');
    if (!card) return;
    var bar = card.querySelector('.progress-bar');
    var val = card.querySelector('.progress-val');
    if (bar) bar.style.width = data.progress + '%';
    if (val) val.textContent = data.progress + '%';
  });

  window.appSocket.on('activity_added', function (data) {
    var tbody = document.getElementById('recent-activity-list');
    if (!tbody) return;
    var tr = document.createElement('tr');
    tr.innerHTML =
      '<td>' + (data.project_judul || '—') + '</td>' +
      '<td>' + (data.nama || '—') + '</td>' +
      '<td>' + (data.tanggal || '—') + '</td>' +
      '<td>' + (data.pelaksana || '—') + '</td>' +
      '<td><span class="badge badge-' + (data.status || 'pending') + '">' +
        capitalize(data.status || 'pending') + '</span></td>';
    tbody.insertBefore(tr, tbody.firstChild);
    // keep max 10 rows
    while (tbody.rows.length > 10) tbody.deleteRow(tbody.rows.length - 1);
  });

  function capitalize(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
  }
})();
