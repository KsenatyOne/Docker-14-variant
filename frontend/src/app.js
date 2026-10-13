const $ = (sel) => document.querySelector(sel);

const esc = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

async function api(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch (_) { /* ignore */ }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

let toastTimer;
function toast(message, isError = false) {
  const el = $("#toast");
  el.textContent = message;
  el.classList.toggle("err", isError);
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
}

/* Кнопка 1: плейлисты из БД */
async function loadPlaylists() {
  const box = $("#playlists");
  box.innerHTML = '<p class="muted">Загрузка…</p>';
  try {
    const playlists = await api("/api/playlists");
    if (!playlists.length) {
      box.innerHTML = '<p class="muted">Плейлистов пока нет. Создайте первый.</p>';
      return;
    }
    box.innerHTML = playlists
      .map(
        (p) => `
      <div class="item">
        <div>
          <strong>${esc(p.name)}</strong>
          <span class="badge">${p.tracks_count} трек(ов)</span>
          <div class="meta">${esc(p.description || "Без описания")}</div>
        </div>
        <div class="controls">
          <button data-tracks="${p.id}">Показать треки</button>
          <button class="danger" data-del="${p.id}">Удалить</button>
        </div>
      </div>
      <div class="tracks" id="tracks-${p.id}"></div>`
      )
      .join("");
  } catch (e) {
    box.innerHTML = `<p class="error">Ошибка: ${esc(e.message)}</p>`;
  }
}

async function toggleTracks(playlistId) {
  const box = document.getElementById(`tracks-${playlistId}`);
  if (!box) return;
  if (box.dataset.open === "1") {
    box.innerHTML = "";
    box.dataset.open = "0";
    return;
  }
  box.innerHTML = '<p class="muted">Загрузка треков…</p>';
  try {
    const tracks = await api(`/api/playlists/${playlistId}/tracks`);
    box.dataset.open = "1";
    box.innerHTML = tracks.length
      ? tracks
          .map(
            (t) =>
              `<div class="track">${esc(t.title)} — ${esc(t.artist)} (${esc(t.album || "—")}, ${
                t.year || "—"
              })</div>`
          )
          .join("")
      : '<p class="muted">В плейлисте нет треков.</p>';
  } catch (e) {
    box.innerHTML = `<p class="error">Ошибка: ${esc(e.message)}</p>`;
  }
}

async function deletePlaylist(playlistId) {
  if (!confirm("Удалить плейлист?")) return;
  try {
    await api(`/api/playlists/${playlistId}`, { method: "DELETE" });
    toast("Плейлист удалён");
    loadPlaylists();
  } catch (e) {
    toast(`Ошибка: ${e.message}`, true);
  }
}

async function createPlaylist(event) {
  event.preventDefault();
  const name = $("#newPlaylistName").value.trim();
  const description = $("#newPlaylistDesc").value.trim();
  if (!name) return;
  try {
    await api("/api/playlists", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, description }),
    });
    $("#playlistForm").reset();
    toast("Плейлист создан");
    loadPlaylists();
  } catch (e) {
    toast(`Ошибка: ${e.message}`, true);
  }
}

/* Кнопка 2: поиск треков через Web-сервис */
let searchResults = [];

async function searchTracks() {
  const box = $("#searchResults");
  const query = $("#searchQuery").value.trim();
  box.innerHTML = '<p class="muted">Поиск…</p>';
  try {
    const [data, playlists] = await Promise.all([
      api(`/api/search?q=${encodeURIComponent(query)}`),
      api("/api/playlists"),
    ]);
    searchResults = data.results || [];
    if (!searchResults.length) {
      box.innerHTML = '<p class="muted">Ничего не найдено.</p>';
      return;
    }
    const options = playlists
      .map((p) => `<option value="${p.id}">${esc(p.name)}</option>`)
      .join("");
    box.innerHTML = searchResults
      .map(
        (t) => `
      <div class="item">
        <div>
          <strong>${esc(t.title)}</strong>
          <span class="meta"> — ${esc(t.artist)} · ${esc(t.album || "—")} (${t.year || "—"})</span>
          <div class="meta">Жанр: ${esc(t.genre || "—")}</div>
        </div>
        <div class="controls">
          ${
            playlists.length
              ? `<select id="sel-${t.id}">${options}</select>
                 <button data-add="${t.id}">Добавить в плейлист</button>`
              : '<span class="muted">Сначала создайте плейлист</span>'
          }
        </div>
      </div>`
      )
      .join("");
  } catch (e) {
    box.innerHTML = `<p class="error">Ошибка: ${esc(e.message)}</p>`;
  }
}

async function addTrack(trackId) {
  const track = searchResults.find((t) => String(t.id) === String(trackId));
  const select = document.getElementById(`sel-${trackId}`);
  if (!track || !select) return;
  const playlistId = select.value;
  try {
    await api(`/api/playlists/${playlistId}/tracks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: track.title,
        artist: track.artist,
        album: track.album,
        year: track.year,
        duration_sec: track.duration_sec,
      }),
    });
    toast(`«${track.title}» добавлен в плейлист`);
  } catch (e) {
    toast(`Ошибка: ${e.message}`, true);
  }
}

/* Делегирование кликов */
document.addEventListener("click", (event) => {
  const target = event.target.closest("button");
  if (!target) return;
  if (target.id === "btnPlaylists") loadPlaylists();
  else if (target.id === "btnSearch") searchTracks();
  else if (target.dataset.tracks) toggleTracks(target.dataset.tracks);
  else if (target.dataset.del) deletePlaylist(target.dataset.del);
  else if (target.dataset.add) addTrack(target.dataset.add);
});

$("#playlistForm").addEventListener("submit", createPlaylist);
$("#searchQuery").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    searchTracks();
  }
});

loadPlaylists();
