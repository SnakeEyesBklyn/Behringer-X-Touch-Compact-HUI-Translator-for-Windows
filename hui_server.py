import mido
import time
import sys

mido.set_backend("mido.backends.rtmidi")

XTOUCH_PORT_NAME = "X-TOUCH COMPACT"
HUI_TO_PROTOOLS_PORT = "HUI Out"
HUI_FROM_PROTOOLS_PORT = "HUI In"
FADER_COUNT = 8
HUI_FADER_CENTER_MSB = 64
HUI_ZONE_SOLO = 0x0A
HUI_ZONE_MUTE = 0x0B
HUI_ZONE_RECORD_ARM = 0x0D
HUI_ZONE_SELECT = 0x0F

MCU_BUTTON_NOTES = {
    "record_arm": tuple(range(0, 8)),
    "solo": tuple(range(8, 16)),
    "mute": tuple(range(16, 24)),
    "select": tuple(range(24, 32)),
}


def find_port(names, device_name):
    matches = [name for name in names if device_name.upper() in name.upper()]
    return matches[0] if matches else None


def main():
    print("--- Behringer X-Touch Compact HUI Server (Windows) ---")

    input_names = mido.get_input_names()
    output_names = mido.get_output_names()

    xtouch_input = find_port(input_names, XTOUCH_PORT_NAME)
    xtouch_output = find_port(output_names, XTOUCH_PORT_NAME)

    if not xtouch_input or not xtouch_output:
        print("[-] X-Touch Compact not found.")
        print("    Connect it by USB and set it to MC (Mackie Control) mode.")
        print("    Available MIDI inputs:", input_names)
        print("    Available MIDI outputs:", output_names)
        return 1

    hui_output = find_port(output_names, HUI_TO_PROTOOLS_PORT)
    hui_input = find_port(input_names, HUI_FROM_PROTOOLS_PORT)

    if not hui_output:
        print("[-] Virtual HUI output not found:", HUI_TO_PROTOOLS_PORT)
        print("    Create it in loopMIDI, then restart this script.")
        return 1

    if not hui_input:
        print("[-] Virtual HUI input not found:", HUI_FROM_PROTOOLS_PORT)
        print("    Create it in loopMIDI, then restart this script.")
        return 1

    ports = []
    try:
        xtouch_in = mido.open_input(xtouch_input)
        ports.append(xtouch_in)
        xtouch_out = mido.open_output(xtouch_output)
        ports.append(xtouch_out)
        hui_in = mido.open_input(hui_input)
        ports.append(hui_in)
        hui_out = mido.open_output(hui_output)
        ports.append(hui_out)
    except Exception as exc:
        print(f"[-] Could not open one or more MIDI ports: {exc}")
        for port in ports:
            try:
                port.close()
            except Exception:
                pass
        return 1

    print(f"[+] X-Touch input:  {xtouch_input}")
    print(f"[+] X-Touch output: {xtouch_output}")
    print(f"[+] HUI input:      {hui_input}")
    print(f"[+] HUI output:     {hui_output}")

    current_hui_zone = 0
    fader_msb = [HUI_FADER_CENTER_MSB] * FADER_COUNT

    def send_hui_button(zone, channel, is_pressed):
        hui_out.send(mido.Message("control_change", channel=0, control=0x0C, value=zone))
        hui_out.send(mido.Message(
            "control_change", channel=0, control=0x2C,
            value=channel | (0x40 if is_pressed else 0x00)
        ))

    def send_mcu_button(note, is_pressed):
        xtouch_out.send(mido.Message(
            "note_on", channel=0, note=note,
            velocity=127 if is_pressed else 0
        ))

    def handle_xtouch_to_daw(msg):
        if msg.type == "pitchwheel":
            channel = msg.channel
            if 0 <= channel <= 7:
                value = msg.pitch + 8192
                msb = (value >> 7) & 0x7F
                lsb = value & 0x7F
                hui_out.send(mido.Message("control_change", channel=0, control=channel, value=msb))
                hui_out.send(mido.Message("control_change", channel=0, control=channel + 32, value=lsb))

        elif msg.type in ("note_on", "note_off"):
            is_pressed = int(msg.type == "note_on" and msg.velocity > 0)

            if 104 <= msg.note <= 111:
                fader_index = msg.note - 104
                hui_out.send(mido.Message("control_change", channel=0, control=0x0F, value=fader_index))
                hui_out.send(mido.Message("control_change", channel=0, control=0x2F, value=0x40 if is_pressed else 0x00))
            else:
                channel_button = next((
                    (name, channel)
                    for name, notes in MCU_BUTTON_NOTES.items()
                    for channel, note in enumerate(notes)
                    if note == msg.note
                ), None)

                if channel_button:
                    button_name, channel = channel_button
                    hui_zone = {
                        "record_arm": HUI_ZONE_RECORD_ARM,
                        "solo": HUI_ZONE_SOLO,
                        "mute": HUI_ZONE_MUTE,
                        "select": HUI_ZONE_SELECT,
                    }[button_name]
                    send_hui_button(hui_zone, channel, is_pressed)

                elif msg.note == 46 and is_pressed:
                    hui_out.send(mido.Message("control_change", channel=0, control=0x0C, value=0x0A))
                    hui_out.send(mido.Message("control_change", channel=0, control=0x2C, value=0x40))

                elif msg.note == 47 and is_pressed:
                    hui_out.send(mido.Message("control_change", channel=0, control=0x0C, value=0x0A))
                    hui_out.send(mido.Message("control_change", channel=0, control=0x2C, value=0x41))

                elif msg.note in (91, 92, 93, 94, 95):
                    port = {91: 0, 92: 1, 93: 2, 94: 3, 95: 4}[msg.note]
                    value = 0x40 + port if is_pressed else port
                    hui_out.send(mido.Message("control_change", channel=0, control=0x0C, value=0x0E))
                    hui_out.send(mido.Message("control_change", channel=0, control=0x2C, value=value))

        elif msg.type == "control_change":
            if 16 <= msg.control <= 23:
                hui_cc = msg.control - 16 + 0x40
                hui_out.send(mido.Message("control_change", channel=0, control=hui_cc, value=msg.value))
            else:
                hui_out.send(msg)

    def handle_daw_to_xtouch(msg):
        nonlocal current_hui_zone, fader_msb

        if msg.type == "note_on" and msg.note == 0 and msg.velocity == 0:
            hui_out.send(mido.Message("note_on", channel=0, note=0, velocity=127))
            return

        if msg.type != "control_change":
            return

        if 0 <= msg.control <= 7:
            fader_msb[msg.control] = msg.value

        elif 32 <= msg.control <= 39:
            channel = msg.control - 32
            value = (fader_msb[channel] << 7) | msg.value
            xtouch_out.send(mido.Message("pitchwheel", channel=channel, pitch=value - 8192))

        elif msg.control == 0x0C:
            current_hui_zone = msg.value

        elif msg.control == 0x2C:
            if current_hui_zone == 0x0E:
                port = msg.value & 0x0F
                is_on = bool(msg.value & 0x40)
                mcu_note_map = {0: 91, 1: 92, 2: 93, 3: 94, 4: 95}
                if port in mcu_note_map:
                    send_mcu_button(mcu_note_map[port], is_on)

            elif current_hui_zone in {
                HUI_ZONE_RECORD_ARM,
                HUI_ZONE_SOLO,
                HUI_ZONE_MUTE,
                HUI_ZONE_SELECT,
            }:
                channel = msg.value & 0x0F
                if channel < FADER_COUNT:
                    is_on = bool(msg.value & 0x40)
                    mcu_row = {
                        HUI_ZONE_RECORD_ARM: "record_arm",
                        HUI_ZONE_SOLO: "solo",
                        HUI_ZONE_MUTE: "mute",
                        HUI_ZONE_SELECT: "select",
                    }[current_hui_zone]
                    send_mcu_button(MCU_BUTTON_NOTES[mcu_row][channel], is_on)

    xtouch_in.callback = handle_xtouch_to_daw
    hui_in.callback = handle_daw_to_xtouch

    print("[+] Server Active. Press Ctrl+C to terminate.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping HUI Server...")
    finally:
        for port in ports:
            try:
                port.close()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
