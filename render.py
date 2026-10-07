import subprocess, sys, os, shutil
r = subprocess.run([sys.executable, "tools/fetch_trends.py"], capture_output=True, text=True)
os.makedirs("out/tr", exist_ok=True)
open("out/tr/run.log", "w").write(r.stdout + "\n---\n" + r.stderr[-5000:])
if os.path.exists("data/trends.json"): shutil.copy("data/trends.json", "out/tr/trends.json")
