(function () {
  'use strict';

  var chartData = window.CHART_DATA;
  if (!chartData || typeof Chart === 'undefined') return;

  Chart.defaults.color = '#8b949e';
  Chart.defaults.borderColor = '#30363d';
  Chart.defaults.font.family = "'Geist', system-ui, sans-serif";

  // --- Progress Donut ---
  var progressCanvas = document.getElementById('progress-chart');
  var progressChart = null;
  if (progressCanvas) {
    progressChart = new Chart(progressCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Fisik', 'Sisa'],
        datasets: [{
          data: [chartData.progress, 100 - chartData.progress],
          backgroundColor: ['#22d3ee', '#1c2333'],
          borderWidth: 0,
          hoverOffset: 4,
        }],
      },
      options: {
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (ctx) { return ctx.label + ': ' + ctx.raw + '%'; },
            },
          },
        },
        animation: { duration: 600 },
      },
    });

    // Center text plugin
    Chart.register({
      id: 'centerText',
      afterDraw: function (chart) {
        if (chart.canvas.id !== 'progress-chart') return;
        var ctx = chart.ctx;
        var w = chart.width, h = chart.height;
        ctx.save();
        ctx.font = 'bold 22px Geist Mono, monospace';
        ctx.fillStyle = '#e6edf3';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(chartData.progress + '%', w / 2, h / 2);
        ctx.restore();
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
            backgroundColor: 'rgba(34,211,238,.35)',
            borderColor: '#22d3ee',
            borderWidth: 1,
            borderRadius: 4,
          },
          {
            label: 'Realisasi',
            data: chartData.realisasi,
            backgroundColor: 'rgba(63,185,80,.35)',
            borderColor: '#3fb950',
            borderWidth: 1,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12 } },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ctx.dataset.label + ': Rp ' + formatRp(ctx.raw);
              },
            },
          },
        },
        scales: {
          x: { grid: { color: '#21262d' } },
          y: {
            grid: { color: '#21262d' },
            ticks: {
              callback: function (v) { return 'Rp ' + formatRp(v); },
            },
          },
        },
      },
    });
  }

  // Live updates
  if (window.appSocket) {
    window.appSocket.on('progress_update', function (data) {
      if (!progressChart) return;
      if (String(data.project_id) !== String(window.CURRENT_PROJECT_ID)) return;
      chartData.progress = data.progress;
      progressChart.data.datasets[0].data = [data.progress, 100 - data.progress];
      progressChart.update();
    });

    window.appSocket.on('budget_changed', function (data) {
      if (!budgetChart) return;
      if (String(data.project_id) !== String(window.CURRENT_PROJECT_ID)) return;
      // Reload page to refresh budget chart (full re-query needed for categories)
      setTimeout(function () { window.location.reload(); }, 1500);
    });
  }

  function formatRp(n) {
    if (!n) return '0';
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  window.formatRp = formatRp;
})();
