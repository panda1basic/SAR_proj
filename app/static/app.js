async function loadItems() {
  const rows = document.getElementById("rows");
  rows.innerHTML = "";
  const res = await fetch("/api/items");
  const data = await res.json();

  for (const it of data) {
    const tr = document.createElement("tr");
    tr.innerHTML = <td></td><td></td><td></td><td></td>;
    rows.appendChild(tr);
  }
}

async function createItem() {
  const status = document.getElementById("status");
  status.textContent = "Отправляю запрос...";
  const name = document.getElementById("name").value.trim();
  const value = parseInt(document.getElementById("value").value, 10);

  if (!name || Number.isNaN(value)) {
    status.textContent = "Ошибка: заполните name и value (целое число).";
    return;
  }

  const res = await fetch("/api/items", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, value })
  });

  if (!res.ok) {
    const err = await res.text();
    status.textContent = "Ошибка API: " + err;
    return;
  }

  const created = await res.json();
  status.textContent = Создано: id=;
  document.getElementById("name").value = "";
  document.getElementById("value").value = "";
  await loadItems();
}

function escapeHtml(s) {
  return s.replace(/[&<>\"]/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'
  }[c]));
}

window.addEventListener("load", loadItems);
