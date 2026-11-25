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

## Command-line usage

The translator supports two diagnostic modes:

### List MIDI ports

Print the Windows MIDI input and output names without starting or opening the server:

```powershell
py hui_server.py --list-ports
```

Use this command to confirm the X-Touch Compact and loopMIDI port names before setup.

### Diagnostic MIDI logging

Print MIDI messages received from both the X-Touch Compact and the HUI/loopMIDI connection while the server runs:

```powershell
py hui_server.py --diagnostic
```

Press <kbd>Ctrl</kbd>+<kbd>C</kbd> to stop the server. Diagnostic output is useful for checking fader movement and button behavior.

## Verification checklist

- The X-Touch appears as separate MIDI input and output ports.
- The X-Touch is in Mackie Control mode.
- Moving a fader changes the matching Pro Tools control.
- Fader touch, channel buttons, transport, bank, and V-Pot controls respond.
- Pro Tools changes update X-Touch LEDs and fader motors.
- Pro Tools reports no port-in-use or exclusive-access errors.

## Troubleshooting

- Restart loopMIDI and the script after creating or renaming virtual ports.
- Close applications that may hold the X-Touch MIDI ports exclusively.
- Run `py hui_server.py --list-ports` to confirm that all required devices are visible.
- Run `py hui_server.py --diagnostic` to inspect MIDI traffic in both directions.
- If hardware or loopMIDI ports are missing, the script prints the detected MIDI port names.

## Note on hardware testing

Automated GitHub checks can validate syntax and MIDI message construction, but
physical faders, LEDs, loopMIDI routing, and Pro Tools behavior must be verified
on Windows hardware.

## Original project

Based on [Quuikz/x-touch-compact-hui-translator](https://github.com/Quuikz/x-touch-compact-hui-translator).
