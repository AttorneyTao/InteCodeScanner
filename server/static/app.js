/* eslint-env browser */
const form   = document.getElementById("uploadForm");
const loader = document.getElementById("loader");
const result = document.getElementById("result");
const dlLink = document.getElementById("downloadLink");
const tableW = document.getElementById("tableWrap");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = form.querySelector("input[type=file]");
  if (!fileInput.files.length) return;
  const csvFile = fileInput.files[0];

  loader.classList.remove("d-none");
  result.classList.add("d-none");

  const body = new FormData();
  body.append("file", csvFile);

  try {
    const resp = await fetch("/enrich/csv", {method: "POST", body});
    if (!resp.ok) throw new Error(await resp.text());
    const blob = await resp.blob();

    // create download link
    const url = URL.createObjectURL(blob);
    dlLink.href = url;

    // preview first 50 rows
    const text = await blob.text();
    const parsed = Papa.parse(text, {header: true, preview: 50});
    renderTable(parsed.data);

    result.classList.remove("d-none");
  } catch (err) {
    alert("Error: " + err);
  } finally {
    loader.classList.add("d-none");
  }
});

function renderTable(rows) {
  if (!rows.length) return;
  const cols = Object.keys(rows[0]);
  let html = "<table class='table table-striped table-sm'><thead><tr>";
  cols.forEach(c => html += `<th>${c}</th>`);
  html += "</tr></thead><tbody>";
  rows.forEach(r => {
    html += "<tr>";
    cols.forEach(c => html += `<td>${r[c] || ""}</td>`);
    html += "</tr>";
  });
  html += "</tbody></table>";
  tableW.innerHTML = html;
}
