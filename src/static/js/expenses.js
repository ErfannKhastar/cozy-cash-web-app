/**
 * @file expenses.js
 * @description Manages the Expenses list page.
 * Features include fetching expenses, pagination, client-side filtering (Search, Category, Date),
 * and handling Create/Update/Delete operations via modals.
 */

const API_BASE_URL = "api/v1";

let allExpenses = [];
let filteredExpenses = [];
let currentPage = 1;
const rowsPerPage = 10;

/**
 * Returns the CSS classes and icon for a given category.
 * Used to render colored icons in the list.
 * @param {string} category - The expense category.
 * @returns {Object} { icon: string, color: string }
 */
function getCategoryStyle(category) {
  const styles = {
    Food: { icon: "bi-basket", color: "bg-soft-terracotta text-accent" },
    Transport: {
      icon: "bi-fuel-pump",
      color: "bg-soft-coffee text-primary-cozy",
    },
    Housing: { icon: "bi-house-door", color: "bg-soft-green text-success" },
    Utilities: {
      icon: "bi-lightning-charge",
      color: "bg-soft-coffee text-warning",
    },
    Entertainment: {
      icon: "bi-controller",
      color: "bg-soft-terracotta text-danger",
    },
    Shopping: { icon: "bi-bag", color: "bg-soft-terracotta text-danger" },
    Health: { icon: "bi-heart-pulse", color: "bg-soft-green text-success" },
    Education: { icon: "bi-book", color: "bg-soft-coffee text-primary-cozy" },
    Travel: { icon: "bi-airplane", color: "bg-soft-green text-success" },
    Personal: { icon: "bi-person", color: "bg-soft-terracotta text-accent" },
    Debt: { icon: "bi-bank", color: "bg-soft-coffee text-dark-brown" },
    Savings: { icon: "bi-piggy-bank", color: "bg-soft-green text-success" },
    Gifts: { icon: "bi-gift", color: "bg-soft-terracotta text-danger" },
    Other: { icon: "bi-box", color: "bg-soft-coffee text-dark-brown" },
  };
  return (
    styles[category] || {
      icon: "bi-tag",
      color: "bg-soft-coffee text-dark-brown",
    }
  );
}

/**
 * Handles 401 Unauthorized errors by clearing session and redirecting.
 */
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
  setupAddExpenseForm(token);
  setupFilters();

  loadUserProfile(token);
  await loadExpenses(token);
});

// --- Core Functions ---
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
 * Fetches all expenses from the API and initializes the table.
 * Sorts data by date descending.
 */
async function loadExpenses(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/expenses/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (handleAuthError(response)) return;

    if (response.ok) {
      allExpenses = await response.json();
      allExpenses.sort((a, b) => new Date(b.date) - new Date(a.date));
      filteredExpenses = [...allExpenses]; // Init filtered list with all items
      displayData(1); // Show first page
    }
  } catch (error) {
    console.error("Error loading expenses:", error);
  }
}

/**
 * Calculates pagination logic and renders the current page's items.
 * @param {number} page - The page number to display.
 */
function displayData(page) {
  const container = document.getElementById("expensesList");
  container.innerHTML = "";

  const totalItems = filteredExpenses.length;
  const pageCount = Math.ceil(totalItems / rowsPerPage);

  if (page < 1) page = 1;
  if (page > pageCount && pageCount > 0) page = pageCount;
  currentPage = page;

  const start = (currentPage - 1) * rowsPerPage;
  const end = start + rowsPerPage;
  const paginatedItems = filteredExpenses.slice(start, end);

  renderExpenses(paginatedItems);

  setupPaginationControls(totalItems, pageCount);
}

/**
 * Generates the HTML for pagination buttons (Prev, Numbers, Next).
 */
function setupPaginationControls(totalItems, pageCount) {
  const wrapper = document.getElementById("paginationControls");
  if (!wrapper) return;

  wrapper.innerHTML = "";

  if (pageCount <= 1) return;

  const prevClass = currentPage === 1 ? "disabled" : "";
  let paginationHTML = `
        <li class="page-item ${prevClass}">
            <a class="page-link" href="#" onclick="changePage(${
              currentPage - 1
            }); return false;">Previous</a>
        </li>
    `;

  for (let i = 1; i <= pageCount; i++) {
    const activeClass =
      i === currentPage
        ? "active bg-primary-cozy border-primary-cozy"
        : "text-dark-brown";
    const textClass = i === currentPage ? "" : "text-dark-brown";

    paginationHTML += `
            <li class="page-item ${activeClass}">
                <a class="page-link ${textClass}" href="#" onclick="changePage(${i}); return false;">${i}</a>
            </li>
        `;
  }

  const nextClass = currentPage === pageCount ? "disabled" : "";
  paginationHTML += `
        <li class="page-item ${nextClass}">
            <a class="page-link" href="#" onclick="changePage(${
              currentPage + 1
            }); return false;">Next</a>
        </li>
    `;

  wrapper.innerHTML = paginationHTML;
}

window.changePage = function (newPage) {
  displayData(newPage);
  const filterCard = document.querySelector(".card-cozy");
  if (filterCard) filterCard.scrollIntoView({ behavior: "smooth" });
};

/**
 * Renders the HTML cards for a list of expenses.
 */
