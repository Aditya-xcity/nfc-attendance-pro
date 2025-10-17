# models/voice.py - Voice feedback system
import pyttsx3

class VoiceEngine:
    _engine = None

    @classmethod
    def init(cls):
        if cls._engine is None:
            try:
                cls._engine = pyttsx3.init()
                cls._engine.setProperty('rate', 150)
                cls._engine.setProperty('volume', 0.8)
            except Exception:
                cls._engine = None
        return cls._engine

def voice_feedback(text):
    try:
        engine = VoiceEngine.init()
        if engine:
            engine.say(text)
            engine.runAndWait()
    except Exception:
        pass