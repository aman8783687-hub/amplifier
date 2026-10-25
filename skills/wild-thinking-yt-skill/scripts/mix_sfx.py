import subprocess, os, sys

workdir = sys.argv[1] if len(sys.argv) > 1 else "."
os.chdir(workdir)

# compute transition times from clip durations
times = []
cum = 0.0
import glob
for f in sorted(glob.glob("clips/*.mp4")):
    d = float(subprocess.check_output(
        ["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", f]).decode().strip())
    if cum > 0:
        times.append(cum)
    cum += d
open("/tmp/times.txt","w").write("\n".join("%.3f"%t for t in times))

# extract base audio from final_no_sfx.mp4
subprocess.run(["ffmpeg","-y","-i","final_no_sfx.mp4","-vn","-acodec","pcm_s16le","-ar","44100","-ac","2","/tmp/base.wav"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# mix whoosh at each transition
mixed = "/tmp/mixed.wav"
import shutil
shutil.copy("/tmp/base.wav", mixed)
i = 0
with open("/tmp/times.txt") as fh:
    for line in fh:
        t = line.strip()
        if not t:
            continue
        ms = int(float(t)*1000)
        subprocess.run(["ffmpeg","-nostdin","-y","-i",mixed,"-i","sfx/whoosh.wav",
            "-filter_complex", f"[1]adelay={ms}|{ms},volume=0.3[fx];[0][fx]amix=inputs=2:duration=first:weights=1 0.3:normalize=0",
            "-c:a","pcm_s16le","/tmp/mixed2.wav"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace("/tmp/mixed2.wav", mixed)
        i += 1
print(f"mixed {i} whooshes -> {mixed}")
