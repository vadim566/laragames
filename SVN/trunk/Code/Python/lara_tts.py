
import lara_parse_utils
import lara_config
import lara_utils
import requests
from urllib.parse import urlencode

_readspeaker_license_key = ''
_readspeaker_license_key_file = '$LARA/Code/Python/readspeaker_license_key.txt'

def call_tts_engine(TTSEngine, TTSLanguageId, TTSVoice, TTSURL, AnnotatedText, LongFile, Count, Total):
    try:
        call_tts_engine1(TTSEngine, TTSLanguageId, TTSVoice, TTSURL, AnnotatedText, LongFile, Count, Total)
    except Exception as e:
        lara_utils.print_and_flush(f'*** Error: something went wrong when doing TTS for "{AnnotatedText}"')
        lara_utils.print_and_flush(str(e))
        return False

def call_tts_engine1(TTSEngine, TTSLanguageId, TTSVoice, TTSURL, AnnotatedText, LongFile, Count, Total):
    if TTSEngine == 'readspeaker':
        return create_mp3_using_readspeaker(TTSLanguageId, TTSVoice, TTSURL, AnnotatedText, LongFile, Count, Total)
    elif TTSEngine == 'abair':
        return create_mp3_using_abair(TTSLanguageId, TTSVoice, TTSURL, AnnotatedText, LongFile, Count, Total)
    elif TTSEngine == 'google_tts':
        return create_mp3_using_google_tts(TTSLanguageId, TTSVoice, TTSURL, AnnotatedText, LongFile, Count, Total)

## Adapt PHP example
## // Compose API call url
##	 $url = $api_url . '?key='.$apikey.'&lang='.$language.'&voice='.$voice.'&text='.$text_to_read;

def create_mp3_using_readspeaker(RSLangId, RSVoiceId, URL, Text, File, Count, Total):
    RSKey = get_readspeaker_key()
    if RSKey == False:
        return False
    Data = {"key": RSKey,
            "lang": RSLangId,
            "voice": RSVoiceId,
            "text": Text,
            "streaming": 0}
    lara_utils.print_and_flush(f'--- Sending "{Text}" for TTS ({Count}/{Total})')
    r = requests.post(URL, Data, stream=True)
    if r.status_code != 200:
        lara_utils.print_and_flush(f'*** Warning: TTS failed"')
        return False
    else:
        AbsFile = lara_utils.absolute_file_name(File)
        with open(AbsFile, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        lara_utils.print_and_flush(f'--- TTS output saved to {File}')
        return True

## import gtts							     
## tts = gtts.gTTS('hello', lang='en')
## tts.save(file)

def create_mp3_using_google_tts(GoogleLangId, GoogleVoiceId, URL, Text, File, Count, Total):
    import gtts
    lara_utils.print_and_flush(f'--- Sending "{Text}" for TTS ({Count}/{Total})')
    tts = gtts.gTTS(Text, lang=GoogleLangId)
    tts.save(File)
    return True

## https://tts.readspeaker.com/a/speak?key=[API_KEY]&voice=Female01&lang=sv_se&command=events&text=This%20is%20an%20example.");

def get_events_using_readspeaker(RSLangId, RSVoiceId, URL, Text, Count, Total):
    RSKey = get_readspeaker_key()
    if RSKey == False:
        return False
    Data = {"key": RSKey,
            "lang": RSLangId,
            "voice": RSVoiceId,
            "text": Text,
            "command": "events"}
    lara_utils.print_and_flush(f'--- Sending "{Text}" for "events" info ({Count}/{Total})')
    r = requests.post(URL, Data, stream=True)
    if r.status_code != 200:
        lara_utils.print_and_flush(f'*** Warning: TTS failed"')
        return False
    else:
        try:
            Result = r.json()
        except:
            lara_utils.print_and_flush(f'*** Warning: unable to get JSON')
            Result = False
        return Result

## Get credits 
## https://tts.readspeaker.com/a/speak?key=[API_KEY]&command=credits");

def get_readspeaker_credits():
    RSKey = get_readspeaker_key()
    if RSKey == False:
        return False
    URL = lara_config._tts_info['readspeaker']['url']
    Data = {"key": RSKey,
            "command": "credits"}
    lara_utils.print_and_flush(f'--- Asking for ReadSpeaker credits')
    r = requests.post(URL, Data)
    Code = r.status_code
    if Code != 200:
        lara_utils.print_and_flush(f'*** Warning: TTS failed: status_code = {Code}"')
        return False
    else:
        try:
            JSON = r.json()
        except:
            print_and_flush(f'*** Warning: bad JSON at {url}')
            JSON = False
        return JSON

def get_readspeaker_key():
    global _readspeaker_license_key
    if _readspeaker_license_key == '':
        try:
            _readspeaker_license_key = lara_utils.read_lara_text_file(_readspeaker_license_key_file).strip()
        except Exception as e:
            lara_utils.print_and_flush(f'*** Error: unable to get Readspeaker license key')
            lara_utils.print_and_flush(str(e))
            return False
    return _readspeaker_license_key


#HB added for abair.ie
import base64
def create_mp3_using_abair(AbairLangId, AbairVoiceId, URL, Text, File, Count, Total):
    #_abair_url = "https://www.abair.tcd.ie/api2/synthesise"
    
    #( AbairLangId, AbairVoiceId ) = language_id_to_abair_language_and_voice(LanguageId)
    #URL = _abair_url
    Data = {
        "synthinput": {
            "text": Text
        },
        "voiceparams": {
            "languageCode": AbairLangId,
            "name": AbairVoiceId
        },
        "audioconfig": {
            "audioEncoding": "MP3"
        }
    }
    lara_utils.print_and_flush(f'--- Sending "{Text}" for TTS ({Count}/{Total})')
    r = requests.post(URL, json=Data)
    if r.status_code != 200:
        lara_utils.print_and_flush(f'*** Warning: TTS failed"')
        return False
    else:
        encoded_audio = r.json()["audioContent"]
        decoded_audio = base64.b64decode(encoded_audio)
        
        AbsFile = lara_utils.absolute_file_name(File)
        with open(AbsFile, 'wb') as f:
            f.write(decoded_audio)
        lara_utils.print_and_flush(f'--- TTS output saved to {File}')
        return True


##def language_id_to_abair_language_and_voice(LanguageId):
##    #TODO way to select dialect and voice (and in future Irish English)
##    return ("ga-IE", "ga_UL_anb_nnmnkwii")

