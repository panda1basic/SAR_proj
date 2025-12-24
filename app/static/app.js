function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>\"]/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'
  }[c]));
}

function setStatus(msg) {
  document.getElementById("status").textContent = msg || "";
}

async function loadCars() {
  const rows = document.getElementById("rows");
  rows.innerHTML = "";
  setStatus("Загружаю список машин...");

  const res = await fetch("/cars");
  if (!res.ok) {
    setStatus("Ошибка загрузки списка: " + (await res.text()));
    return;
  }

  const data = await res.json();
  const items = data.items || [];

  if (items.length === 0) {
    setStatus("Пока пусто. Добавь первую машину 🙂");
  } else {
    setStatus("Готово. Машин в гараже: " + items.length);
  }

  for (const it of items) {
    const tr = document.createElement("tr");
    const created = it.created_at ? new Date(it.created_at).toLocaleString() : "";
    tr.innerHTML = `
      <td>${escapeHtml(it.id)}</td>
      <td>${escapeHtml(it.brand)}</td>
      <td>${escapeHtml(it.model)}</td>
      <td>${escapeHtml(it.year)}</td>
      <td>${escapeHtml(it.plate || "—")}</td>
      <td>${escapeHtml(created)}</td>
      <td>
        <div class="actions">
          <button class="danger" onclick="deleteCar(${it.id})">Удалить</button>
        </div>
      </td>
    `;
    rows.appendChild(tr);
  }
}

async function createCar() {
  const brand = document.getElementById("brand").value.trim();
  const model = document.getElementById("model").value.trim();
  const year = parseInt(document.getElementById("year").value, 10);
  const plate = document.getElementById("plate").value.trim();

  if (!brand || !model || Number.isNaN(year)) {
    setStatus("Ошибка: заполни марку, модель и год.");
    return;
  }

  setStatus("Добавляю машину...");

  const res = await fetch("/cars", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      brand,
      model,
      year,
      plate: plate ? plate : null
    })
  });

  if (!res.ok) {
    setStatus("Ошибка API: " + (await res.text()));
    return;
  }

  document.getElementById("brand").value = "";
  document.getElementById("model").value = "";
  document.getElementById("year").value = "";
  document.getElementById("plate").value = "";

  setStatus("Машина добавлена ✅");
  await loadCars();
}

async function deleteCar(id) {
  if (!confirm("Удалить машину #" + id + "?")) return;

  setStatus("Удаляю машину...");
  const res = await fetch("/cars/" + id, { method: "DELETE" });

  if (!res.ok) {
    // тут будет "Машина не найдена" если 404
    try {
      const j = await res.json();
      setStatus("Ошибка: " + (j.detail || JSON.stringify(j)));
    } catch {
      setStatus("Ошибка: " + (await res.text()));
    }
    return;
  }

  setStatus("Машина удалена ✅");
  await loadCars();
}

window.addEventListener("load", loadCars);
