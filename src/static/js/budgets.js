/**
 * @file budgets.js
 * @description Manages the Budget page logic.
 * Responsible for fetching budgets AND expenses to calculate spending progress.
 * Includes logic for progress bars, color coding statuses, and duplicate budget prevention.
 */
const API_BASE_URL = "api/v1";
let allBudgets = [];
let allExpenses = [];

function getCategoryStyle(category) {
  const styles = {
    Food: { icon: "bi-basket" },
    Transport: { icon: "bi-fuel-pump" },
    Housing: { icon: "bi-house-door" },
    Utilities: { icon: "bi-lightning-charge" },
    Entertainment: { icon: "bi-controller" },
    Shopping: { icon: "bi-bag" },
    Health: { icon: "bi-heart-pulse" },
    Education: { icon: "bi-book" },
    Travel: { icon: "bi-airplane" },
    Personal: { icon: "bi-person" },
    Debt: { icon: "bi-bank" },
    Savings: { icon: "bi-piggy-bank" },
    Gifts: { icon: "bi-gift" },
    Other: { icon: "bi-box" },
  };
  return styles[category] || { icon: "bi-tag" };
}

function handleAuthError(response) {
  if (response.status === 401) {
    alert("Session expired. Please login again.");
    localStorage.clear();
    window.location.href = "/auth";
    return true;
  }
  return false;
}

document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("accessToken");
  if (!token) {
    window.location.href = "/auth";
    return;
  }

  setupLogout();
  setupAddBudgetForm(token);
  setupFilters();
  loadUserProfile(token);

  await loadBudgetsAndCalculate(token);
});

function setupLogout() {
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.clear();
      window.location.href = "/";
    });
  }
}

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
  } catch (e) {
    console.error(e);
  }
}

/**
 * Fetches BOTH budgets and expenses in parallel to calculate progress.
 * Expenses are needed to see how much of the budget has been consumed.
 */