function renderExpenses(items) {
  const container = document.getElementById("expensesList");

  if (items.length === 0) {
    container.innerHTML =
      '<div class="text-center mt-5"><i class="bi bi-inbox fs-1 text-muted"></i><p class="text-muted mt-2">No expenses found.</p></div>';
    return;
  }

  items.forEach((exp) => {
    const dateObj = new Date(exp.date);
    const dateStr = dateObj.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
    const style = getCategoryStyle(exp.category);

    const html = `
            <div class="card expense-row border-0 shadow-sm">
                <div class="card-body d-flex align-items-center p-3">
                    <div class="icon-box ${style.color} rounded-circle me-3">
                        <i class="bi ${style.icon}"></i>
                    </div>
                    
                    <div class="flex-grow-1">
                        <h6 class="fw-bold text-dark-brown mb-1">${
                          exp.description
                        }</h6>
                        <div class="small text-muted">
                            <span class="me-2"><i class="bi bi-calendar3 me-1"></i> ${dateStr}</span>
                            <span class="badge bg-light text-dark border">${
                              exp.category
                            }</span>
                        </div>
                    </div>

                    <div class="text-end d-flex align-items-center gap-3">
                        <span class="fw-bold text-danger fs-5 me-2">-$${Number(
                          exp.amount
                        ).toLocaleString()}</span>
                        
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-light text-primary-cozy" onclick="openEditModal(${
                              exp.id
                            })" title="Edit">
                                <i class="bi bi-pencil-square"></i>
                            </button>
                            <button class="btn btn-sm btn-light text-danger" onclick="deleteExpense(${
                              exp.id
                            })" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    container.insertAdjacentHTML("beforeend", html);
  });
}

/**
 * Sets up listeners for the Search Bar, Category Dropdown, and Date Picker.
 * Filters the `filteredExpenses` array based on input.
 */
function setupFilters() {
  const searchInput = document.getElementById("filterSearch");
  const categorySelect = document.getElementById("filterCategory");
  const dateInput = document.getElementById("filterDate");
  const resetBtn = document.getElementById("resetFiltersBtn");

  function applyFilters() {
    if (!searchInput || !categorySelect || !dateInput) return;

    const searchTerm = searchInput.value.toLowerCase();
    const selectedCategory = categorySelect.value;
    const selectedDate = dateInput.value;

    filteredExpenses = allExpenses.filter((exp) => {
      const matchesSearch = exp.description.toLowerCase().includes(searchTerm);
      const matchesCategory =
        selectedCategory === "" ||
        selectedCategory === "All Categories" ||
        exp.category === selectedCategory;

      let matchesDate = true;
      if (selectedDate) {
        const expDateStr = exp.date.split("T")[0];
        matchesDate = expDateStr === selectedDate;
      }

      return matchesSearch && matchesCategory && matchesDate;
    });

    displayData(1); // Reset to page 1 after filter
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      searchInput.value = "";
      categorySelect.value = "All Categories";
      categorySelect.selectedIndex = 0;
      dateInput.value = "";

      filteredExpenses = [...allExpenses];
      displayData(1);
    });
  }

  if (searchInput) searchInput.addEventListener("input", applyFilters);
  if (categorySelect) categorySelect.addEventListener("change", applyFilters);
  if (dateInput) dateInput.addEventListener("change", applyFilters);
}

/**
 * Populates and shows the Edit Modal for a specific expense.
 */
window.openEditModal = function (id) {
  const expense = allExpenses.find((e) => e.id === id);
  if (!expense) return;

  document.getElementById("editExpenseId").value = expense.id;
  document.getElementById("editAmount").value = expense.amount;
  document.getElementById("editDesc").value = expense.description;
  document.getElementById("editCategory").value = expense.category;

  const dateStr = expense.date.split("T")[0];
  document.getElementById("editDate").value = dateStr;

  const modalEl = document.getElementById("editExpenseModal");
  const modal = new bootstrap.Modal(modalEl);
  modal.show();

  const form = document.getElementById("editExpenseForm");
  const newForm = form.cloneNode(true);
  form.parentNode.replaceChild(newForm, form);

  newForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    await submitEditExpense();
  });
};

async function submitEditExpense() {
  const id = document.getElementById("editExpenseId").value;
  const token = localStorage.getItem("accessToken");

  // Construct ISO date string
  const payload = {
    amount: document.getElementById("editAmount").value,
    description: document.getElementById("editDesc").value,
    category: document.getElementById("editCategory").value,
    date: new Date(document.getElementById("editDate").value).toISOString(),
  };

  try {
    const res = await fetch(`${API_BASE_URL}/expenses/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (handleAuthError(res)) return;

    if (res.ok) {
      alert("Expense Updated!");
      const closeBtn = document.querySelector("#editExpenseModal .btn-close");
      if (closeBtn) closeBtn.click();
      loadExpenses(token);
    } else {
      alert("Failed to update expense.");
    }
  } catch (error) {
    console.error("Error updating:", error);
  }
}

/**
 * Deletes an expense and updates the local lists.
 */
window.deleteExpense = async function (id) {
  if (!confirm("Are you sure you want to delete this expense?")) return;
  const token = localStorage.getItem("accessToken");
  try {
    const response = await fetch(`${API_BASE_URL}/expenses/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (handleAuthError(response)) return;

    if (response.status === 204) {
      // Optimistic UI update: Remove locally without refetching all
      allExpenses = allExpenses.filter((exp) => exp.id !== id);
      filteredExpenses = filteredExpenses.filter((exp) => exp.id !== id);

      displayData(currentPage);
    }
  } catch (error) {
    console.error("Error deleting:", error);
  }
};

/**
 * Configures the "Add Expense" modal, including date presets and form submission.
 */
function setupAddExpenseForm(token) {
  const form = document.getElementById("addExpenseForm");
  const dateInput = document.getElementById("expenseDate");
  const modalElement = document.getElementById("addExpenseModal");

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

          const modal = bootstrap.Modal.getInstance(modalElement);
          if (modal) modal.hide();

          form.reset();
          setTodayDate();

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
