# Display as pasted strings: [1][2], [0][2] for NPC_s.
def NPC_(records):
    # For every NPC_ record, extract the second and first subrecord's (FNAM & NAME) string data.
    npc_labels = []
    for record in records:
        npc_fnam_bytes, npc_name_bytes = record[1], record[0]

        def formatNPC_String(x):
            return str(x[2][:-1], encoding="windows-1252")

        npc_labels.append(
            "{!s} ({!s})".format(
                formatNPC_String(npc_fnam_bytes),
                formatNPC_String(npc_name_bytes),
            )
        )
    # An index into the records was desired, so that's what is returned alongside the name.
    return [{"name": v, "index": i} for i, v in enumerate(npc_labels)]


def CELL(records):  # [[type, size, databuffer]*]
    import struct

    # Find desired subrecord type, then define an unpacking methodology and presentation format.
    def find_subrecords(stype, subrecords):  # subrecord type
        return filter(lambda s: stype.encode().startswith(s[0]), subrecords)

    # TODO: implement MVRF-subrecord handling. These indicate references that have moved (NPCs!): https://en.uesp.net/wiki/Morrowind_Mod:Mod_File_Format/CELL.

    # "Cell definition metadata" Cell DATA subrecord. This subrecord holds the metadata for a CELL definition.
    table_dictionary = [
        {
            "Flags": flags,
            "Grix X": grid_x,
            "Grid Y": grid_y,
        }
        for (flags, grid_x, grid_y) in [
            struct.unpack("=3l", record[1][2])  # record > DATA > buffer
            for record in records
        ]
    ]

    return table_dictionary
