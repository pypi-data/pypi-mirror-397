# ListenerCLI

A fast and easy CLI-based speech-to-text tool that records audio from your microphone, transcribes it using Whisper AI, and automatically copies the result to your clipboard.

```
╔═══════════════════════════════════════╗
║                                       ║
║     🎤  LISTENER CLI  🎤              ║
║                                       ║
║     Speech-to-Text Transcription     ║
║                                       ║
╚═══════════════════════════════════════╝
```

## Features

- 🎤 **Simple Recording**: Press Enter to start/stop recording
- 🤖 **AI Transcription**: Powered by faster-whisper (OpenAI's Whisper)
- 📋 **Auto Clipboard**: Transcription automatically copied to clipboard
- 🚀 **Multiple Models**: Choose from tiny to large models (tiny, base, small, medium, large, turbo)
- 🌍 **Multi-language**: Support for 99+ languages with auto-detection
- ⚡ **Local Processing**: Everything runs locally on your machine
- 💾 **Smart Caching**: Models downloaded once and cached for future use
- 🔄 **Re-transcribe**: Re-process your last recording without re-recording

## Installation

Install using uv:

```bash
uv pip install listenercli
```

Or using pip:

```bash
pip install listenercli
```

## Usage

### Basic Usage

Simply run the command and start speaking:

```bash
lci
```

**Steps:**
1. Run `lci`
2. Press Enter to start recording
3. Speak into your microphone
4. Press Enter to stop recording
5. Wait for transcription (first run downloads the model)
6. Your transcription is automatically copied to clipboard and printed to stdout

### Available Options

```bash
# Use a specific Whisper model
lci --model turbo              # Fast and accurate (recommended)
lci --model tiny               # Fastest, less accurate (~75MB)
lci --model base               # Default, good balance (~145MB)
lci --model medium             # More accurate (~1.5GB)
lci --model large-v3           # Most accurate (~3GB)

# Force a specific language
lci --language en              # English
lci --language es              # Spanish
lci --language fr              # French

# Re-transcribe last recording (without re-recording)
lci --last

# List all available Whisper models
lci --list-models

# Adjust audio settings
lci --sample-rate 16000 --channels 1

# See all options
lci --help
```

### Full Command Name

You can also use the full command name:

```bash
listenercli
```

Both `lci` and `listenercli` work identically.

## Model Guide

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| `tiny` | ~75MB | ⚡⚡⚡ | ⭐⭐ | Quick notes |
| `base` | ~145MB | ⚡⚡ | ⭐⭐⭐ | Default use (balanced) |
| `small` | ~466MB | ⚡ | ⭐⭐⭐⭐ | Good accuracy |
| `medium` | ~1.5GB | 🐢 | ⭐⭐⭐⭐⭐ | High accuracy |
| `large-v3` | ~3GB | 🐢🐢 | ⭐⭐⭐⭐⭐⭐ | Best accuracy |
| `turbo` | ~809MB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Recommended (fast + accurate) |

**Note**: Models are downloaded once and cached. First run will be slower.

## Environment Variables

- `LISTENER_CLI_LANGUAGE`: Set default language for transcription
  ```bash
  export LISTENER_CLI_LANGUAGE=en
  lci
  ```

## Audio File Location

Recordings are saved to:
- **macOS**: `~/Library/Caches/listenerCLI/last.wav`
- **Linux**: `~/.cache/listenerCLI/last.wav`
- **Windows**: `%LOCALAPPDATA%\listenerCLI\Cache\last.wav`

You can re-transcribe the last recording with `lci --last` without recording again.

## Requirements

- Python >= 3.13
- Microphone access
- Internet connection (first run only, to download models)

## Troubleshooting

### No audio device found
Make sure your microphone is connected and accessible. Check system permissions for microphone access.

### Model download fails
Check your internet connection. Models are downloaded from Hugging Face on first use.

### Transcription is inaccurate
Try a larger model: `lci --model turbo` or `lci --model medium`

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Credits

Built with:
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper transcription
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
