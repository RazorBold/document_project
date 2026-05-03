(function () {
  'use strict';

  var pid = window.CURRENT_PROJECT_ID;
  var tbody = document.getElementById('activity-tbody');
  var template = document.getElementById('activity-row-template');
  var STATUS_CYCLE = ['pending', 'ongoing', 'selesai'];

  // ── Add row ──
  document.getElementById('add-row-btn').addEventListener('click', function () {
    var clone = template.content.cloneNode(true);
    var tr = clone.querySelector('tr');
    var rowNum = tbody.rows.length + 1;
    tr.querySelector('.row-num').textContent = rowNum;
    tbody.appendChild(clone);
    tr = tbody.lastElementChild;
    wireRow(tr);
    tr.querySelector('input[name="nama"]').focus();
  });

  // Wire up existing rows
  Array.prototype.forEach.call(tbody.rows, wireRow);

  function wireRow(tr) {
    // Duration auto-calc
    var mulaiInput = tr.querySelector('input[name="jam_mulai"]');
    var selesaiInput = tr.querySelector('input[name="jam_selesai"]');
    if (mulaiInput) mulaiInput.addEventListener('input', function () { calcDurasi(tr); });
    if (selesaiInput) selesaiInput.addEventListener('input', function () { calcDurasi(tr); });

    // Blur to save
    tr.querySelectorAll('.act-input').forEach(function (inp) {
      inp.addEventListener('blur', function () { saveRow(tr); });
    });

    // Status badge cycle
    var badge = tr.querySelector('.status-badge');
    if (badge) {
      badge.addEventListener('click', function () {
        var cur = badge.dataset.status || 'pending';
        var idx = STATUS_CYCLE.indexOf(cur);
        var next = STATUS_CYCLE[(idx + 1) % STATUS_CYCLE.length];
        badge.dataset.status = next;
        badge.className = 'badge badge-' + next + ' badge-clickable status-badge';
        badge.textContent = capitalize(next);
        var id = tr.dataset.id;
        if (id) {
          fetch('/activities/' + id + '/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: next }),
          });
        }
      });
    }

    // Delete
    var delBtn = tr.querySelector('.delete-row-btn');
    if (delBtn) {
      delBtn.addEventListener('click', function () {
        if (!confirm('Hapus baris ini?')) return;
        var id = tr.dataset.id;
        if (id) {
          fetch('/activities/' + id + '/delete', { method: 'POST' }).then(function () {
            tr.remove();
            renumber();
            window.showToast && window.showToast('Baris dihapus', 'warning');
          });
        } else {
          tr.remove();
          renumber();
        }
      });
    }
  }

  function calcDurasi(tr) {
    var mulai = tr.querySelector('input[name="jam_mulai"]');
    var selesai = tr.querySelector('input[name="jam_selesai"]');
    var cell = tr.querySelector('.durasi-cell');
    if (!mulai || !selesai || !cell) return;
    if (!mulai.value || !selesai.value) { cell.textContent = '—'; return; }
    var start = parseTime(mulai.value);
    var end = parseTime(selesai.value);
    var min = end - start;
    if (min < 0) min += 24 * 60;
    var h = Math.floor(min / 60), m = min % 60;
    cell.textContent = h ? h + 'j ' + m + 'm' : m + 'm';
  }

  function parseTime(t) {
    var parts = t.split(':');
    return parseInt(parts[0]) * 60 + parseInt(parts[1]);
  }

  function saveRow(tr) {
    var id = tr.dataset.id;
    var payload = {};
    tr.querySelectorAll('.act-input[data-field]').forEach(function (inp) {
      payload[inp.dataset.field] = inp.value || null;
    });
    var badge = tr.querySelector('.status-badge');
    if (badge) payload.status = badge.dataset.status || 'pending';

    if (tr.dataset.new === 'true') {
      if (!payload.nama) return;
      fetch('/activities/project/' + pid + '/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).then(function (r) { return r.json(); }).then(function (a) {
        tr.dataset.id = a.id;
        tr.dataset.new = '';
        tr.querySelector('.durasi-cell').textContent = a.durasi_fmt || '—';
        // Wire meeting link
        var meetingBtn = tr.querySelector('.btn-icon:first-child');
        if (meetingBtn && meetingBtn.tagName === 'SPAN') {
          var link = document.createElement('a');
          link.href = '/meeting/activity/' + a.id;
          link.className = 'btn-icon';
          link.title = 'Note Rapat';
          link.textContent = '📋';
          meetingBtn.replaceWith(link);
        }
        window.showToast && window.showToast('Kegiatan disimpan', 'success');
      });
    } else if (id) {
      fetch('/activities/' + id + '/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).then(function (r) { return r.json(); }).then(function (a) {
        tr.querySelector('.durasi-cell').textContent = a.durasi_fmt || '—';
      });
    }
  }

  // Live updates from other users
  if (window.appSocket) {
    window.appSocket.on('activity_updated', function (data) {
      var tr = tbody.querySelector('tr[data-id="' + data.activity_id + '"]');
      if (!tr || !data.changes) return;
      var changes = data.changes;
      var fields = ['nama', 'tanggal', 'jam_mulai', 'jam_selesai', 'pelaksana', 'lokasi', 'output', 'catatan'];
      fields.forEach(function (f) {
        if (changes[f] !== undefined) {
          var inp = tr.querySelector('[data-field="' + f + '"]');
          if (inp) inp.value = changes[f] || '';
        }
      });
      if (changes.durasi_fmt) tr.querySelector('.durasi-cell').textContent = changes.durasi_fmt;
      if (changes.status) {
        var badge = tr.querySelector('.status-badge');
        if (badge) {
          badge.dataset.status = changes.status;
          badge.className = 'badge badge-' + changes.status + ' badge-clickable status-badge';
          badge.textContent = capitalize(changes.status);
        }
      }
    });

    window.appSocket.on('activity_added', function (data) {
      if (tbody.querySelector('tr[data-id="' + data.id + '"]')) return;
      var tr = document.createElement('tr');
      tr.setAttribute('data-id', data.id);
      tr.innerHTML = buildRowHtml(data, tbody.rows.length + 1);
      tbody.appendChild(tr);
      wireRow(tr);
    });
  }

  function buildRowHtml(a, num) {
    return '<td class="row-num">' + num + '</td>' +
      '<td><input class="act-input" data-field="nama" value="' + esc(a.nama) + '"></td>' +
      '<td><input class="act-input" type="date" data-field="tanggal" value="' + (a.tanggal||'') + '"></td>' +
      '<td><input class="act-input" type="time" data-field="jam_mulai" value="' + (a.jam_mulai||'') + '"></td>' +
      '<td><input class="act-input" type="time" data-field="jam_selesai" value="' + (a.jam_selesai||'') + '"></td>' +
      '<td class="durasi-cell row-num">' + (a.durasi_fmt||'—') + '</td>' +
      '<td><input class="act-input" data-field="pelaksana" value="' + esc(a.pelaksana||'') + '"></td>' +
      '<td><input class="act-input" data-field="lokasi" value="' + esc(a.lokasi||'') + '"></td>' +
      '<td><textarea class="act-input" data-field="output" rows="1">' + esc(a.output||'') + '</textarea></td>' +
      '<td><span class="badge badge-' + (a.status||'pending') + ' badge-clickable status-badge" data-status="' + (a.status||'pending') + '">' + capitalize(a.status||'pending') + '</span></td>' +
      '<td><input class="act-input" data-field="catatan" value="' + esc(a.catatan||'') + '"></td>' +
      '<td>' +
        '<a href="/meeting/activity/' + a.id + '" class="btn-icon" title="Note Rapat">📋</a>' +
        '<button class="btn-icon danger delete-row-btn" data-id="' + a.id + '" title="Hapus">✕</button>' +
      '</td>';
  }

  function renumber() {
    Array.prototype.forEach.call(tbody.rows, function (tr, i) {
      var cell = tr.querySelector('.row-num');
      if (cell) cell.textContent = i + 1;
    });
  }

  function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : ''; }
  function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
})();