async function loadBudgetsAndCalculate(token) {
  try {
    const [budgetsRes, expensesRes] = await Promise.all([
      fetch(`${API_BASE_URL}/budgets/`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
      fetch(`${API_BASE_URL}/expenses/`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
    ]);

    if (handleAuthError(budgetsRes) || handleAuthError(expensesRes)) return;

    if (budgetsRes.ok && expensesRes.ok) {
      allBudgets = await budgetsRes.json();
      allExpenses = await expensesRes.json();
      // Sort budgets by date descending
      allBudgets.sort((a, b) => new Date(b.month) - new Date(a.month));
      applyDefaultFilter(); // Show current month by default
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

/**
 * Defaults the view to the current month when page loads.
 */
function applyDefaultFilter() {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const currentMonthStr = `${yyyy}-${mm}`;

  const filterMonthInput = document.getElementById("filterMonth");
  if (filterMonthInput) {
    filterMonthInput.value = currentMonthStr;
    filterMonthInput.dispatchEvent(new Event("change"));
  } else {
    renderBudgets(allBudgets);
  }
}

/**
 * Handles filtering logic for Category, specific Month, or "All Year".
 */
function setupFilters() {
  const categorySelect = document.getElementById("filterCategory");
  const monthInput = document.getElementById("filterMonth");
  const showAllYearCheck = document.getElementById("showAllYear");
  const resetBtn = document.getElementById("resetFiltersBtn");

  function applyFilters() {
    const selectedCategory = categorySelect.value;
    const selectedMonthVal = monthInput.value;
    const showAllYear = showAllYearCheck.checked;

    const filtered = allBudgets.filter((budget) => {
      const matchCategory =
        selectedCategory === "" || budget.category === selectedCategory;

      let matchTime = true;
      if (selectedMonthVal) {
        const budgetMonthStr = budget.month.substring(0, 7);

        if (showAllYear) {
          const selectedYear = selectedMonthVal.substring(0, 4);
          const budgetYear = budgetMonthStr.substring(0, 4);
          matchTime = budgetYear === selectedYear;
        } else {
          matchTime = budgetMonthStr === selectedMonthVal;
        }
      }

      return matchCategory && matchTime;
    });

    renderBudgets(filtered);
  }

  if (categorySelect) categorySelect.addEventListener("change", applyFilters);
  if (monthInput) monthInput.addEventListener("change", applyFilters);
  if (showAllYearCheck)
    showAllYearCheck.addEventListener("change", applyFilters);

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      categorySelect.value = "";
      showAllYearCheck.checked = false;
      applyDefaultFilter();
    });
  }
}

/**
 * Renders the Budget cards with progress bars.
 * Calculates spending for each budget based on its category and month.
 */
function renderBudgets(budgets) {
  const container = document.getElementById("budgetsContainer");
  container.innerHTML = "";

  if (budgets.length === 0) {
    container.innerHTML =
      '<div class="col-12 text-center mt-5"><i class="bi bi-calendar-x fs-1 text-muted"></i><p class="text-muted mt-2">No budgets found for this period.</p></div>';
    return;
  }

  budgets.forEach((budget) => {
    const budgetDate = new Date(budget.month);
    const monthName = budgetDate.toLocaleDateString("en-US", {
      month: "long",
      year: "numeric",
    });

    // Calculate how much spent for this budget
    const spent = allExpenses
      .filter((exp) => {
        const expDate = new Date(exp.date);
        return (
          exp.category === budget.category &&
          expDate.getMonth() === budgetDate.getMonth() &&
          expDate.getFullYear() === budgetDate.getFullYear()
        );
      })
      .reduce((sum, exp) => sum + Number(exp.amount), 0);

    const percentage = Math.min((spent / budget.amount) * 100, 100);
    const percentageText = Math.round((spent / budget.amount) * 100);

    // Dynamic coloring based on usage
    let colorClass = "bg-success";
    let textClass = "text-success";
    let statusBadge = "Good";
    let badgeClass = "bg-soft-green text-success";

    const style = getCategoryStyle(budget.category);

    if (percentageText >= 100) {
      colorClass = "bg-danger";
      textClass = "text-danger";
      statusBadge = "Over Budget";
      badgeClass = "bg-soft-terracotta text-danger";
    } else if (percentageText >= 80) {
      colorClass = "bg-warning";
      textClass = "text-warning";
      statusBadge = "Warning";
      badgeClass = "bg-soft-coffee text-warning";
    }

    const html = `
    <div class="col-md-6 col-lg-4">
        <div class="card card-cozy h-100 position-relative">
            <div class="card-body">
                
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="fw-bold text-dark-brown d-flex align-items-center m-0" style="max-width: 65%;">
                        <i class="bi ${style.icon} me-2 ${textClass}"></i>
                        <span class="text-truncate" title="${
                          budget.category
                        }">${budget.category}</span>
                    </h5>
                    
                    <div class="d-flex align-items-center gap-1">
                        <span class="badge bg-light text-dark border me-1 small d-none d-md-inline-block">${monthName}</span>
                        
                        <span class="badge ${badgeClass} p-1">${statusBadge}</span>
                        
                        <button class="btn btn-sm btn-link text-primary-cozy p-0 ms-1" onclick="openEditBudgetModal(${
                          budget.id
                        })" title="Edit">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-sm btn-link text-danger p-0 ms-1" onclick="deleteBudget(${
                          budget.id
                        })" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                
                <h3 class="fw-bold mb-3 ${textClass}">
                    $${Math.round(
                      spent
                    )} <span class="text-muted fs-6 fw-normal">/ $${Math.round(
      budget.amount
    )}</span>
                </h3>
                
                <div class="progress mb-2" style="height: 10px;">
                    <div class="progress-bar ${colorClass}" role="progressbar" style="width: ${percentage}%"></div>
                </div>
                <small class="text-muted">${percentageText}% used</small>
            </div>
        </div>
    </div>
  `;
    container.insertAdjacentHTML("beforeend", html);
  });
}

function setupAddBudgetForm(token) {
  const form = document.getElementById("addBudgetForm");
  const monthInput = document.getElementById("budgetMonth");
  if (monthInput) {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, "0");
    monthInput.value = `${yyyy}-${mm}`;
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const category = document.getElementById("budgetCategory").value;
      const amount = document.getElementById("budgetAmount").value;
      const monthStr = document.getElementById("budgetMonth").value;

      // Prevent duplicate budget for same category/month on client side
      const duplicate = allBudgets.find((b) => {
        const budgetMonth = b.month.substring(0, 7);
        return b.category === category && budgetMonth === monthStr;
      });

      if (duplicate) {
        alert(
          `You already have a budget for "${category}" in this month. Please Edit it instead.`
        );
        return;
      }

      const fullDate = `${monthStr}-01`;

      const payload = {
        category: category,
        amount: amount,
        month: fullDate,
      };

      try {
        const res = await fetch(`${API_BASE_URL}/budgets/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });

        if (handleAuthError(res)) return;

        if (res.ok) {
          alert("Budget Set Successfully!");
          window.location.reload();
        } else {
          const err = await res.json();
          if (res.status === 409) {
            alert("Duplicate budget! You already have this budget.");
          } else {
            alert("Error: " + JSON.stringify(err));
          }
        }
      } catch (error) {
        console.error(error);
      }
    });
  }
}

/**
 * Opens Edit Budget Modal and pre-fills it.
 */
window.openEditBudgetModal = function (id) {
  const budget = allBudgets.find((b) => b.id === id);
  if (!budget) return;

  document.getElementById("editBudgetId").value = budget.id;
  document.getElementById("editBudgetCategory").value = budget.category;
  document.getElementById("editBudgetAmount").value = budget.amount;

  const monthStr = budget.month.substring(0, 7);
  document.getElementById("editBudgetMonth").value = monthStr;

  const modalEl = document.getElementById("editBudgetModal");
  const modal = new bootstrap.Modal(modalEl);
  modal.show();

  const form = document.getElementById("editBudgetForm");
  const newForm = form.cloneNode(true);
  form.parentNode.replaceChild(newForm, form);

  newForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    await submitEditBudget(budget);
  });
};

async function submitEditBudget(originalBudget) {
  const id = document.getElementById("editBudgetId").value;
  const newAmount = document.getElementById("editBudgetAmount").value;
  const token = localStorage.getItem("accessToken");

  // Keep original month and category, only update amount
  const payload = {
    category: originalBudget.category,
    amount: newAmount,
    month: originalBudget.month,
  };

  try {
    const res = await fetch(`${API_BASE_URL}/budgets/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (handleAuthError(res)) return;

    if (res.ok) {
      alert("Budget Updated!");
      const closeBtn = document.querySelector("#editBudgetModal .btn-close");
      if (closeBtn) closeBtn.click();
      window.location.reload();
    } else {
      alert("Failed to update budget.");
    }
  } catch (error) {
    console.error("Error updating:", error);
  }
}

window.deleteBudget = async function (id) {
  if (!confirm("Delete this budget?")) return;
  const token = localStorage.getItem("accessToken");

  try {
    const res = await fetch(`${API_BASE_URL}/budgets/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (handleAuthError(res)) return;

    if (res.status === 204) {
      window.location.reload();
    } else {
      alert("Failed to delete.");
    }
  } catch (e) {
    console.error(e);
  }
};
