/* Each long video is initialized only after an explicit play request. */
document.querySelectorAll('[data-hls]').forEach(video => {
  const frame = video.closest('figure');
  const button = frame.querySelector('.hls-play');
  const message = frame.querySelector('.media-error');
  let player;
  let started = false;
  let recovering = false;
  const fail = () => {
    message.textContent = 'The video could not load. Check your connection and try again.';
    message.hidden = false;
    button.hidden = false;
    button.disabled = false;
    started = false;
    if (player) { player.destroy(); player = null; }
  };
  const play = () => {
    button.hidden = true;
    button.disabled = false;
    video.play().catch(() => {
      message.textContent = 'Use the video controls to start playback.';
      message.hidden = false;
    });
  };
  button.addEventListener('click', () => {
    message.hidden = true;
    button.disabled = true;
    if (started) { play(); return; }
    started = true;
    recovering = false;
    if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = video.dataset.hls;
      video.addEventListener('loadedmetadata', play, { once: true });
      video.addEventListener('error', fail, { once: true });
      video.load();
    } else if (window.Hls && Hls.isSupported()) {
      player = new Hls({ maxBufferLength: 30, maxMaxBufferLength: 60, backBufferLength: 30 });
      player.on(Hls.Events.MANIFEST_PARSED, play);
      player.on(Hls.Events.ERROR, (_event, data) => {
        if (!data.fatal) return;
        if (data.type === Hls.ErrorTypes.MEDIA_ERROR && !recovering) {
          recovering = true;
          player.recoverMediaError();
        } else { fail(); }
      });
      player.loadSource(video.dataset.hls);
      player.attachMedia(video);
    } else {
      message.textContent = 'This browser cannot play this video. Please use a recent version of Safari, Chrome, Firefox, or Edge.';
      message.hidden = false;
      button.hidden = true;
    }
  });
  video.addEventListener('pause', () => { if (player) player.stopLoad(); });
  video.addEventListener('play', () => { if (player) player.startLoad(-1); });
});
document.querySelectorAll('video').forEach(video => {
  video.addEventListener('play', () => {
    document.querySelectorAll('video').forEach(other => { if (other !== video) other.pause(); });
  });
});
