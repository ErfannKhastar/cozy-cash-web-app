/**
 * @file dashboard.js
 * @description Main controller for the Dashboard page.
 * Fetches and displays financial summaries, charts, and recent activities.
 */

const API_BASE_URL = "api/v1";
let spendingChartInstance = null;
let categoryChartInstance = null;

/**
 * Checks for 401 Unauthorized response and redirects to login if session expired.
 * @param {Response} response - The fetch API response object.
 * @returns {boolean} True if auth error occurred, False otherwise.
 */
function handleAuthError(response) {
  if (response.status === 401) {
    alert("Session expired. Please login again.");
    localStorage.clear();
    window.location.href = "auth.html";
    return true;
  }
  return false;
}

document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("accessToken");
  if (!token) {
    window.location.href = "auth.html";
    return;
  }

  setupLogout();
  setupAddExpenseForm(token);

  try {
    await loadUserProfile(token);

    // Load all dashboard components in parallel
    await Promise.all([
      loadDashboardSummary(token),
      loadRecentActivity(token),
      loadCharts(token),
    ]);
  } catch (error) {
    console.error("Error initializing dashboard:", error);
  }
});

// --- Functions ---

function setupLogout() {
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.clear();
      window.location.href = "/";
    });
  }
}

/**
 * Fetches current user profile to display the welcome message.
 * @param {string} token - JWT Access Token.
 */
async function loadUserProfile(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.ok) {
      const userData = await response.json();
      let name = userData.email.split("@")[0];
      name = name.charAt(0).toUpperCase() + name.slice(1);

      const welcomeEl = document.getElementById("userWelcome");
      if (welcomeEl) welcomeEl.textContent = `Hello, ${name}`;
    }
  } catch (error) {
    console.error(error);
  }
}

/**
 * Loads high-level summary cards (Total Expenses, Remaining Budget, Top Category).
 * @param {string} token - JWT Access Token.
 */
