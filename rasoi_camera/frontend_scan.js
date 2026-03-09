/**
 * RasoiAI Camera — Frontend scan controls.
 *
 * Drop this into any HTML page served from the RPi:
 *   <button id="scan-btn" onclick="triggerRemoteScan()">📸 Scan</button>
 *   <button id="forward-btn" onclick="triggerScanAndForward()">🍳 Scan & Get Recipes</button>
 *   <img id="preview" alt="Latest capture" />
 *   <p id="status-text"></p>
 *   <div id="results"></div>
 */

const API_BASE = window.location.origin + "/api/camera";

/**
 * Trigger a camera capture and display the resulting image.
 */
async function triggerRemoteScan() {
    const btn = document.getElementById("scan-btn");
    const statusEl = document.getElementById("status-text");
    const preview = document.getElementById("preview");

    btn.disabled = true;
    statusEl.textContent = "📷 Capturing…";

    try {
        const res = await fetch(`${API_BASE}/scan`, { method: "POST" });
        const data = await res.json();

        if (!res.ok) {
            statusEl.textContent = `❌ ${data.detail || "Capture failed"}`;
            return;
        }

        statusEl.textContent = `✅ ${data.message}`;

        // Load the latest image with a cache-busting timestamp
        preview.src = `${API_BASE}/latest-image?t=${Date.now()}`;
        preview.style.display = "block";
    } catch (err) {
        statusEl.textContent = `❌ Network error: ${err.message}`;
    } finally {
        btn.disabled = false;
    }
}

/**
 * Full pipeline: Capture → Analyse → Forward → Display recipes.
 */
async function triggerScanAndForward() {
    const btn = document.getElementById("forward-btn");
    const statusEl = document.getElementById("status-text");
    const preview = document.getElementById("preview");
    const resultsEl = document.getElementById("results");

    btn.disabled = true;
    statusEl.textContent = "📷 Capturing and analysing…";
    resultsEl.innerHTML = "";

    try {
        const res = await fetch(`${API_BASE}/scan-and-forward`, { method: "POST" });
        const data = await res.json();

        if (!res.ok) {
            statusEl.textContent = `❌ ${data.detail || "Pipeline failed"}`;
            return;
        }

        // Show the captured image
        preview.src = `${API_BASE}/latest-image?t=${Date.now()}`;
        preview.style.display = "block";

        // Display detected ingredients
        const ingredients = data.ingredients_detected || [];
        statusEl.textContent = `✅ Found ${ingredients.length} ingredient(s): ${ingredients.join(", ")}`;

        // Display recipe results
        const recipes = data.recipes;
        if (recipes && recipes.recipes) {
            let html = "<h3>🍳 Recipe Recommendations</h3><ul>";
            for (const r of recipes.recipes) {
                html += `<li><strong>${r.recipe}</strong> (score: ${r.match_score || "–"})</li>`;
            }
            html += "</ul>";
            resultsEl.innerHTML = html;
        }
    } catch (err) {
        statusEl.textContent = `❌ Network error: ${err.message}`;
    } finally {
        btn.disabled = false;
    }
}
