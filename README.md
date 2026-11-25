# Windows 11 X-Touch Compact HUI Translator

Python MIDI translator for using a Behringer X-Touch Compact as a basic HUI
surface in Pro Tools on Windows 11.

## Requirements

- Windows 11
- Behringer X-Touch Compact connected by USB
- X-Touch Compact set to MC (Mackie Control) mode
- Python 3.11 or newer
- loopMIDI
- `mido` and `python-rtmidi`

## Setup

1. Install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html).
2. Create two ports named exactly:
   - `HUI In`
   - `HUI Out`
3. Install Python dependencies:

```powershell
py -m pip install -r requirements.txt
```

4. Start the translator:

```powershell
py hui_server.py
```

5. In Pro Tools, configure an HUI control surface to use the loopMIDI ports:
   - Receive MIDI from `HUI Out`
   - Send MIDI to `HUI In`

Keep the script running while using Pro Tools.

## Port orientation

If Pro Tools asks for separate MIDI input and output ports:

- **Pro Tools receives from:** `HUI Out`
- **Pro Tools sends to:** `HUI In`

The script translates MCU messages from the X-Touch Compact into HUI messages
and forwards HUI feedback back to the X-Touch LEDs and motorized faders.

## Troubleshooting

- Confirm the X-Touch Compact appears in `mido.get_input_names()` and
  `mido.get_output_names()`.
- Restart loopMIDI and the script after changing virtual MIDI ports.
- Verify the X-Touch Compact is in Mackie Control mode.
- In Windows Settings, ensure no application has exclusive control of the
  hardware MIDI port.

## Original project

Based on [Quuikz/x-touch-compact-hui-translator](https://github.com/Quuikz/x-touch-compact-hui-translator).
