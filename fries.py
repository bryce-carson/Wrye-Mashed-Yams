import marimo

__generated_with = "0.10.9"
app = marimo.App(width="medium", app_title="Fries")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo, records_dropdown):
    def page_fries():
        logo = mo.image("Clint Grant Gibbon smoking cigar PA2003-2130.jpeg")
        danger_callout = mo.callout("This application is highly experimental. You should not use it.", "danger")
        dropdown = records_dropdown()
        return mo.md(
            f"""
            # Fries
            (Ash Yam) Fries is a Morrowind mod management and utility framework based upon Mopy.

            See the extensive [Credits](#/credits)!

            [The ESP plug-in format guide created by Humphrey](https://en.uesp.net/morrow/tech/mw_esm.txt)

            <div data-tooltip="Clint Grant's &quot;Gibbon smoking cigar PA2003-2130&quot;">{logo}</div>

            {danger_callout}

            {dropdown}
            """
        )
    return (page_fries,)


@app.cell(hide_code=True)
def _(mo):
    def page_credits():
        return mo.md(
            r"""
            # Credits
            - Individual Mopy contributors
            - Polemos
            - Wrye

            "A stand alone edition of Wrye Mash, based on the latest Yacoby source." --- Polemos
            """
        )
    return (page_credits,)


@app.cell(hide_code=True)
def _(mo):
    records_file_chooser = mo.ui.file_browser(filetypes = [".ess", ".esm", ".esp"],
                                              label = "Select an Elder Scrolls file.",
                                             multiple=False)
    records_file_chooser
    return (records_file_chooser,)


@app.cell
def _(mo, records_file_chooser):
    import src.mash.records as recordlib
    from os import path


    # Without an input_stream the Wrye record classes are more or less unusable.
    input_file = open(records_file_chooser.path(), "rb")
    reader = recordlib.Tes3Reader(
        path.basename(records_file_chooser.path()), input_file
    )

    records = []
    while not reader.atEnd():
        (name, size, deleted_flag, frozen_flag) = reader.unpackRecHeader()
        header = (name, size, deleted_flag, frozen_flag)
        data = reader.read(size)

        # print(name, round(size / 1024))
        records.append((header, data))

    input_file.close()
    unique_record_types = [
        str(record_type)[1:7][1:5]
        for record_type in set([record[0][0] for record in records])
    ]

    selected_record_type = mo.ui.dropdown(
        unique_record_types, "CELL", label="Pick a record type."
    )

    selected_record_type
    return (
        data,
        deleted_flag,
        frozen_flag,
        header,
        input_file,
        name,
        path,
        reader,
        recordlib,
        records,
        selected_record_type,
        size,
        unique_record_types,
    )


@app.cell
def _(mo, selected_record_type):
    if selected_record_type.value == "CELL":
        cellMd = mo.md(
            r"""
            # CELL objects
            Cell objects are record-derived objects composed of cells, of course. Let's analyze them until we get to the point where we can determine if an NPC has moved from its original position as defined in a master file (or a plugin!). We'll be comparing ESS files against ESM or ESP files.

            Comparing against ESM and ESP files will require knowing whether a reference exists in other records as well.

            Some CELLs are unnamed, and their NAME subrecord size is one byte, the NULL byte.

            Let's investigate the DATA subrecord, beginning with one which looks like it has an interesting group of subrecords which aren't that well handled in TES3CMD (as far as I can tell).
            """
        )
        cellMd
    return (cellMd,)


@app.cell
def _(mo, path, records, records_file_chooser, selected_record_type):
    from src.cyber.records import process_records


    records_of_selected_type = filter(lambda b: f'{selected_record_type.value}'.encode().startswith(b[0][0]), records)
    (count, selected_record_type_subrecords) = process_records(records_of_selected_type)

    # Record-type functions module, or "read the fucking manual, you git!"
    import src.cyber.record_type_functions as rtfm

    match selected_record_type.value:
        case "NPC_":
            summary = mo.ui.table(rtfm.NPC_(selected_record_type_subrecords))
        case "CELL":
            flags_xy = rtfm.CELL(selected_record_type_subrecords)
            summary = mo.ui.array([
                mo.ui.table(flags_xy)
            ])
        case None:
            summary = "Select a record type."
        case "STLN":
            summary = mo.tree(selected_record_type_subrecords)
        case _:
            summary = mo.vstack(["Select a different record type. No record-specific summary is implemented for current selection. A general tree listing of the subrecords is displayed instead.",
                                mo.plain_text(str(selected_record_type_subrecords))])

    summary_tree = mo.tree(
        [
            summary,
            f'There are {count} {selected_record_type.value} records in {path.basename(records_file_chooser.path())}.',
        ],
        label = "Record type selection and summary."
    )

    summary_tree
    return (
        count,
        flags_xy,
        process_records,
        records_of_selected_type,
        rtfm,
        selected_record_type_subrecords,
        summary,
        summary_tree,
    )


@app.cell
def _(selected_record_type, selected_record_type_subrecords, summary):
    if hasattr(summary, "value") and selected_record_type == "NPC_":
        [selected_record_type_subrecords[i] for i in [item["index"] for item in summary.value]]
    return


if __name__ == "__main__":
    app.run()
