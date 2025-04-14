document.addEventListener("DOMContentLoaded", () => {
    // Simulate real-time updates (optional, can connect to API later)
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

    // Update stats every 10 seconds
    setInterval(updateStats, 10000);
    updateStats(); // Initial call
});
