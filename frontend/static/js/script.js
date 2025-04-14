document.addEventListener("DOMContentLoaded", () => {
    const updateStats = async () => {
        try {
            const response = await fetch("/stats");
            const stats = await response.json();
            document.getElementById("total").textContent = stats.total;
            document.getElementById("approved").textContent = stats.approved;
            document.getElementById("rejected").textContent = stats.rejected;
            document.getElementById("rejection-rate").textContent = stats.rejection_rate + "%";
        } catch (error) {
            console.error("Error updating stats:", error);
        }
    };
    setInterval(updateStats, 10000); // Update every 10s
    updateStats();
});
