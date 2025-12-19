"""
morse_audio.py

A Python library for converting text to Morse code, generating Morse audio signals,
and decoding Morse from microphone recordings.

Features:
- TextToMorse: Converts text to Morse code
- MorseToText: Converts Morse code back to text
- MorseToAudio: Generates and optionally plays Morse audio

Author: Mattia Alessi
License: MIT
"""

import numpy as np
import sounddevice as sd

class Morse:
    """
    Class to handle Morse code conversions and audio generation/decoding.

    Attributes:
        fs (int): Sampling rate in Hz for audio
        freq (int): Frequency of the Morse beep in Hz
        unit_duration (float): Duration of a single Morse unit (dot) in seconds
    """

    def __init__(self, fs: int = 44100, freq: int = 750, unit_duration: float = 0.1):
        """
        Initializes the Morse code system.

        Args:
            fs (int, optional): Audio sampling rate (Hz). Defaults to 44100.
            freq (int, optional): Beep frequency (Hz). Defaults to 750.
            unit_duration (float, optional): Duration of a single Morse unit in seconds. Defaults to 0.1.
        """
        
        # Standard International Morse Code dictionary
        MORSE_DICT = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..',
            '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
            '6': '-....', '7': '--...', '8': '---..', '9': '----.',
            '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',
            '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
            ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
            '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'
        }
        self.dict = MORSE_DICT
        self.rev_dict = {v: k for k, v in self.dict.items()}
        self._fs = fs
        self._freq = freq
        self._unit_duration = unit_duration

    @property
    def fs(self) -> int:
        """Audio sampling rate in Hz."""
        return self._fs

    @fs.setter
    def fs(self, value: int):
        if value <= 0:
            raise ValueError("Sampling rate must be positive.")
        self._fs = value

    @property
    def freq(self) -> int:
        """Frequency of Morse beep in Hz."""
        return self._freq

    @freq.setter
    def freq(self, value: int):
        if value <= 0:
            raise ValueError("Frequency must be positive.")
        self._freq = value

    @property
    def unit_duration(self) -> float:
        """Duration of a single Morse unit (dot) in seconds."""
        return self._unit_duration

    @unit_duration.setter
    def unit_duration(self, value: float):
        if value <= 0:
            raise ValueError("Unit duration must be positive.")
        self._unit_duration = value


    # Text ↔ Morse Conversions


    def text_to_morse(self, message: str) -> str:
        """
        Converts a text message into Morse code.

        Args:
            message (str): Text message to convert

        Returns:
            str: Morse code representation (dots, dashes, and '/' for spaces)

        Raises:
            ValueError: If a character is not supported in Morse code
        """
        morse_msg = []
        for char in message.upper():
            if char in self.dict:
                morse_msg.append(self.dict[char])
            else:
                raise ValueError(f"Character not supported: {char}")
        return " ".join(morse_msg)

    def morse_to_text(self, morse_msg: str) -> str:
        """
        Converts a Morse code message into text.

        Args:
            morse_msg (str): Morse code string (dots, dashes, spaces, '/')

        Returns:
            str: Decoded text message
        """
        text_msg = []
        words = morse_msg.strip().split(" / ")
        for word in words:
            letters = word.split()
            for letter in letters:
                if letter in self.rev_dict:
                    text_msg.append(self.rev_dict[letter])
                else:
                    raise ValueError(f"Invalid Morse sequence: {letter}")
            text_msg.append(" ")
        return "".join(text_msg).strip()

 
    # Audio Generation
 

    def morse_to_audio(self, morse_msg: str, play_sound: bool = True) -> np.ndarray:
        """
        Generates audio for a Morse code message.

        Args:
            morse_msg (str): Morse code string
            play_sound (bool, optional): If True, plays the audio immediately. Defaults to True.

        Returns:
            np.ndarray: Array of audio samples representing the Morse code
        """
        dot_duration = self._unit_duration
        dash_duration = 3 * self._unit_duration
        symbol_pause = self._unit_duration
        letter_pause = 3 * self._unit_duration
        word_pause = 7 * self._unit_duration

        sound_blocks = []

        words = morse_msg.strip().split(" / ")
        for w_idx, word in enumerate(words):
            letters = word.split()
            for l_idx, letter in enumerate(letters):
                for s_idx, symbol in enumerate(letter):
                    if symbol == ".":
                        t = np.linspace(0, dot_duration, int(self._fs * dot_duration), endpoint=False)
                        beep = np.sin(2 * np.pi * self._freq * t)
                        sound_blocks.append(beep)
                    elif symbol == "-":
                        t = np.linspace(0, dash_duration, int(self._fs * dash_duration), endpoint=False)
                        beep = np.sin(2 * np.pi * self._freq * t)
                        sound_blocks.append(beep)
                    if s_idx < len(letter) - 1:
                        silence = np.zeros(int(self._fs * symbol_pause))
                        sound_blocks.append(silence)
                if l_idx < len(letters) - 1:
                    silence = np.zeros(int(self._fs * (letter_pause - symbol_pause)))
                    sound_blocks.append(silence)
            if w_idx < len(words) - 1:
                silence = np.zeros(int(self._fs * word_pause))
                sound_blocks.append(silence)

        final_sound = np.concatenate(sound_blocks)

        if play_sound:
            sd.play(final_sound, self._fs)
            sd.wait()

        return final_sound