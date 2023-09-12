import os
import sys
import urllib.request
from tqdm import tqdm
import requests

from .midi2xml import midi2xml

voices_ids = {
	"english":
		{"female": [9,10], "male": [11]},
	"japanese":
		{"female": [0,1,2,4,5,6,7], "male": [3,8]},
	"mandarin":
		{"female": [12], "male": []}
}


def renderize_voice(lyrics, midi_path, tempo=80, lang="english", gender="female", voiceindex=0, out_folder=".", vibpower=1, f0shift=0, synalpha=0.55):
    
    VOICE_XML_PATH = os.path.join(out_folder, "voice.xml")
    VOICE_WAV_PATH = os.path.join(out_folder, "voice.wav")

    midi2xml(lyrics, midi_path, VOICE_XML_PATH, tempo, lang)
    
    if lang == "korean":
        lang = "japanese"
    
    sinsy_request(VOICE_XML_PATH, VOICE_WAV_PATH, lang, gender, voiceindex, vibpower, f0shift, synalpha)


def voice_code(lang="english", gender="female", index=0):
	if lang == "mandarin" and gender == "male":
		raise Exception("No male voices available for mandarin.")
	options = voices_ids[lang][gender]
	return options[index]

def sinsy_request(xml_file_path, wav_path, lang="english", gender="female", voiceindex=0, vibpower=1, f0shift=0, synalpha=0.55):
    SPKR = voice_code(lang, gender, voiceindex)

    headers = {'User-Agent': 'Mozilla/5.0'}
    payload = {'SPKR_LANG': lang, 'SPKR': SPKR, 'VIBPOWER': vibpower, 'F0SHIFT': f0shift, "SYNALPHA": synalpha}
    files = {'SYNSRC': open(xml_file_path,'rb')}

    print("Voice Synthesis started. This may take some time...")
    r = requests.post(url='http://sinsy.sp.nitech.ac.jp/index.php', headers=headers, data=payload, files=files)

    html_response = r.text.split("temp/")
    url_file_name = find_wav_name_on_website(html_response)
    print(url_file_name)


    if url_file_name is None:
        raise Exception("No wav file found on sinsy.jp. Try again!")
    else:
        download_with_progress(url_file_name, wav_path)
        print("Voice Synthesis completed.")

def find_wav_name_on_website(htmlResponse):
	url_file_name = None
	for line in htmlResponse:
		parts = line.split(".")
		if parts[1][:3] == "wav":
			url_file_name = parts[0]
			break
	return url_file_name

def download_with_progress(url_file_name, wav_path):
	response = requests.get("http://sinsy.sp.nitech.ac.jp/temp/" + url_file_name + ".wav", stream=True)

	total = int(response.headers.get('content-length', 0))
	block_size = 1024  # 1 Kibibyte

	progress_bar = tqdm(total=total, unit='iB', unit_scale=True)
	with open(wav_path, 'wb') as file:
		for data in response.iter_content(block_size):
			progress_bar.update(len(data))
			file.write(data)
	progress_bar.close()