async function loadDashboardSummary(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/summary`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (handleAuthError(response)) return;

    if (response.ok) {
      const data = await response.json();

      // Update UI Cards
      document.getElementById(
        "totalExpensesCard"
      ).textContent = `$${data.total_spent.toLocaleString()}`;

      const remainingEl = document.getElementById("remainingBudgetCard");
      remainingEl.textContent = `$${data.remaining_budget.toLocaleString()}`;

      // Set color based on financial health status
      if (data.status === "Danger")
        remainingEl.className = "fw-bold mb-0 text-danger";
      else if (data.status === "Warning")
        remainingEl.className = "fw-bold mb-0 text-warning";
      else remainingEl.className = "fw-bold mb-0 text-dark-brown";

      document.getElementById("topCategoryCard").textContent =
        data.top_category;
    }
  } catch (error) {
    console.error("Summary Error:", error);
  }
}

/**
 * Fetches recent expenses and renders them in the activity feed.
 * @param {string} token - JWT Access Token.
 */
async function loadRecentActivity(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/expenses/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
      let expenses = await response.json();
      // Sort by date descending and take top 10
      expenses.sort((a, b) => new Date(b.date) - new Date(a.date));
      expenses = expenses.slice(0, 10);

      renderRecentTransactions(expenses);
    }
  } catch (error) {
    console.error("Recent Activity Error:", error);
  }
}

/**
 * Renders the list of transactions into the HTML container.
 * Maps backend categories to specific Bootstrap icons and colors.
 * @param {Array<Object>} expenses - List of expense objects.
 */
function renderRecentTransactions(expenses) {
  const container = document.getElementById("recentTransactionsList");
  if (!container) return;
  container.innerHTML = "";

  if (expenses.length === 0) {
    container.innerHTML =
      '<p class="text-muted text-center mt-3 small">No recent transactions.</p>';
    return;
  }

  // Visual mapping for categories
  const categoryStyles = {
    Food: { icon: "bi-cup-hot", color: "bg-soft-terracotta text-accent" },
    Transport: {
      icon: "bi-car-front",
      color: "bg-soft-coffee text-primary-cozy",
    },
    Fuel: { icon: "bi-fuel-pump", color: "bg-soft-coffee text-primary-cozy" },
    Housing: { icon: "bi-house-heart", color: "bg-soft-green text-success" },
    Utilities: {
      icon: "bi-lightning-charge",
      color: "bg-warning bg-opacity-10 text-warning",
    },
    Entertainment: {
      icon: "bi-controller",
      color: "bg-info bg-opacity-10 text-info",
    },
    Shopping: { icon: "bi-bag", color: "bg-danger bg-opacity-10 text-danger" },
    Health: {
      icon: "bi-heart-pulse",
      color: "bg-success bg-opacity-10 text-success",
    },
    Education: {
      icon: "bi-book",
      color: "bg-primary bg-opacity-10 text-primary",
    },
    Travel: {
      icon: "bi-airplane",
      color: "bg-secondary bg-opacity-10 text-secondary",
    },
    Personal: { icon: "bi-person", color: "bg-soft-terracotta text-accent" },
    Savings: { icon: "bi-piggy-bank", color: "bg-success text-white" },
    Debt: { icon: "bi-credit-card", color: "bg-danger text-white" },
    Gifts: { icon: "bi-gift", color: "bg-pink bg-opacity-10 text-danger" },
    Other: { icon: "bi-three-dots", color: "bg-light text-muted" },
  };

  expenses.forEach((exp) => {
    const dateObj = new Date(exp.date);
    const dateStr = dateObj.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });

    const style = categoryStyles[exp.category] || categoryStyles["Other"];

    const html = `
            <div class="d-flex align-items-center border-bottom py-2"> <div class="icon-box-sm ${
              style.color
            } me-3 rounded-circle d-flex align-items-center justify-content-center" style="width:40px; height:40px; min-width: 40px;">
                    <i class="bi ${style.icon}"></i>
                </div>
                <div class="flex-grow-1 overflow-hidden">
                    <h6 class="mb-0 text-dark-brown fw-bold text-truncate">${
                      exp.description
                    }</h6>
                    <small class="text-muted">${dateStr} • ${
      exp.category
    }</small>
                </div>
                <div class="text-end ms-2">
                    <span class="fw-bold text-danger">-$${Number(
                      exp.amount
                    ).toLocaleString()}</span>
                </div>
            </div>
        `;
    container.insertAdjacentHTML("beforeend", html);
  });
}

/**
 * Fetches data and renders both Spending Trend and Category Breakdown charts.
 * @param {string} token - JWT Access Token.
 */
async function loadCharts(token) {
  // --- Spending Trend (Line Chart) ---
  try {
    const trendRes = await fetch(`${API_BASE_URL}/analytics/spending-trend`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (trendRes.ok) {
      const trendData = await trendRes.json();
      renderTrendChart(trendData.data);
    }
  } catch (e) {
    console.error("Trend Chart Error:", e);
  }

  // --- Category Breakdown (Doughnut Chart) ---
  try {
    const catRes = await fetch(`${API_BASE_URL}/analytics/category-breakdown`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (catRes.ok) {
      const catData = await catRes.json();
      renderCategoryChart(catData.data);
    }
  } catch (e) {
    console.error("Category Chart Error:", e);
  }
}

/**
 * Renders a Line Chart using Chart.js.
 * @param {Array<Object>} dataPoints - Array of {date, amount} objects.
 */
function renderTrendChart(dataPoints) {
  const ctx = document.getElementById("spendingTrendChart").getContext("2d");

  if (spendingChartInstance) {
    spendingChartInstance.destroy();
  }

  const labels = dataPoints.map((dp) => dp.date);
  const values = dataPoints.map((dp) => dp.amount);

  spendingChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Daily Spending",
          data: values,
          borderColor: "#6F4E37",
          backgroundColor: "rgba(111, 78, 55, 0.1)",
          borderWidth: 2,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: "#E07A5F",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: "#f0f0f0" } },
        x: { grid: { display: false } },
      },
    },
  });
}

/**
 * Renders a Doughnut Chart using Chart.js.
 * @param {Array<Object>} dataItems - Array of {category, total_amount} objects.
 */
function renderCategoryChart(dataItems) {
  const ctx = document
    .getElementById("categoryBreakdownChart")
    .getContext("2d");

  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  const labels = dataItems.map((item) => item.category);
  const values = dataItems.map((item) => item.total_amount);

  const cozyColors = [
    "#E07A5F",
    "#81B29A",
    "#F2CC8F",
    "#6F4E37",
    "#3D405B",
    "#F4F1DE",
  ];

  categoryChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          data: values,
          backgroundColor: cozyColors,
          borderWidth: 0,
          hoverOffset: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { usePointStyle: true, boxWidth: 10 },
        },
      },
      cutout: "70%",
    },
  });
}

/**
 * Initializes the "Add Expense" modal and handles its form submission.
 * Manages date inputs to include current time for accurate sorting.
 * @param {string} token - JWT Access Token.
 */
function setupAddExpenseForm(token) {
  const form = document.getElementById("addExpenseForm");
  const dateInput = document.getElementById("expenseDate");
  const modalElement = document.getElementById("addExpenseModal");

  // Helper to set date input to Today
  const setTodayDate = () => {
    if (!dateInput) return;
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    dateInput.value = `${year}-${month}-${day}`;
  };

  if (dateInput && !dateInput.value) setTodayDate();

  if (modalElement) {
    modalElement.addEventListener("show.bs.modal", () => {
      if (!dateInput.value) setTodayDate();
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const amount = document.getElementById("expenseAmount").value;
      const desc = document.getElementById("expenseDesc").value;
      const category = document.getElementById("expenseCategory").value;
      const rawDate = document.getElementById("expenseDate").value;

      // Construct a full DateTime string (Date from input + Current Time)
      const now = new Date();
      const timePart = now.toTimeString().split(" ")[0];
      const finalDateTime = `${rawDate}T${timePart}`;

      const payload = {
        amount: amount,
        description: desc,
        category: category,
        date: finalDateTime,
      };

      try {
        const res = await fetch(`${API_BASE_URL}/expenses/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });

        if (handleAuthError(res)) return;

        if (res.ok) {
          alert("Expense Added!");

          // Hide Modal
          const modal = bootstrap.Modal.getInstance(modalElement);
          if (modal) modal.hide();

          form.reset();
          setTodayDate();

          // Refresh data based on current page context
          if (typeof loadDashboardSummary === "function") {
            console.log("Updating Dashboard...");
            await Promise.all([
              loadDashboardSummary(token),
              loadRecentActivity(token),
              loadCharts(token),
            ]);
          } else if (typeof loadExpenses === "function") {
            console.log("Updating Expenses List...");
            loadExpenses(token);
          } else {
            window.location.reload();
          }
        } else {
          const err = await res.json();
          alert("Error: " + (err.detail || JSON.stringify(err)));
        }
      } catch (error) {
        console.error(error);
      }
    });
  }
}
