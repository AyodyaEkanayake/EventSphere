
"use strict";

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    const existingToken = sessionStorage.getItem("eventsphere_access_token");

    // Already logged in? Redirect according to role.
    if (existingToken) {
        checkExistingLogin(existingToken);
    }

    async function checkExistingLogin(token) {
        try {
            const response = await fetch("/auth/me", {
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (!response.ok) {
                sessionStorage.removeItem("eventsphere_access_token");
                return;
            }

            const user = await response.json();
            redirectByRole(user.role);
        } catch (error) {
            console.error(error);
        }
    }

    function redirectByRole(role) {
        if (role === "admin") {
            window.location.href = "/admin";
        } else if (role === "attendee") {
            window.location.href = "/attendee";
        } else if (role === "gate_staff") {
            window.location.href = "/scanner";
        } else {
            document.getElementById("loginMessage").textContent =
                "Your account role is not supported.";
        }
    }

    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const button = document.getElementById("loginButton");
        const message = document.getElementById("loginMessage");

        button.disabled = true;
        button.textContent = "Logging in...";
        message.textContent = "";

        try {
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);

            const response = await fetch("/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: formData.toString()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Login failed.");
            }

            sessionStorage.setItem(
                "eventsphere_access_token",
                data.access_token
            );

            const userResponse = await fetch("/auth/me", {
                headers: {
                    "Authorization": `Bearer ${data.access_token}`
                }
            });

            if (!userResponse.ok) {
                throw new Error("Could not retrieve user details.");
            }

            const user = await userResponse.json();
            redirectByRole(user.role);

        } catch (error) {
            message.textContent = error.message;
            sessionStorage.removeItem("eventsphere_access_token");
        } finally {
            button.disabled = false;
            button.textContent = "Login";
        }
    });
}

// Shared logout function for all dashboards
function logoutEventSphere() {
    sessionStorage.removeItem("eventsphere_access_token");
    sessionStorage.removeItem("eventsphere_admin_token");
    window.location.href = "/login";
}
