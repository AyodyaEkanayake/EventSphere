
"use strict";

const loginSection = document.getElementById("loginSection");
const dashboardSection = document.getElementById("dashboardSection");
const dashboardMessage = document.getElementById("dashboardMessage");
const refreshButton = document.getElementById("refreshButton");
const logoutButton = document.getElementById("logoutButton");

const adminToken = sessionStorage.getItem("eventsphere_access_token");

function showMessage(message, success = false) {
    dashboardMessage.textContent = message;
    dashboardMessage.className = success
        ? "message success-message"
        : "message";
}

function addCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value ?? "";
    row.appendChild(cell);
}

function logout() {
    sessionStorage.removeItem("eventsphere_access_token");
    sessionStorage.removeItem("eventsphere_admin_token");
    window.location.href = "/login";
}

async function loadDashboard() {
    if (!adminToken) {
        window.location.href = "/login";
        return;
    }

    try {
        // Confirm the logged-in user's role
        const userResponse = await fetch("/auth/me", {
            headers: { "Authorization": `Bearer ${adminToken}` }
        });

        if (!userResponse.ok) {
            logout();
            return;
        }

        const user = await userResponse.json();

        if (user.role !== "admin") {
            if (user.role === "attendee") {
                window.location.href = "/attendee";
            } else if (user.role === "gate_staff") {
                window.location.href = "/scanner";
            } else {
                logout();
            }
            return;
        }

        loginSection.classList.add("hidden");
        dashboardSection.classList.remove("hidden");
        showMessage("Loading dashboard...");

        const response = await fetch("/dashboard/", {
            headers: { "Authorization": `Bearer ${adminToken}` }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to load dashboard.");
        }

        document.getElementById("totalEvents").textContent =
            data.summary.total_events;

        document.getElementById("totalTickets").textContent =
            data.summary.total_tickets_sold;

        document.getElementById("totalRevenue").textContent =
            "LKR " + Number(data.summary.total_revenue).toLocaleString();

        document.getElementById("totalCheckins").textContent =
            data.summary.total_check_ins;

        const capacityTable = document.getElementById("capacityTable");
        capacityTable.replaceChildren();

        if (!data.event_capacity || data.event_capacity.length === 0) {
            const row = capacityTable.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 5;
            cell.textContent = "No ticket categories available.";
        } else {
            data.event_capacity.forEach(item => {
                const row = capacityTable.insertRow();
                addCell(row, item.event_title);
                addCell(row, item.ticket_category);
                addCell(row, item.total_quantity);
                addCell(row, item.sold_quantity);
                addCell(row, item.available_quantity);
            });
        }

        const logsTable = document.getElementById("agentLogsTable");
        logsTable.replaceChildren();

        if (!data.agent_logs || data.agent_logs.length === 0) {
            const row = logsTable.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 5;
            cell.textContent = "No agent messages recorded.";
        } else {
            data.agent_logs.forEach(log => {
                const row = logsTable.insertRow();
                addCell(row, log.sender);
                addCell(row, log.receiver);
                addCell(row, log.performative);
                addCell(row, JSON.stringify(log.content));

                const date = log.created_at
                    ? new Date(log.created_at).toLocaleString()
                    : "";

                addCell(row, date);
            });
        }

        showMessage("Dashboard loaded successfully!", true);

    } catch (error) {
        console.error("Dashboard error:", error);
        showMessage("Error: " + error.message);
    }
}

refreshButton.addEventListener("click", loadDashboard);
logoutButton.addEventListener("click", logout);

loadDashboard();
