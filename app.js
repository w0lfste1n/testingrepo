const currency = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "KZT",
  maximumFractionDigits: 0,
});

const integer = new Intl.NumberFormat("ru-RU");
let chart;

function renderStat(id, value) {
  document.getElementById(id).textContent = value;
}

function renderTable(targetId, rows, labelKey) {
  const target = document.getElementById(targetId);
  if (!rows.length) {
    target.innerHTML = '<div class="state">Данные пока не загружены.</div>';
    return;
  }

  target.innerHTML = rows
    .slice(0, 6)
    .map(
      (row) => `
        <div class="table-row">
          <div>
            <strong>${row[labelKey]}</strong>
          </div>
          <span>${currency.format(row.revenue)}</span>
        </div>
      `,
    )
    .join("");
}

function renderChart(daily) {
  const ctx = document.getElementById("ordersChart");
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: daily.map((item) => item.date),
      datasets: [
        {
          type: "bar",
          label: "Заказы",
          data: daily.map((item) => item.orders),
          borderRadius: 12,
          backgroundColor: "#b85c38",
          yAxisID: "y",
        },
        {
          type: "line",
          label: "Выручка",
          data: daily.map((item) => item.revenue),
          borderColor: "#0d6b5f",
          backgroundColor: "rgba(13,107,95,0.18)",
          tension: 0.35,
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
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "rgba(30, 26, 23, 0.08)" },
        },
        y1: {
          beginAtZero: true,
          position: "right",
          grid: { display: false },
          ticks: {
            callback: (value) => `${Math.round(value / 1000)}k ₸`,
          },
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
    renderStat("totalRevenue", currency.format(payload.summary.total_revenue));
    renderStat("avgOrderValue", currency.format(payload.summary.average_order_value));
    renderStat("largeOrders", integer.format(payload.summary.large_orders));
    renderStat("thresholdValue", currency.format(payload.summary.threshold));

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
