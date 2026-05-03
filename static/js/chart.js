(function () {
  'use strict';

  var chartData = window.CHART_DATA;
  if (!chartData || typeof Chart === 'undefined') return;

  Chart.defaults.color = '#8b949e';
  Chart.defaults.borderColor = '#30363d';
  Chart.defaults.font.family = "'Geist', system-ui, sans-serif";

  // Plugin HARUS didaftarkan sebelum chart dibuat
  Chart.register({
    id: 'centerText',
    afterDraw: function (chart) {
      if (chart.canvas.id !== 'progress-chart') return;
      var ctx = chart.ctx;
      var cx = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
      var cy = chart.chartArea.top  + (chart.chartArea.bottom - chart.chartArea.top) / 2;
      ctx.save();
      ctx.font = 'bold 32px Geist Mono, monospace';
      ctx.fillStyle = '#e6edf3';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(chartData.progress + '%', cx, cy - 10);
      ctx.font = '12px Geist, system-ui';
      ctx.fillStyle = '#8b949e';
      ctx.letterSpacing = '0.05em';
      ctx.fillText('PROGRESS FISIK', cx, cy + 18);
      ctx.restore();
    },
  });

  // --- Progress Donut ---
  var progressCanvas = document.getElementById('progress-chart');
  var progressChart = null;
  if (progressCanvas) {
    var pct = Math.max(0, Math.min(100, chartData.progress || 0));
    progressChart = new Chart(progressCanvas, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [pct, 100 - pct],
          backgroundColor: [
            pct >= 80 ? '#3fb950' : pct >= 50 ? '#22d3ee' : pct >= 25 ? '#d29922' : '#f85149',
            '#1e2d3d',
          ],
          borderWidth: 0,
          hoverOffset: 0,
        }],
      },
      options: {
        cutout: '78%',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false },
        },
        animation: { duration: 900, easing: 'easeInOutQuart' },
      },
    });
  }

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
      progressChart.update();
    });
  }

  function formatRp(n) {
    if (!n) return '0';
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }
  window.formatRp = formatRp;
})();
