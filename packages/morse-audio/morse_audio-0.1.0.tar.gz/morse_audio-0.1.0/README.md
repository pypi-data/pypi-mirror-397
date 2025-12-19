# Morse Audio

Python library for converting text to Morse code, generating audio Morse signals, 
and decoding Morse from microphone recordings.

## Installation

```bash
pip install morse_audio
```

## Usage

```bash
from morse_audio import Morse

m = Morse()
msg = m.text_to_morse("Hello World")
m.morse_to_audio(msg)  # plays Morse audio
```
