import argparse
import asyncio
import json
import os
import platform
import ssl
import logging

from aiohttp import web
import aiohttp_cors

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

ROOT = os.path.dirname(__file__)
relay = None
webcam = None

def create_local_tracks():
    global relay, webcam

    options = {"framerate": "30", "video_size": "640x480", "pixel_format": "uyvy422"}
    if relay is None:
        if platform.system() == "Darwin":
            webcam = MediaPlayer("default:none", format="avfoundation", options=options)
        elif platform.system() == "Windows":
            webcam = MediaPlayer("video=Integrated Camera", format="dshow", options=options)
        else:
            webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
        relay = MediaRelay()
    return None, relay.subscribe(webcam.video)

async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)

async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

async def offer(request):
    try:
        logging.info("Received offer request")
        params = await request.json()
        logging.info("Request JSON: %s", params)
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            if pc.connectionState == "failed":
                await pc.close()
                pcs.discard(pc)

        audio, video = create_local_tracks()

        await pc.setRemoteDescription(offer)
        for t in pc.getTransceivers():
            if t.kind == "video" and video:
                pc.addTrack(video)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return web.json_response(
            {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
        )
    except Exception as e:
        logging.exception("Error handling offer request")
        return web.Response(status=500, text="Internal Server Error")

pcs = set()

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC webcam demo")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    args = parser.parse_args()

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    logging.basicConfig(level=logging.INFO)

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)

    # Configure CORS
    cors = aiohttp_cors.setup(app)
    for route in list(app.router.routes()):
        cors.add(route, {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)
