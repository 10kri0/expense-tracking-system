function parseChartPayload(id) {
  const node = document.getElementById(id);
  if (!node) {
    return null;
  }

  try {
    return JSON.parse(node.textContent);
  } catch (error) {
    return null;
  }
}

function renderCategoryChart() {
  const canvas = document.getElementById("categoryChart");
  const payload = parseChartPayload("category-chart-data");
  if (!canvas || !payload || !payload.labels || !payload.labels.length || typeof Chart === "undefined") {
    return;
  }

  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: payload.labels,
      datasets: [
        {
          data: payload.values,
          backgroundColor: ["#f26b4b", "#0f766e", "#dd9d18", "#3d6980", "#f2b5a7"],
          borderWidth: 0,
          hoverOffset: 10,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            usePointStyle: true,
            boxWidth: 10,
            color: "#21313c",
          },
        },
      },
    },
  });
}

function renderTrendChart() {
  const canvas = document.getElementById("trendChart");
  const payload = parseChartPayload("trend-chart-data");
  if (!canvas || !payload || !payload.labels || !payload.labels.length || typeof Chart === "undefined") {
    return;
  }

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: payload.labels,
      datasets: [
        {
          label: "Monthly Expenses",
          data: payload.values,
          backgroundColor: "#0f766e",
          borderRadius: 10,
          maxBarThickness: 42,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            color: "#5f6d74",
          },
          grid: {
            color: "rgba(33, 49, 60, 0.08)",
          },
        },
        x: {
          ticks: {
            color: "#5f6d74",
          },
          grid: {
            display: false,
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderCategoryChart();
  renderTrendChart();
});
