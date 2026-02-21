let page = 1;

async function loadEvents() {

    try {
        const res = await fetch(`/events?page=${page}`);
        const data = await res.json();

        const feed = document.getElementById("feed");
        feed.innerHTML = "";

        if (data.length === 0) {
            feed.innerHTML = "<p class='empty'>No more events</p>";
            return;
        }

        data.forEach(event => {

            let text = "";
            let cssClass = "card";

            if (event.action === "PUSH") {
                text = `📌 ${event.author} pushed to ${event.to_branch}`;
                cssClass += " push";
            }

            if (event.action === "PULL_REQUEST") {
                text = `🔁 ${event.author} opened PR ${event.from_branch} → ${event.to_branch}`;
                cssClass += " pr";
            }

            if (event.action === "MERGE") {
                text = `✅ ${event.author} merged ${event.from_branch} → ${event.to_branch}`;
                cssClass += " merge";
            }

            feed.innerHTML += `
                <div class="${cssClass}">
                    <div>${text}</div>
                    <div class="meta">${event.timestamp}</div>
                </div>
            `;
        });

    } catch (err) {
        console.error("Error loading events:", err);
    }
}

function nextPage() {
    page++;
    loadEvents();
}

function prevPage() {
    if (page > 1) {
        page--;
        loadEvents();
    }
}

loadEvents();

/* ✅ Theme Toggle */

const toggle = document.getElementById("themeToggle");

function setTheme(theme) {
    document.body.className = theme;
    localStorage.setItem("theme", theme);
    toggle.checked = theme === "light";
}

toggle.addEventListener("change", () => {
    setTheme(toggle.checked ? "light" : "dark");
});

/* ✅ Load Saved Theme */

const savedTheme = localStorage.getItem("theme") || "dark";
setTheme(savedTheme);