import os
import subprocess
import sys
import time

model_name = sys.argv[1]
text_file = sys.argv[2]
midi_file = sys.argv[3]
lang = sys.argv[4]
gender = sys.argv[5]
bpm = sys.argv[6]

subprocess.run(["python", "-m", "midi2voice", "-l", text_file, "-m", midi_file, "--lang", lang, "-g", gender, "-t", bpm])

os.chdir('./RVC')
oneclick = subprocess.run(["python", "oneclickprocess.py", "--name", model_name])

print("All processes have finished.")
