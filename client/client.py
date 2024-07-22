import cv2
import numpy as np
import asyncio
import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription

async def main():
    pc = RTCPeerConnection()

    @pc.on("track")
    def on_track(track):
        print("Track received")
        if track.kind == "video":
            async def read_track():
                while True:
                    frame = await track.recv()
                    img = frame.to_ndarray(format="rgb24")
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    cv2.imshow("Webcam", img_bgr)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            asyncio.create_task(read_track())

    # Add transceivers for video and audio
    pc.addTransceiver('video', direction='recvonly')
    pc.addTransceiver('audio', direction='recvonly')

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    async with aiohttp.ClientSession() as session:
        payload = {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
        print("Sending payload:", payload)
        async with session.post("http://192.168.0.110:8080/offer", json=payload) as response:
            if response.headers['Content-Type'].startswith('application/json'):
                answer = await response.json()
                print("Received answer:", answer)
                sdp = answer['sdp']
                type_ = answer['type']
            else:
                print("Unexpected response type:", response.headers['Content-Type'])
                print(await response.text())
                return

    answer = RTCSessionDescription(sdp=sdp, type=type_)
    await pc.setRemoteDescription(answer)

    # No need to await on the track attribute
    # You can just let the on_track callback handle the tracks as they are received
    await asyncio.sleep(3600)  # Keep the program running to receive video

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
