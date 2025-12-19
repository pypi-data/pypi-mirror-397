import ctypes
import platform
import wave
from os.path import dirname, isfile
from typing import Optional

import numpy as np


class AhoTTS:
    """
    A class to interact with AhoTTS, a text-to-speech (TTS) system that uses a shared library for synthesis.

    Attributes:
        data_path (bytes): Path to the directory containing TTS data.
        tts (ctypes.c_void_p): The TTS instance created by the shared library.
        current_lang (Optional[str]): The current language used by the TTS instance.
    """

    def __init__(self, lib_path: Optional[str] = None,
                 data_path: str = f"{dirname(__file__)}/data_tts"):
        """
        Initializes the AhoTTS instance, loading the shared library and setting the data path.

        Args:
            lib_path (Optional[str]): Path to the shared library (.so, .dll, .dylib). If None, the library is
                                       determined based on the platform.
            data_path (str): Path to the directory containing TTS data (default is `./data_tts`).
        """
        if lib_path is None:
            lib_path = f"{dirname(__file__)}/libhtts_{platform.machine()}.so"
            if not isfile(lib_path):
                raise FileNotFoundError(f"Please compile and pass the shared library via 'lib_path' argument")

        self.data_path = data_path.encode("utf-8")
        self._load_library(lib_path)
        self.tts = None
        self.current_lang = None

    def _load_library(self, lib_path: str):
        """
        Loads the shared library and sets up the function prototypes for TTS operations.

        Args:
            lib_path (str): Path to the shared library.
        """
        self.lib = ctypes.cdll.LoadLibrary(lib_path)

        # Setup argument types and return types for library functions
        self.lib.create_tts.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.create_tts.restype = ctypes.c_void_p

        self.lib.synthesize_text.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_short)),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.synthesize_text.restype = ctypes.c_int

        self.lib.free_samples.argtypes = [ctypes.POINTER(ctypes.c_short)]
        self.lib.destroy_tts.argtypes = [ctypes.c_void_p]

    def _recreate_tts(self, lang: str):
        """
        Recreates the TTS instance for a given language.

        Args:
            lang (str): The language code (e.g., 'eu' for Basque).

        Raises:
            RuntimeError: If the TTS instance could not be created.
        """
        if self.tts is not None:
            self.lib.destroy_tts(self.tts)
        self.tts = self.lib.create_tts(self.data_path, lang.encode("utf-8"))
        if not self.tts:
            raise RuntimeError(f"Failed to create TTS instance for language: {lang}")
        self.current_lang = lang

    def get_tts(self, text: str, lang: str = "eu", wav_path: Optional[str] = None) -> bytes:
        """
        Generates speech from text and returns it as a byte array, optionally saving it to a WAV file.

        Args:
            text (str): The text to be converted to speech.
            lang (str): The language code for TTS synthesis (default is 'eu' for Basque).
            wav_path (Optional[str]): If provided, saves the generated audio as a WAV file at this path.

        Returns:
            bytes: The generated audio as a byte array, or an empty byte array if synthesis fails.
        """
        text_bytes = text.encode("utf-8")
        lang_bytes = lang.encode("utf-8")

        # Check if the language is different from the current language
        if self.tts is None or self.current_lang != lang:
            self._recreate_tts(lang)

        samples_ptr = ctypes.POINTER(ctypes.c_short)()
        length = ctypes.c_int()

        success = self.lib.synthesize_text(
            self.tts, text_bytes, self.data_path, lang_bytes,
            ctypes.byref(samples_ptr), ctypes.byref(length)
        )

        if not success or length.value <= 0:
            return b""

        # Convert to NumPy array
        samples_np = np.ctypeslib.as_array(samples_ptr, shape=(length.value,))
        samples_bytes = samples_np.astype(np.int16).tobytes()

        if wav_path:
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 2 bytes per sample (16-bit)
                wf.setframerate(16000)  # Assuming 16kHz
                wf.writeframes(samples_bytes)

        self.lib.free_samples(samples_ptr)
        return samples_bytes

    def __del__(self):
        """
        Cleans up by destroying the TTS instance when the object is deleted.
        """
        if hasattr(self, 'tts') and self.tts:
            self.lib.destroy_tts(self.tts)
            self.tts = None


if __name__ == "__main__":
    tts = AhoTTS()

    audio_bytes = tts.get_tts("Kaixo Mundua!", lang="eu", wav_path="../output_eu.wav")

    if audio_bytes:
        print(f"Generated {len(audio_bytes)} bytes of audio.")

    audio_bytes = tts.get_tts("Hola Mundo", lang="es", wav_path="../output_es.wav")

    if audio_bytes:
        print(f"Generated {len(audio_bytes)} bytes of audio.")
