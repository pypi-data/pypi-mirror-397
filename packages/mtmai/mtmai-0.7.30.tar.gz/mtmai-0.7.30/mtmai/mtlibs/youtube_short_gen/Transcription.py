import torch
from faster_whisper import WhisperModel


def transcribeAudio(audio_path):
    try:
        Device = "cuda" if torch.cuda.is_available() else "cpu"
        model = WhisperModel(
            "base.en", device="cuda" if torch.cuda.is_available() else "cpu"
        )
        segments, info = model.transcribe(
            audio=audio_path,
            beam_size=5,
            language="en",
            max_new_tokens=128,
            condition_on_previous_text=False,
        )
        segments = list(segments)
        extracted_texts = [
            [segment.text, segment.start, segment.end] for segment in segments
        ]
        return extracted_texts
    except Exception:
        return []


if __name__ == "__main__":
    audio_path = "audio.wav"
    transcriptions = transcribeAudio(audio_path)
    print("Done")
    TransText = ""

    for text, start, end in transcriptions:
        TransText += f"{start} - {end}: {text}"
    print(TransText)
