/**
 * Sidak_CRM - Vanilla JavaScript
 * Handles delete confirmations, alert dismissals, and simple client-side form helpers.
 */

document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------
    // 1. Alert Dismissal
    // ----------------------------------------------------
    const closeButtons = document.querySelectorAll(".alert-close");
    closeButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const alertBox = btn.closest(".alert");
            if (alertBox) {
                alertBox.style.opacity = "0";
                alertBox.style.transition = "opacity 0.2s ease";
                setTimeout(() => alertBox.remove(), 200);
            }
        });
    });

    // ----------------------------------------------------
    // 2. Custom Safe Delete Confirmation Modal
    // ----------------------------------------------------
    const deleteModal = document.getElementById("deleteModal");
    const modalMessage = document.getElementById("deleteModalMessage");
    const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
    const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
    let formToSubmit = null;

    // Attach to all delete forms
    const deleteForms = document.querySelectorAll(".confirm-delete-form");
    deleteForms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            formToSubmit = form;
            const itemName = form.getAttribute("data-item-name") || "this record";
            const itemType = form.getAttribute("data-item-type") || "record";

            if (modalMessage) {
                modalMessage.textContent = `Are you sure you want to permanently delete the ${itemType} "${itemName}"? This action cannot be undone.`;
            }
            if (deleteModal) {
                deleteModal.classList.add("active");
            } else {
                // Fallback if modal DOM element is not present
                if (confirm(`Are you sure you want to delete "${itemName}"?`)) {
                    form.submit();
                }
            }
        });
    });

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener("click", () => {
            if (formToSubmit) {
                formToSubmit.submit();
            }
        });
    }

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener("click", () => {
            if (deleteModal) {
                deleteModal.classList.remove("active");
            }
            formToSubmit = null;
        });
    }

    // Close modal on click outside box
    if (deleteModal) {
        deleteModal.addEventListener("click", (e) => {
            if (e.target === deleteModal) {
                deleteModal.classList.remove("active");
                formToSubmit = null;
            }
        });
    }

    // ----------------------------------------------------
    // 3. Client-Side Form Enhancements
    // ----------------------------------------------------
    const forms = document.querySelectorAll("form[data-validate='true']");
    forms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const requiredInputs = form.querySelectorAll("[required]");
            let isValid = true;

            requiredInputs.forEach((input) => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = "var(--danger)";
                } else {
                    input.style.borderColor = "";
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert("Please fill in all required fields.");
            }
        });
    });
});
