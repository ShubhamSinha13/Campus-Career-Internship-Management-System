document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-table-search]").forEach((input) => {
        const table = document.querySelector(input.dataset.tableSearch);
        if (!table) return;
        input.addEventListener("input", () => {
            const term = input.value.toLowerCase();
            table.querySelectorAll("tbody tr").forEach((row) => {
                row.hidden = !row.textContent.toLowerCase().includes(term);
            });
        });
    });

    const cardSearch = document.querySelector("[data-card-search]");
    const statusFilter = document.querySelector("[data-status-filter]");
    const jobTypeFilter = document.querySelector("[data-job-type-filter]");
    const cards = document.querySelectorAll(".job-card");
    const filterCards = () => {
        const term = cardSearch ? cardSearch.value.toLowerCase() : "";
        const status = statusFilter ? statusFilter.value.toLowerCase() : "";
        const jobType = jobTypeFilter ? jobTypeFilter.value.toLowerCase() : "";
        cards.forEach((card) => {
            const matchesText = card.dataset.search.toLowerCase().includes(term);
            const matchesStatus = !status || card.dataset.status.toLowerCase() === status;
            const matchesJobType = !jobType || card.dataset.jobType.toLowerCase() === jobType;
            card.hidden = !(matchesText && matchesStatus && matchesJobType);
        });
    };
    if (cardSearch) cardSearch.addEventListener("input", filterCards);
    if (statusFilter) statusFilter.addEventListener("change", filterCards);
    if (jobTypeFilter) jobTypeFilter.addEventListener("change", filterCards);

    const companySearch = document.querySelector("[data-company-search]");
    if (companySearch) {
        const companyCards = document.querySelectorAll(companySearch.dataset.companySearch);
        companySearch.addEventListener("input", () => {
            const term = companySearch.value.toLowerCase();
            companyCards.forEach((card) => {
                card.hidden = !card.dataset.search.toLowerCase().includes(term);
            });
        });
    }
});
