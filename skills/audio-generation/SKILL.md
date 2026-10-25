---
name: audio-generation
description: Voice generation and text-to-speech using Microsoft Edge's neural TTS service via edge-tts (rany2/edge-tts). Use when the user wants to generate spoken audio/voice from text, needs TTS output, accessibility reads, narration, or asks for voice generation.
---

# Edge-TTS Voice Generation

Generate high-quality text-to-speech audio using Microsoft Edge's neural TTS service via the `uvx edge-tts` command (powered by https://github.com/rany2/edge-tts).
Supports multiple languages, voices, adjustable speed/pitch/volume, and subtitle generation.

## Usage
```shell
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3

# With subtitles
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3 --write-subtitles -
```

## Changing rate (speed), volume and pitch
```shell
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3 --rate=+50%
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3 --volume=+50% --pitch=-50Hz
```

## Changing the voice
```shell
uvx edge-tts --text "{msg}" --write-media {tempdir}/{filename}.mp3 --voice en-US-JennyNeural
```

## Available voices (sample)
```
en-US-JennyNeural                  Female    General                Friendly, Considerate, Comfort
en-US-GuyNeural                   Male      News, Novel            Passion
en-US-AriaNeural                  Female    News, Novel            Positive, Confident
zh-CN-XiaoxiaoNeural              Female    News, Novel            Warm
```

Retrieve all available voices:
```shell
uvx edge-tts --list-voices
```

## Notes
- Requires network access (Microsoft Edge online TTS service).
- `uvx` will fetch edge-tts automatically; no manual install needed.
- Source library: https://github.com/rany2/edge-tts
