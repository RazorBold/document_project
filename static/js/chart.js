(function () {
  'use strict';

  var chartData = window.CHART_DATA;
  if (!chartData || typeof Chart === 'undefined') return;

  Chart.defaults.color = '#8b949e';
  Chart.defaults.borderColor = '#30363d';
  Chart.defaults.font.family = "'Geist', system-ui, sans-serif";

  // Unified centerText plugin — reads options from chart.options.plugins.centerText
  Chart.register({
    id: 'centerText',
    afterDraw: function (chart) {
      var opts = chart.options.plugins && chart.options.plugins.centerText;
      if (!opts || !opts.enabled) return;
      var ctx = chart.ctx;
      var cx = (chart.chartArea.left + chart.chartArea.right) / 2;
      var cy = (chart.chartArea.top  + chart.chartArea.bottom) / 2;
      ctx.save();
      if (opts.top !== undefined) {
        ctx.font = 'bold ' + (opts.topSize || '28px') + ' Geist Mono, monospace';
        ctx.fillStyle = opts.topColor || '#e6edf3';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(String(opts.top), cx, cy - 9);
      }
      if (opts.bottom !== undefined) {
        ctx.font = (opts.bottomSize || '11px') + ' Geist, system-ui';
        ctx.fillStyle = '#8b949e';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(String(opts.bottom), cx, cy + 13);
      }
      ctx.restore();
    },
  });

  function makeDoughnut(canvasId, segments, colors, centerTop, centerBottom, topSize) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    var total = segments.reduce(function (a, b) { return a + b; }, 0);
    return new Chart(canvas, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: total > 0 ? segments : [1],
          backgroundColor: total > 0 ? colors : ['#1e2d3d'],
          borderWidth: 0,
          hoverOffset: 0,
        }],
      },
      options: {
        cutout: '74%',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false },
          centerText: {
            enabled: true,
            top: centerTop,
            bottom: centerBottom,
            topSize: topSize || '26px',
          },
        },
        animation: { duration: 900, easing: 'easeInOutQuart' },
      },
    });
  }

  // --- Progress Donut ---
  var pct = Math.max(0, Math.min(100, chartData.progress || 0));
  var progressColor = pct >= 80 ? '#3fb950' : pct >= 50 ? '#22d3ee' : pct >= 25 ? '#d29922' : '#f85149';
  var progressChart = makeDoughnut(
    'progress-chart',
    [pct, 100 - pct],
    [progressColor, '#1e2d3d'],
    pct + '%', 'PROGRESS FISIK', '32px'
  );

  // --- Activity Status Donut ---
  var actSelesai = chartData.act_selesai || 0;
  var actOngoing = chartData.act_ongoing || 0;
  var actPending = chartData.act_pending || 0;
  var actTotal   = chartData.act_total   || (actSelesai + actOngoing + actPending);
  var actPct     = actTotal > 0 ? Math.round(actSelesai / actTotal * 100) : 0;
  makeDoughnut(
    'activity-status-chart',
    [actSelesai, actOngoing, actPending],
    ['#3fb950', '#22d3ee', '#d29922'],
    actPct + '%', 'KEGIATAN', '24px'
  );

  // --- Milestone Donut ---
  var msSelesai = chartData.ms_selesai || 0;
  var msBelum   = chartData.ms_belum   || 0;
  var msTotal   = chartData.ms_total   || (msSelesai + msBelum);
  makeDoughnut(
    'milestone-chart',
    [msSelesai, msBelum],
    ['#3fb950', '#21262d'],
    msSelesai + '/' + msTotal, 'MILESTONE', '22px'
  );

  // --- Budget Bar ---
  var budgetCanvas = document.getElementById('budget-chart');
  var budgetChart = null;
  if (budgetCanvas && chartData.labels && chartData.labels.length) {
    budgetChart = new Chart(budgetCanvas, {
      type: 'bar',
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: 'Anggaran',
            data: chartData.anggaran,
            backgroundColor: 'rgba(34,211,238,.25)',
            borderColor: '#22d3ee',
            borderWidth: 1.5,
            borderRadius: 6,
          },
          {
            label: 'Realisasi',
            data: chartData.realisasi,
            backgroundColor: 'rgba(63,185,80,.25)',
            borderColor: '#3fb950',
            borderWidth: 1.5,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 10, boxHeight: 10, useBorderRadius: true, borderRadius: 2 },
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ' ' + ctx.dataset.label + ': Rp ' + formatRp(ctx.raw);
              },
            },
          },
        },
        scales: {
          x: { grid: { color: 'rgba(48,54,61,.6)' } },
          y: {
            grid: { color: 'rgba(48,54,61,.6)' },
            ticks: { callback: function (v) { return 'Rp ' + formatRp(v); } },
          },
        },
      },
    });
  }

  // Live updates via socket
  if (window.appSocket) {
    window.appSocket.on('progress_update', function (data) {
      if (!progressChart) return;
      if (String(data.project_id) !== String(window.CURRENT_PROJECT_ID)) return;
      var p = data.progress;
      chartData.progress = p;
      progressChart.data.datasets[0].data = [p, 100 - p];
      progressChart.data.datasets[0].backgroundColor[0] =
        p >= 80 ? '#3fb950' : p >= 50 ? '#22d3ee' : p >= 25 ? '#d29922' : '#f85149';
      progressChart.options.plugins.centerText.top = p + '%';
      progressChart.update();
    });
  }

  function formatRp(n) {
    if (!n) return '0';
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }
  window.formatRp = formatRp;
})();
