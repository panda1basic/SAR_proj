async function loadItems() {
  const rows = document.getElementById("rows");
  rows.innerHTML = "";

  const res = await fetch("/notes");
  const data = await res.json();

  for (const it of data.items) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${it.id}</td><td>${escapeHtml(it.text)}</td>`;
    rows.appendChild(tr);
  }
}

async function createItem() {
  const status = document.getElementById("status");
  status.textContent = "Отправляю запрос...";

  const text = document.getElementById("text").value.trim();
  if (!text) {
    status.textContent = "Ошибка: заполните text.";
    return;
  }

  const res = await fetch("/notes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });

  if (!res.ok) {
    const err = await res.text();
    status.textContent = "Ошибка API: " + err;
    return;
  }

  const created = await res.json();
  status.textContent = `Создано: id=${created.id}`;
  document.getElementById("text").value = "";
  await loadItems();
}

function escapeHtml(s) {
  return s.replace(/[&<>"]/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'
  }[c]));
}

window.addEventListener("load", loadItems);
