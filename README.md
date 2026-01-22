# Python Video Server (CPU HLS 1080p)

Servidor HTTP para procesamiento de video usando **FFmpeg (CPU)** y generación de **HLS (Vod)**.

- Upload de video (POST multipart/form-data)
- Conversión a 1080p vía `libx264`
- Generación de segmentos `.ts` + playlist `index.m3u8`
- Listado de videos generados
- Cleanup automático del RAW
- API documentada con Swagger/OpenAPI

---

## 📦 Requisitos

### 1. Python & FastAPI

```bash
Python 3.10+
pip install -r requirements.txt
```

### 2. FFmpeg (CPU)

Debe estar instalado y accesible en PATH  
Ejemplo en Windows:

```
C:\ffmpeg\ffmpeg-8.0.1-full_build-shared\bin
```

Probar:

```bash
ffmpeg -version
ffprobe -version
```

---

## 📂 Estructura

```
upload/
 ├── raw/         # Videos antes de convertir (se limpian automáticamente)
 └── videos/
      └── <id>/
          ├── index.m3u8     # playlist HLS
          ├── index0.ts      # segmentos
          ├── index1.ts
          └── metadata.json
```

ID estilo NestJS:

```
<timestamp>-<nombre-limpio>
```

---

## 🚀 Levantar el servidor

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📘 Swagger UI

```
http://localhost:8000/swagger
```

Endpoints:

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/videos/videos` | Listar videos |
| POST | `/videos/videos` | Upload + conversión HLS |
| GET | `/streams/:id/index.m3u8` | Consumir HLS |

---

## 🎥 Test con Swagger

1. Abrir `/swagger`
2. Ir a `POST /videos/videos`
3. Subir un `.mp4`
4. Esperar conversión (log muestra %)
5. Ir a `GET /videos/videos`
6. Obtener `playlistUrl`

Ejemplo `playlistUrl`:

```
/streams/1768842220000-trbx304yamaha/index.m3u8
```

---

## 🎬 Test HLS (Player)

Puedes probar con VLC:

```
Media > Open Network Stream > http://localhost:8000/streams/<id>/index.m3u8
```

O con `<video>` en web:

```html
<video controls src="http://localhost:8000/streams/<id>/index.m3u8"></video>
```

---

## ♻ Limpieza

El video RAW se borra automáticamente al final del proceso:

```
upload/raw/
```

Nunca se exponen los RAW al cliente.

---

## 🏁 Próximos pasos opcionales

- Multi-resolución (360p, 720p, 1080p)
- GPU (NVENC)
- Cola (RabbitMQ) estilo WBC
- Auth bearer para producción

---

## 📄 Licencia

