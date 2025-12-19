# AhoTTS Python

[AhoTTS](https://github.com/aholab/AhoTTS) is a Text-to-Speech conversor for Basque and Spanish. 
It includes linguistic processing and built voices for the languages aforementioned. Its acoustic
engine is based on hts_engine and it uses a high quality vocoder called
AhoCoder. Developed by Aholab Signal Processing Laboratory, at the Bilbao
School of Engineering (University of the Basque Country).

## Compile

```bash
git clone https://github.com/TigreGotico/pyAhoTTS
cd pyAhoTTS
mkdir build
cd build
cmake .. 
make
```

## Usage

```python
from pyahotts import AhoTTS

# libhtts_x86_64.so and libhtts_aarch64.so is bundled with the package
# for other archs like x86 (32bit) you need to pass lib_path
tts = AhoTTS(
    lib_path="/home/miro/PycharmProjects/AhoTTS/libhtts_x86.so"
)

audio_bytes = tts.get_tts("Kaixo Mundua!", lang="eu", wav_path="output_eu.wav")

if audio_bytes:
    print(f"Generated {len(audio_bytes)} bytes of audio.")

audio_bytes = tts.get_tts("Hola Mundo", lang="es", wav_path="output_es.wav")

if audio_bytes:
    print(f"Generated {len(audio_bytes)} bytes of audio.")
```

## LICENSE

Read `COPYRIGHT_and_LICENSE_code.txt` and `COPYRIGHT_and_LICENSE_voices.txt`

    Basque (voice models & linguistic data):
     	Copyright: Aholab Signal Processing Laboratory, University of the Basque Country (UPV/EHU)
    	License: The files in this package are licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
    	         http://creativecommons.org/licenses/by-sa/3.0/
    
    Spanish: (voice models & linguistic data):
     	Copyright: Aholab Signal Processing Laboratory, University of the Basque Country (UPV/EHU)
    	License: The files in this package are licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
    	         http://creativecommons.org/licenses/by-sa/3.0/

## Credits

<img src="img.png" width="128"/>

> Python bindings for AhoTTS were funded by the Ministerio para la Transformación Digital y de la Función Pública and Plan de Recuperación, Transformación y Resiliencia - Funded by EU – NextGenerationEU within the framework of the project ILENIA with reference 2022/TL22/00215337

> Based on the [fork from @ekaitz-zarraga](https://github.com/ekaitz-zarraga/AhoTTS)
