import subprocess
import sys

print("🚀 STARTING FULL PA PIPELINE")

# =========================
# STEP 1: EXCEL → TEXT
# =========================
print("\n📝 STEP 1: Excel → Text conversion")
res1 = subprocess.run(
    [sys.executable, "excel_to_texts_batch.py"],
    capture_output=True,
    text=True
)

print(res1.stdout)
if res1.returncode != 0:
    print("❌ Excel → Text FAILED")
    print(res1.stderr)
    sys.exit(1)

# =========================
# STEP 2: TEXT → MP3
# =========================
print("\n🔊 STEP 2: Text → MP3 conversion")
res2 = subprocess.run(
    [sys.executable, "texts_to_mp3_batch.py"],
    capture_output=True,
    text=True
)

print(res2.stdout)
if res2.returncode != 0:
    print("❌ Text → MP3 FAILED")
    print(res2.stderr)
    sys.exit(1)

print("\n🔥🔥 FULL PIPELINE COMPLETED SUCCESSFULLY 🔥🔥")
