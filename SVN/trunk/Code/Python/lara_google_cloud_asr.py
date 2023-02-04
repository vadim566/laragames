
import lara_utils
from google.cloud import speech_v1p1beta1 as speech
import io
    
def mp3_to_rec_responses_google(AbsSpeechFile, LanguageCode):
    client = speech.SpeechClient()
    with io.open(AbsSpeechFile, "rb") as audio_file:
        content = (audio_file.read())

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code=LanguageCode,
        enable_word_time_offsets=True
        )
    
    Responses = client.recognize(config=config, audio=audio)
    return extract_data_from_responses(Responses)

def large_mp3_to_rec_responses_google(SpeechFileURI, LanguageCode, Timeout):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=SpeechFileURI)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code=LanguageCode,
        enable_word_time_offsets=True
        #enable_automatic_punctuation=True
        )
    
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    Responses = operation.result(timeout=Timeout)
    return extract_data_from_responses(Responses)

def extract_data_from_responses(Responses):
    try:
        Alternative = Responses.results[0].alternatives[0]
        return { 'transcript': str(Alternative.transcript),
                 'confidence': Alternative.confidence,
                 'word_info': [ { 'word': WordInfo.word,
                                  'start_end': [ WordInfo.start_time.total_seconds(), WordInfo.end_time.total_seconds() ] }
                                for WordInfo in Alternative.words ]
                 }
    except Exception as e:
        lara_utils.print_and_flush(f'*** Warning: reply was not a recognition response:')
        lara_utils.print_and_flush(str(Responses))
        return { 'transcript': False }






        
