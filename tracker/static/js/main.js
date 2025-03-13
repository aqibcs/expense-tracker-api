document.addEventListener("DOMContentLoaded", () => {
  // Toggle sidebar on mobile
  const sidebarToggle = document.getElementById("sidebarToggle");
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      const sidebar = document.querySelector(".sidebar");
      sidebar.classList.toggle("expanded");
    });
  }

  // Password toggle
  const passwordToggles = document.querySelectorAll(".password-toggle");
  passwordToggles.forEach((toggle) => {
    toggle.addEventListener("click", function () {
      const inputWrapper = this.closest(".input-wrapper");
      const passwordInput = inputWrapper.querySelector("input");
      const eyeIcon = this.querySelector(".eye");
      const eyeOffIcon = this.querySelector(".eye-off");

      if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.style.display = "none";
        eyeOffIcon.style.display = "block";
      } else {
        passwordInput.type = "password";
        eyeIcon.style.display = "block";
        eyeOffIcon.style.display = "none";
      }
    });
  });

  // Close messages
  const closeButtons = document.querySelectorAll(".close-message");
  closeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      this.closest(".message").remove();
    });
  });

  // Filter toggle
  const filterToggle = document.getElementById("filterToggle");
  const filterForm = document.getElementById("filterForm");
  if (filterToggle && filterForm) {
    filterToggle.addEventListener("click", () => {
      filterForm.style.display =
        filterForm.style.display === "none" ? "block" : "none";
    });
  }

  // Delete expense modal
  const deleteButtons = document.querySelectorAll(".delete-expense");
  const deleteModal = document.getElementById("deleteModal");
  const cancelDelete = document.getElementById("cancelDelete");
  const deleteForm = document.getElementById("deleteForm");

  if (deleteButtons.length && deleteModal) {
    deleteButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const expenseId = this.dataset.id;
        deleteForm.action = `/expenses/${expenseId}/delete/`;
        deleteModal.classList.add("active");
      });
    });

    if (cancelDelete) {
      cancelDelete.addEventListener("click", () => {
        deleteModal.classList.remove("active");
      });
    }

    const closeModal = deleteModal.querySelector(".close-modal");
    if (closeModal) {
      closeModal.addEventListener("click", () => {
        deleteModal.classList.remove("active");
      });
    }
  }

  // Edit profile modal
  const editProfileBtn = document.getElementById("editProfileBtn");
  const editProfileModal = document.getElementById("editProfileModal");
  const cancelEdit = document.getElementById("cancelEdit");

  if (editProfileBtn && editProfileModal) {
    editProfileBtn.addEventListener("click", (e) => {
      e.preventDefault();
      editProfileModal.classList.add("active");
    });

    if (cancelEdit) {
      cancelEdit.addEventListener("click", () => {
        editProfileModal.classList.remove("active");
      });
    }

    const closeModal = editProfileModal.querySelector(".close-modal");
    if (closeModal) {
      closeModal.addEventListener("click", () => {
        editProfileModal.classList.remove("active");
      });
    }
  }

  // Export to CSV
  const exportBtn = document.getElementById("exportBtn");
  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      const table = document.querySelector(".table");
      if (!table) return;

      const rows = table.querySelectorAll("tbody tr");
      if (!rows.length) return;

      let csvContent = "data:text/csv;charset=utf-8,";

      // Headers
      const headers = Array.from(table.querySelectorAll("thead th"))
        .map((th) => `"${th.textContent.trim()}"`)
        .slice(0, -1); // Remove Actions column
      csvContent += headers.join(",") + "\r\n";

      // Rows
      rows.forEach((row) => {
        const cells = Array.from(row.querySelectorAll("td"))
          .slice(0, -1) // Remove Actions column
          .map((cell) => {
            let text = cell.textContent.trim();
            // Remove currency symbol
            if (cell.classList.contains("amount")) {
              text = text.replace("$", "");
            }
            return `"${text}"`;
          });
        csvContent += cells.join(",") + "\r\n";
      });

      // Create download link
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "expenses.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }
});
