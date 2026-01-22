const API_BASE = "";

const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");
const videoList = document.getElementById("videoList");
const videoPlayer = document.getElementById("videoPlayer");

let hlsInstance = null;

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString();
}

async function loadVideos() {
  videoList.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/videos`);
    if (!res.ok) throw new Error("Error al cargar videos");
    
    const videos = await res.json();
    if (!videos.length) {
      videoList.innerHTML =
        '<li class="library-item"><span class="library-name">No hay videos todavía.</span></li>';
      return;
    }

    for (const v of videos) {
      const li = document.createElement("li");
      li.className = "library-item";

      const main = document.createElement("div");
      main.className = "library-main";

      const name = document.createElement("span");
      name.className = "library-name";
      name.textContent = v.originalName || v.id;

      const meta = document.createElement("span");
      meta.className = "library-meta";
      meta.textContent = v.uploadedAt ? formatDate(v.uploadedAt) : "";
      main.appendChild(name);
      main.appendChild(meta);

      const btn = document.createElement("button");
      btn.textContent = "Reproducir";
      btn.onclick = () => playVideo(v);

      li.appendChild(main);
      li.appendChild(btn);

      videoList.appendChild(li);
    }
  } catch (err) {
    console.error(err);
    videoList.innerHTML =
      '<li class="library-item"><span class="library-name">Error al cargar la biblioteca.</span></li>';
  }
}

function playVideo(video) {
  const url = `${API_BASE}${video.playlistUrl}`;

  if (hlsInstance) {
    hlsInstance.destroy();
    hlsInstance = null;
  }

  if (videoPlayer.canPlayType("application/vnd.apple.mpegurl")) {
    videoPlayer.src = url;
  } else if (Hls.isSupported()) {
    hlsInstance = new Hls();
    hlsInstance.loadSource(url);
    hlsInstance.attachMedia(videoPlayer);
  } else {
    alert("Tu navegador no soporta HLS");
  }
}

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    alert("Selecciona un archivo de video");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  uploadBtn.disabled = true;
  uploadStatus.textContent = "Subiendo y convirtiendo video...";

  try {
    const res = await fetch(`${API_BASE}/videos`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      uploadStatus.textContent = "Error al subir el video";
      uploadBtn.disabled = false;
      return;
    }

    uploadStatus.textContent = "Video convertido correctamente";
    fileInput.value = "";
    await loadVideos();
  } catch (err) {
    console.error(err);
    uploadStatus.textContent = "Error en la comunicación con el servidor";
  } finally {
    uploadBtn.disabled = false;
  }
});

// Inicial
loadVideos();
