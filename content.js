console.log("[AI Hook] Loaded");

let lastMessage = "";

function scrapeAndSend() {
    const messages = document.querySelectorAll(".DTp27d");

    if (!messages.length) {
        console.log("No messages found");
        return;
    }

    const latest = messages[messages.length - 1];

    const text = latest.innerText.trim();

    if (!text) return;

    if (text === lastMessage) return;

    lastMessage = text;

    console.log("Latest message:", text);

    const payload = {
        sender: "Unknown Sender",
        message: text
    };

    console.log("Sending", payload);

    fetch("http://127.0.0.1:5000/triage", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
    .then(async (res) => {
        console.log("HTTP Status:", res.status);
        console.log(await res.text());
    })
    .catch(err => {
        console.error("Fetch failed:", err);
    });
}

const observer = new MutationObserver(() => {
    scrapeAndSend();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

setTimeout(scrapeAndSend, 2000);