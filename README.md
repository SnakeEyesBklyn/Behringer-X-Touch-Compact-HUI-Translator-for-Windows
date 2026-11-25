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
2. Create two loopMIDI ports with these exact names:
   - `HUI In` — Pro Tools sends HUI feedback through this port
   - `HUI Out` — this program sends HUI input to Pro Tools through this port
3. Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

4. Start the translator:

```powershell
py hui_server.py
```

Or double-click `start.bat`.

5. In Pro Tools, configure an HUI control surface:
   - Receive MIDI From: `HUI Out`
   - Send MIDI To: `HUI In`

## Verification checklist

- The X-Touch appears as separate MIDI input and output ports.
- The X-Touch is in Mackie Control mode.
- Moving a fader changes the matching Pro Tools control.
- Fader touch, channel buttons, transport, bank, and V-Pot controls respond.
- Pro Tools changes update X-Touch LEDs and fader motors.
- Pro Tools reports no port-in-use or exclusive-access errors.

## Troubleshooting

- The script prints available MIDI ports when hardware or loopMIDI ports are missing.
- Restart loopMIDI and the script after creating or renaming virtual ports.
- Close applications that may hold the X-Touch MIDI ports exclusively.
- Run `py hui_server.py --list-ports` to print MIDI devices without opening them.
- Run `py hui_server.py --diagnostic` to print all received X-Touch MIDI messages.

## Note on hardware testing

Automated GitHub checks can validate syntax and MIDI message construction, but
physical faders, LEDs, loopMIDI routing, and Pro Tools behavior must be verified
on Windows hardware.

## Original project

Based on [Quuikz/x-touch-compact-hui-translator](https://github.com/Quuikz/x-touch-compact-hui-translator).
