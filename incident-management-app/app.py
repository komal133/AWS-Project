from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

incidents = [
    {
        "id": 1,
        "title": "API latency spike",
        "severity": "High",
        "status": "Open",
        "assignee": "Alicia",
        "description": "Customers are experiencing slow responses from the API gateway."
    },
    {
        "id": 2,
        "title": "Database failover",
        "severity": "Critical",
        "status": "In Progress",
        "assignee": "Jordan",
        "description": "Replica failover is underway while the primary is stabilized."
    },
    {
        "id": 3,
        "title": "Login page timeout",
        "severity": "Medium",
        "status": "Resolved",
        "assignee": "Priya",
        "description": "The issue was resolved after clearing the authentication cache."
    }
]


@app.route("/")
def home():
    return render_template_string("""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Incident Management</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #07111f;
      --panel: rgba(15, 23, 42, 0.9);
      --panel-2: rgba(30, 41, 59, 0.9);
      --border: rgba(148, 163, 184, 0.2);
      --text: #e2e8f0;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --accent-2: #818cf8;
      --danger: #f87171;
      --warning: #fbbf24;
      --success: #34d399;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
      background: linear-gradient(135deg, var(--bg), #1e293b);
      color: var(--text);
      min-height: 100vh;
    }
    .shell { max-width: 1200px; margin: 0 auto; padding: 24px; }
    .hero {
      background: linear-gradient(120deg, rgba(56, 189, 248, 0.2), rgba(129, 140, 248, 0.2));
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 24px;
      margin-bottom: 20px;
      box-shadow: 0 12px 40px rgba(0,0,0,0.25);
    }
    .hero h1 { margin: 0 0 6px; font-size: 28px; }
    .hero p { margin: 0; color: var(--muted); }
    .stats {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 16px;
      backdrop-filter: blur(10px);
    }
    .card h3 { margin: 0 0 4px; font-size: 24px; }
    .card p { margin: 0; color: var(--muted); }
    .content {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 20px;
    }
    form, .incident-list {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }
    label { display: block; margin-bottom: 8px; color: var(--muted); font-size: 13px; }
    input, select, textarea, button {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: var(--panel-2);
      color: var(--text);
      padding: 10px 12px;
      margin-bottom: 12px;
      font-size: 14px;
    }
    button {
      cursor: pointer;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
      border: none;
      font-weight: 600;
      transition: transform 0.15s ease;
    }
    button:hover { transform: translateY(-1px); }
    .incident-list { display: flex; flex-direction: column; gap: 12px; }
    .incident-card {
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      background: rgba(15, 23, 42, 0.8);
    }
    .incident-card header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }
    .pill {
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .severity-high { background: rgba(248, 113, 113, 0.18); color: #fecaca; }
    .severity-critical { background: rgba(251, 191, 36, 0.2); color: #fde68a; }
    .severity-medium { background: rgba(52, 211, 153, 0.18); color: #bbf7d0; }
    .status-row { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
    .status-btn {
      width: auto;
      padding: 7px 10px;
      margin: 0;
      font-size: 12px;
      background: rgba(51, 65, 85, 0.8);
      color: var(--text);
      border: 1px solid var(--border);
    }
    .status-btn.active {
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
    }
    .empty { color: var(--muted); text-align: center; padding: 16px 0; }
    @media (max-width: 900px) {
      .content { grid-template-columns: 1fr; }
      .stats { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <h1>Incident Management Portal</h1>
      <p>Track, triage, and resolve incidents with a fast and modern workflow.</p>
    </section>

    <section class="stats">
      <div class="card">
        <h3 id="open-count">0</h3>
        <p>Open</p>
      </div>
      <div class="card">
        <h3 id="progress-count">0</h3>
        <p>In Progress</p>
      </div>
      <div class="card">
        <h3 id="resolved-count">0</h3>
        <p>Resolved</p>
      </div>
    </section>

    <section class="content">
      <form id="incident-form">
        <label>Title</label>
        <input name="title" placeholder="Service outage" required>

        <label>Severity</label>
        <select name="severity">
          <option value="Low">Low</option>
          <option value="Medium" selected>Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>

        <label>Status</label>
        <select name="status">
          <option value="Open" selected>Open</option>
          <option value="In Progress">In Progress</option>
          <option value="Resolved">Resolved</option>
        </select>

        <label>Assignee</label>
        <input name="assignee" placeholder="Name">

        <label>Description</label>
        <textarea name="description" rows="4" placeholder="Describe the incident"></textarea>

        <button type="submit">Create Incident</button>
      </form>

      <div id="incident-list" class="incident-list"></div>
    </section>
  </div>

  <script>
    const incidentList = document.getElementById("incident-list");
    const form = document.getElementById("incident-form");
    const openCount = document.getElementById("open-count");
    const progressCount = document.getElementById("progress-count");
    const resolvedCount = document.getElementById("resolved-count");

    function severityClass(severity) {
      return severity.toLowerCase();
    }

    function renderIncidents(items) {
      if (!items.length) {
        incidentList.innerHTML = '<div class="empty">No incidents yet.</div>';
        return;
      }

      const counts = { Open: 0, "In Progress": 0, Resolved: 0 };
      items.forEach(item => counts[item.status] = (counts[item.status] || 0) + 1);

      openCount.textContent = counts.Open || 0;
      progressCount.textContent = counts["In Progress"] || 0;
      resolvedCount.textContent = counts.Resolved || 0;

      incidentList.innerHTML = items.map(item => `
        <div class="incident-card">
          <header>
            <strong>${item.title}</strong>
            <span class="pill severity-${severityClass(item.severity)}">${item.severity}</span>
          </header>
          <div style="color: var(--muted); margin-bottom: 8px;">${item.description}</div>
          <div style="font-size: 13px; color: var(--muted);">Assignee: ${item.assignee || "Unassigned"}</div>
          <div class="status-row">
            ${["Open", "In Progress", "Resolved"].map(status => `
              <button class="status-btn ${item.status === status ? "active" : ""}" data-id="${item.id}" data-status="${status}">
                ${status}
              </button>
            `).join("")}
          </div>
        </div>
      `).join("");
    }

    async function loadIncidents() {
      const res = await fetch("/api/incidents");
      const data = await res.json();
      renderIncidents(data);
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      const res = await fetch("/api/incidents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      if (res.ok) {
        form.reset();
        await loadIncidents();
      }
    });

    document.addEventListener("click", async (event) => {
      if (event.target.classList.contains("status-btn")) {
        const id = event.target.dataset.id;
        const status = event.target.dataset.status;
        const res = await fetch(`/api/incidents/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status })
        });
        if (res.ok) {
          await loadIncidents();
        }
      }
    });

    loadIncidents();
  </script>
</body>
</html>
    """)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    return jsonify(incidents)


@app.route("/api/incidents", methods=["POST"])
def create_incident():
    payload = request.get_json(silent=True) or {}
    new_incident = {
        "id": max((item["id"] for item in incidents), default=0) + 1,
        "title": payload.get("title", "Untitled incident"),
        "severity": payload.get("severity", "Medium"),
        "status": payload.get("status", "Open"),
        "assignee": payload.get("assignee", "Unassigned"),
        "description": payload.get("description", "No details provided.")
    }
    incidents.append(new_incident)
    return jsonify(new_incident), 201


@app.route("/api/incidents/<int:incident_id>", methods=["PATCH"])
def update_incident(incident_id):
    payload = request.get_json(silent=True) or {}
    for incident in incidents:
        if incident["id"] == incident_id:
            if "status" in payload:
                incident["status"] = payload["status"]
            if "title" in payload:
                incident["title"] = payload["title"]
            if "severity" in payload:
                incident["severity"] = payload["severity"]
            if "assignee" in payload:
                incident["assignee"] = payload["assignee"]
            if "description" in payload:
                incident["description"] = payload["description"]
            return jsonify(incident)
    return jsonify({"error": "Incident not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
