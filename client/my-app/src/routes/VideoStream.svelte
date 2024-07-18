<script>
  import { onMount } from 'svelte';

  let videoElement;

  async function startWebRTC() {
    const pc = new RTCPeerConnection({
      sdpSemantics: 'unified-plan',
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });

    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    try {
      const response = await fetch('http://localhost:8080/offer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sdp: pc.localDescription.sdp,
          type: pc.localDescription.type
        })
      });

      if (!response.ok) {
        console.error('Failed to fetch offer');
        return;
      }

      const answer = await response.json();
      console.log("Received answer:", answer);
      await pc.setRemoteDescription(answer);

      pc.addEventListener('track', (event) => {
        console.log("Track event received:", event);
        if (event.track.kind === 'video') {
          console.log("Video track received:", event.track);
          const [stream] = event.streams;
          console.log("Video stream:", stream);
          videoElement.srcObject = stream;
          videoElement.play().catch(error => {
            console.error('Error playing video:', error);
          });
        }
      });

      pc.addEventListener('iceconnectionstatechange', () => {
        console.log("ICE connection state change:", pc.iceConnectionState);
      });

      pc.addEventListener('signalingstatechange', () => {
        console.log("Signaling state change:", pc.signalingState);
      });

    } catch (error) {
      console.error('Error during WebRTC setup:', error);
    }
  }

  onMount(() => {
    startWebRTC();
  });
</script>

<video bind:this={videoElement} autoplay playsinline></video>

<style>
  video {
    width: 100%;
    max-width: 640px;
    margin: auto;
    display: block;
  }
</style>
