
let html5QrCode = null;

async function checkInTicket(scannedCode = null) {

    const token = document.getElementById("token").value.trim();
    const eventId = document.getElementById("eventId").value.trim();

    const ticketCode = scannedCode ||
        document.getElementById("ticketCode").value.trim();

    const resultBox = document.getElementById("result");

    if (!token || !eventId || !ticketCode) {
        resultBox.className = "error";
        resultBox.textContent =
            "Please enter the access token, event ID and ticket code.";
        return;
    }

    resultBox.className = "";
    resultBox.textContent = "Checking ticket...";

    try {

        const response = await fetch(
            `/tickets/scan/${eventId}/${encodeURIComponent(ticketCode)}`,
            {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (response.ok) {

            resultBox.className = "success";

            resultBox.textContent =
                "TICKET VALIDATED SUCCESSFULLY!\n\n" +
                "Entry Allowed!\n" +
                "Ticket ID: " + data.ticket_id + "\n" +
                "Ticket Code: " + data.ticket_code + "\n" +
                "Event ID: " + data.event_id + "\n" +
                "Status: " + data.status + "\n" +
                "Checked In: " + data.checked_in_at;

        } else {

            resultBox.className = "error";

            resultBox.textContent =
                "TICKET VALIDATION FAILED!\n\n" +
                (data.detail || "Unable to validate ticket.");

        }

    } catch (error) {

        resultBox.className = "error";
        resultBox.textContent =
            "Server connection error: " + error.message;

    }
}


function startScanner() {

    if (typeof Html5QrcodeScanner === "undefined") {
        alert("QR scanner library could not be loaded. Use manual entry.");
        return;
    }

    if (html5QrCode !== null) {
        return;
    }

    html5QrCode = new Html5QrcodeScanner(
        "reader",
        {
            fps: 10,
            qrbox: { width: 250, height: 250 }
        },
        false
    );

    html5QrCode.render(
        async function (decodedText) {

            document.getElementById("ticketCode").value = decodedText;

            await checkInTicket(decodedText);

            stopScanner();

        },
        function (errorMessage) {
            // Ignore normal scanning errors while searching for a QR code.
        }
    );
}


function stopScanner() {

    if (html5QrCode !== null) {

        html5QrCode.clear().then(() => {
            html5QrCode = null;
        }).catch(error => {
            console.error("Scanner stop error:", error);
            html5QrCode = null;
        });

    }
}
