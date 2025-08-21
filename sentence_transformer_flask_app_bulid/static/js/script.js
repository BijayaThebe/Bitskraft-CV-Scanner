document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();
  const formData = new FormData();
  const jobDesc = document.getElementById("job_description").value;
  const files = document.getElementById("resumes").files;

  if (!jobDesc) {
    alert("Please enter job requirements.");
    return;
  }
  if (files.length === 0) {
    alert("Please upload at least one resume.");
    return;
  }

  formData.append("job_description", jobDesc);
  for (let file of files) {
    formData.append("resumes", file);
  }

  document.getElementById("loading").classList.remove("hidden");
  document.getElementById("results").classList.add("hidden");

  try {
    const res = await fetch("/evaluate", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (data.error) {
      alert("Error: " + data.error);
      document.getElementById("loading").classList.add("hidden");
      return;
    }

    displayResults(data.results);
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("results").classList.remove("hidden");
  } catch (err) {
    alert("Failed to process: " + err.message);
    document.getElementById("loading").classList.add("hidden");
  }
});

function displayResults(results) {
  const tbody = document.getElementById("resultBody");
  const topNSelect = document.getElementById("topN");

  function renderTable(n) {
    tbody.innerHTML = "";
    const limit = n === "all" ? results.length : parseInt(n);
    const toShow = results.slice(0, limit);

    toShow.forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${r.Rank}</strong></td>
        <td>${r["Resume Name"]}</td>
        <td><span class="score">${r["Overall Match Score"]}</span></td>
        <td>${r["Keywords Matched"] || "-"}</td>
        <td>${r["Semantic Relevance"]}</td>
        <td><span class="tag ${r.Summary.toLowerCase().replace(" ", "-")}">${r.Summary}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  renderTable(topNSelect.value);
  topNSelect.onchange = () => renderTable(topNSelect.value);

  document.getElementById("exportCSV").onclick = () => {
    let csv = "Resume Name,Match Score,Keywords Matched,Semantic Relevance,Summary\n";
    results.forEach(r => {
      csv += `"${r["Resume Name"]}",${r["Overall Match Score"]},"${r["Keywords Matched"]}",${r["Semantic Relevance"]},"${r.Summary}"\n`;
    });
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "resume_matches.csv";
    a.click();
  };
}