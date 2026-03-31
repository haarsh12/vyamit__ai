import os
import wave
import json
from vosk import Model, KaldiRecognizer

# STEP 1: Load model
MODEL_PATH = "models/vosk-model-small-en-in-0.4"
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = Model(MODEL_PATH)
    else:
        print(f"Warning: Vosk model not found at '{MODEL_PATH}'. Please ensure it is downloaded.")
except Exception as e:
    print(f"Failed to load Vosk model: {e}")

# STEP 2 & 5: Create function and handle errors
def transcribe_audio(file_path: str) -> str:
    """
    Transcribes audio from a WAV file into text using Vosk offline models.
    Requires mono channel and PCM formatted WAV.
    """
    if not model:
        print("Error: Vosk model is not loaded. Cannot transcribe.")
        return "unable to recognize speech"
        
    if not os.path.exists(file_path):
        print(f"Error: Audio file '{file_path}' not found.")
        return "unable to recognize speech"
        
    try:
        # Handle file opening elegantly using a context manager
        with wave.open(file_path, "rb") as wf:
            
            # Ensure mono channel and PCM format
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                print("Error: Audio file must be WAV format mono PCM.")
                return "unable to recognize speech"
                
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            
            results = []
            
            # STEP 3: Handle partial + final results
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                    
                if rec.AcceptWaveform(data):
                    part_result = json.loads(rec.Result())
                    # Skip empty components
                    if part_result.get("text"):
                        results.append(part_result["text"])
                else:
                    pass
                    
            final_part = json.loads(rec.FinalResult())
            if final_part.get("text"):
                results.append(final_part["text"])
                
            # STEP 4: Clean output
            # Join everything, make lowercase, and split/join implicitly removes all double whitespaces and trims strings
            final_text = " ".join(results).lower()
            cleaned_text = " ".join(final_text.split())
            
            # Return cleaned_text or the fallback if completely empty
            return cleaned_text if cleaned_text else "unable to recognize speech"
            
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        # Improve error fallback
        return "unable to recognize speech"

# STEP 6: Testing
if __name__ == "__main__":
    sample_wav = "sample.wav"
    
    print("====== Offline Speech-to-Text Test ======\n")
    print(f"Input File: {sample_wav}")
    
    if os.path.exists(sample_wav):
        text_output = transcribe_audio(sample_wav)
        print(f"Output Text: \"{text_output}\"")
    else:
        print(f"Note: Please place a valid mono PCM '{sample_wav}' inside this directory to execute a successful test.")
        
    print("-" * 50)
