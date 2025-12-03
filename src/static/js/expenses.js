// static/js/expenses.js

const API_BASE_URL = "api/v1";

// متغیرهای مدیریت دیتا و صفحه‌بندی
let allExpenses = []; // کل داده‌های سرور
let filteredExpenses = []; // داده‌های فیلتر شده (برای نمایش)
let currentPage = 1; // صفحه فعلی
const rowsPerPage = 10; // تعداد آیتم در هر صفحه (می‌تونی تغییر بدی)

// --- Helper: آیکون‌ها ---
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
  setupFilters(); // راه‌اندازی فیلترها

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

async function loadExpenses(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/expenses/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (handleAuthError(response)) return;

    if (response.ok) {
      allExpenses = await response.json();
      // مرتب‌سازی زمانی نزولی
      allExpenses.sort((a, b) => new Date(b.date) - new Date(a.date));

      // مقداردهی اولیه لیست فیلتر شده با کل داده‌ها
      filteredExpenses = [...allExpenses];

      // شروع نمایش از صفحه ۱ (این تابع قبلاً جا افتاده بود!)
      displayData(1);
    }
  } catch (error) {
    console.error("Error loading expenses:", error);
  }
}

// --- Pagination Logic (این بخش قبلاً جا افتاده بود) ---

function displayData(page) {
  const container = document.getElementById("expensesList");
  container.innerHTML = "";

  const totalItems = filteredExpenses.length;
  const pageCount = Math.ceil(totalItems / rowsPerPage);

  // اعتبارسنجی صفحه
  if (page < 1) page = 1;
  if (page > pageCount && pageCount > 0) page = pageCount;
  currentPage = page;

  // برش داده‌ها برای صفحه جاری
  const start = (currentPage - 1) * rowsPerPage;
  const end = start + rowsPerPage;
  const paginatedItems = filteredExpenses.slice(start, end);

  // 1. رندر کردن لیست
  renderExpenses(paginatedItems);

  // 2. رندر کردن دکمه‌های پایین صفحه
  setupPaginationControls(totalItems, pageCount);
}

function setupPaginationControls(totalItems, pageCount) {
  const wrapper = document.getElementById("paginationControls"); // باید در HTML این ID رو به ul داده باشی
  if (!wrapper) return; // اگر المنت نبود ارور نده

  wrapper.innerHTML = "";

  if (pageCount <= 1) return;

  // Previous
  const prevClass = currentPage === 1 ? "disabled" : "";
  let paginationHTML = `
        <li class="page-item ${prevClass}">
            <a class="page-link" href="#" onclick="changePage(${
              currentPage - 1
            }); return false;">Previous</a>
        </li>
    `;

  // Page Numbers
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

  // Next
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

// تابع گلوبال برای تغییر صفحه
window.changePage = function (newPage) {
  displayData(newPage);
  // اسکرول به بالای لیست
  const filterCard = document.querySelector(".card-cozy");
  if (filterCard) filterCard.scrollIntoView({ behavior: "smooth" });
};

// --- Render Logic (Minimal Buttons) ---

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

// --- Filters Logic ---

function setupFilters() {
  // استفاده از ID برای انتخاب دقیق
  const searchInput = document.getElementById("filterSearch");
  const categorySelect = document.getElementById("filterCategory");
  const dateInput = document.getElementById("filterDate");
  const resetBtn = document.getElementById("resetFiltersBtn");

  function applyFilters() {
    // اگر المان‌ها لود نشده باشند، ادامه نده
    if (!searchInput || !categorySelect || !dateInput) return;

    const searchTerm = searchInput.value.toLowerCase();
    const selectedCategory = categorySelect.value;
    const selectedDate = dateInput.value;

    // فیلتر کردن روی کل داده‌ها
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

    // نمایش نتایج فیلتر شده (از صفحه ۱)
    displayData(1);
  }

  // لاجیک دکمه ریست
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      searchInput.value = "";
      categorySelect.value = "All Categories"; // یا مقدار خالی اگر value="" است
      categorySelect.selectedIndex = 0; // مطمئن‌ترین راه برای انتخاب اولین گزینه
      dateInput.value = "";

      // برگرداندن همه داده‌ها
      filteredExpenses = [...allExpenses];
      displayData(1);
    });
  }

  if (searchInput) searchInput.addEventListener("input", applyFilters);
  if (categorySelect) categorySelect.addEventListener("change", applyFilters);
  if (dateInput) dateInput.addEventListener("change", applyFilters);
}

// --- Edit Logic ---

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

// --- Delete Logic ---

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
      // حذف از هر دو آرایه
      allExpenses = allExpenses.filter((exp) => exp.id !== id);
      filteredExpenses = filteredExpenses.filter((exp) => exp.id !== id);

      // رندر مجدد صفحه فعلی
      displayData(currentPage);
    }
  } catch (error) {
    console.error("Error deleting:", error);
  }
};

// --- Add Expense Logic ---

function setupAddExpenseForm(token) {
  const form = document.getElementById("addExpenseForm");
  const dateInput = document.getElementById("expenseDate");
  const modalElement = document.getElementById("addExpenseModal");

  // 1. تابع تنظیم تاریخ امروز (به وقت محلی سیستم کاربر)
  const setTodayDate = () => {
    if (!dateInput) return;
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    dateInput.value = `${year}-${month}-${day}`;
  };

  // تنظیم تاریخ به محض لود شدن (اگر خالی بود)
  if (dateInput && !dateInput.value) setTodayDate();

  // تنظیم تاریخ هر بار که مودال باز می‌شود
  if (modalElement) {
    modalElement.addEventListener("show.bs.modal", () => {
      // اگر کاربر قبلا تاریخی انتخاب نکرده بود یا فرم ریست شده بود، تاریخ امروز را بگذار
      if (!dateInput.value) setTodayDate();
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const amount = document.getElementById("expenseAmount").value;
      const desc = document.getElementById("expenseDesc").value;
      const category = document.getElementById("expenseCategory").value;

      // --- اصلاحیه مهم تاریخ ---
      // گرفتن تاریخ انتخابی کاربر به صورت رشته (مثلا "2025-11-25")
      const rawDate = document.getElementById("expenseDate").value;

      // گرفتن ساعت فعلی سیستم (مثلا "14:30:00")
      const now = new Date();
      const timePart = now.toTimeString().split(" ")[0];

      // چسباندن این دو به هم: "2025-11-25T14:30:00"
      // این روش تضمین می‌کند که روز عوض نمی‌شود
      const finalDateTime = `${rawDate}T${timePart}`;
      // ------------------------

      // --- چک کردن بودجه (اختیاری) ---
      // (اگر کد چک کردن بودجه را داری اینجا بگذار، وگرنه حذفش کن تا شلوغ نشود)

      const payload = {
        amount: amount,
        description: desc,
        category: category,
        date: finalDateTime, // <--- استفاده از تاریخ دقیق ساخته شده
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

          // بستن مودال
          const modal = bootstrap.Modal.getInstance(modalElement);
          if (modal) modal.hide();

          form.reset();
          setTodayDate(); // ست کردن مجدد تاریخ برای ثبت بعدی

          // --- رفرش هوشمند ---
          // اگر در داشبورد هستیم، همه چیز را آپدیت کن
          if (typeof loadDashboardSummary === "function") {
            console.log("Updating Dashboard...");
            await Promise.all([
              loadDashboardSummary(token),
              loadRecentActivity(token),
              loadCharts(token),
            ]);
          }
          // اگر در صفحه هزینه‌ها هستیم، لیست را آپدیت کن
          else if (typeof loadExpenses === "function") {
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
