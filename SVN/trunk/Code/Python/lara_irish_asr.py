import lara_utils
import base64
import requests

_irish_rec_url = "https://phoneticsrv3.lcs.tcd.ie/asr_api/recognise"

def mp3_to_rec_responses_irish(AbsSpeechFile):
    with open(AbsSpeechFile, "rb") as fh:
            audio = fh.read()
            encodedAudio = base64.b64encode(audio).decode('utf-8')
     
    rec_req = {
            "recogniseBlob": encodedAudio,
            "developer":True
        }

    res = requests.post(_irish_rec_url, json=rec_req)
    data = res.json()
    transcription1 = data['transcriptions'][0]['utterance']       
    return { 'transcript': transcription1 }
