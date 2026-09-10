(async function () {
  const video   = document.getElementById('scanner-video');
  const status  = document.getElementById('scanner-status');
  const result  = document.getElementById('scan-result');
  const form    = document.getElementById('scan-form');
  const uuidIn  = document.getElementById('scan-uuid');
  const placeNm = document.getElementById('scan-place-name');

  if (!video) return;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  let stream, rafId, running = false;

  async function startCamera() {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' }
    });
    video.srcObject = stream;
    await video.play();
    running = true;
    rafId = requestAnimationFrame(tick);
  }

  function stopCamera() {
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      video.srcObject = null;
      stream = null;
    }
  }

  function tick() {
    if (!running) return;
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width  = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = window.jsQR
        ? jsQR(img.data, img.width, img.height)
        : null;
      if (code && code.data) {
        handleCode(code.data);
        return;
      }
    }
    rafId = requestAnimationFrame(tick);
  }

  async function handleCode(raw) {
    stopCamera();
    status.textContent = 'QR detected. Looking up…';

    let uuid = raw;
    if (uuid.includes('/l/')) uuid = uuid.split('/l/').pop();

    try {
      const res = await fetch('/scan/api/lookup?uuid=' + encodeURIComponent(uuid));
      if (!res.ok) throw new Error('not found');
      const json = await res.json();
      uuidIn.value = json.place.uuid;
      placeNm.textContent = `${json.place.name} (${json.place.short_code})`;
      result.classList.remove('hidden');
      status.textContent = 'Found it. Add details below.';
    } catch (err) {
      status.textContent = 'No place found. Try again.';
      await startCamera();
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const payload = {
      uuid:  fd.get('uuid'),
      title: fd.get('title'),
      notes: fd.get('notes'),
    };
    try {
      const res = await fetch('/scan/api/add_item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('save failed');
      status.textContent = 'Saved! Ready to scan another.';
      form.reset();
      result.classList.add('hidden');
      await startCamera();
    } catch (err) {
      status.textContent = 'Save failed. Try again.';
    }
  });

  try {
    await startCamera();
  } catch (err) {
    status.textContent = 'Camera access denied or unavailable.';
  }
})();