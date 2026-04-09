const integer = new Intl.NumberFormat("ru-RU");
let chart;

function renderStat(id, value) {
  document.getElementById(id).textContent = value;
}

function formatMoney(value) {
  return `${integer.format(Math.round(value))} ₸`;
}

function renderBarWidth(value, maxValue) {
  if (!maxValue) return 0;
  return Math.max(8, Math.round((value / maxValue) * 100));
}

function formatShortDate(value) {
  return new Date(value).toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
  });
}

function condenseDaily(daily) {
  if (daily.length <= 14) {
    return daily.map((item) => ({
      label: formatShortDate(item.date),
      orders: item.orders,
      revenue: item.revenue,
    }));
  }

  const bucketSize = Math.ceil(daily.length / 10);
  const buckets = [];

  for (let index = 0; index < daily.length; index += bucketSize) {
    const chunk = daily.slice(index, index + bucketSize);
    const first = chunk[0];
    const last = chunk[chunk.length - 1];

    buckets.push({
      label: `${formatShortDate(first.date)} - ${formatShortDate(last.date)}`,
      orders: chunk.reduce((sum, item) => sum + item.orders, 0),
      revenue: chunk.reduce((sum, item) => sum + item.revenue, 0),
    });
  }

  return buckets;
}

function renderTable(targetId, rows, labelKey) {
  const target = document.getElementById(targetId);
  if (!rows.length) {
    target.innerHTML = '<div class="state">Данные пока не загружены.</div>';
    return;
  }

  const maxRevenue = Math.max(...rows.map((row) => row.revenue), 0);

  target.innerHTML = rows
    .slice(0, 6)
    .map(
      (row) => `
        <div class="table-row">
          <div class="table-copy">
            <strong title="${row[labelKey]}">${row[labelKey]}</strong>
            <span>${integer.format(Math.round(row.revenue))} ₸</span>
            <div class="table-bar">
              <div class="table-bar-fill" style="width: ${renderBarWidth(row.revenue, maxRevenue)}%"></div>
            </div>
          </div>
          <div class="table-value">${formatMoney(row.revenue)}</div>
        </div>
      `,
    )
    .join("");
}

function renderChart(daily) {
  const ctx = document.getElementById("ordersChart");
  if (chart) chart.destroy();
  const series = condenseDaily(daily);

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: series.map((item) => item.label),
      datasets: [
        {
          type: "line",
          label: "Заказы",
          data: series.map((item) => item.orders),
          borderColor: "#a5b8ff",
          backgroundColor: "rgba(165, 184, 255, 0.16)",
          yAxisID: "y",
          pointRadius: 3,
          pointHoverRadius: 5,
          tension: 0.35,
          fill: true,
        },
        {
          type: "line",
          label: "Выручка",
          data: series.map((item) => item.revenue),
          borderColor: "#5f82ff",
          backgroundColor: "rgba(95, 130, 255, 0.18)",
          pointBackgroundColor: "#5f82ff",
          pointBorderWidth: 0,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.28,
          fill: true,
          yAxisID: "y1",
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label(context) {
              if (context.dataset.label === "Выручка") {
                return `Выручка: ${formatMoney(context.parsed.y)}`;
              }
              return `Заказы: ${integer.format(context.parsed.y)}`;
            },
          },
        },
      },
      scales: {
        x: {
          ticks: {
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 6,
          },
          grid: { display: false },
          border: { display: false },
        },
        y: {
          beginAtZero: true,
          grid: { color: "rgba(122, 135, 148, 0.12)" },
          ticks: {
            precision: 0,
          },
          border: { display: false },
        },
        y1: {
          beginAtZero: true,
          position: "right",
          grid: { display: false },
          ticks: {
            callback: (value) => formatMoney(value),
          },
          border: { display: false },
        },
      },
    },
  });
}

async function loadDashboard() {
  const generatedAt = document.getElementById("generatedAt");

  try {
    const response = await fetch("/api/dashboard", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();

    renderStat("totalOrders", integer.format(payload.summary.total_orders));
    renderStat("totalRevenue", formatMoney(payload.summary.total_revenue));
    renderStat("avgOrderValue", formatMoney(payload.summary.average_order_value));
    renderStat("largeOrders", integer.format(payload.summary.large_orders));
    renderStat("thresholdValue", formatMoney(payload.summary.threshold));

    renderChart(payload.daily);
    renderTable("citiesTable", payload.top_cities, "city");
    renderTable("sourcesTable", payload.top_sources, "source");

    generatedAt.textContent = `Обновлено: ${new Date(payload.generated_at).toLocaleString("ru-RU")}`;
  } catch (error) {
    generatedAt.textContent = "Не удалось загрузить данные.";
    document.getElementById("statsGrid").innerHTML =
      '<div class="state">Проверьте переменные окружения Vercel и таблицу в Supabase.</div>';
    document.getElementById("citiesTable").innerHTML = `<div class="state">${error.message}</div>`;
    document.getElementById("sourcesTable").innerHTML =
      '<div class="state">API /api/dashboard должен вернуть JSON.</div>';
  }
}

loadDashboard();
