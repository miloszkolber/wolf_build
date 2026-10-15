"""Isolated VA encode probe. Not a Moonlight/session/zero-copy acceptance record."""
import json
import subprocess
import time

results={}
for codec, candidates, parser in (
    ("h264",("vah264lpenc","vah264enc"),"h264parse"),
    ("hevc",("vah265lpenc","vah265enc"),"h265parse"),
    ("av1",("vaav1lpenc","vaav1enc"),"av1parse"),
):
    factory=next((name for name in candidates if subprocess.run(["gst-inspect-1.0",name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0),None)
    if factory is None:
        results[codec]={"status":"unsupported-or-unavailable","capability_evidence":"No matching VA encoder factory registered by the driver"}
        continue
    start=time.monotonic()
    output=subprocess.run(["gst-launch-1.0","-q","videotestsrc","num-buffers=60","!","video/x-raw,width=1280,height=720,framerate=60/1","!","vapostproc","!",factory,"!",parser,"!","fakesink"],capture_output=True,text=True,timeout=60)
    results[codec]={"factory":factory,"status":"pass" if output.returncode==0 else "fail","seconds":round(time.monotonic()-start,3),"stderr":output.stderr[-2000:]}
print(json.dumps(results,indent=2))
if not any(item["status"]=="pass" for item in results.values()) or any(item["status"]=="fail" for item in results.values()):
    raise SystemExit(1)
