def process_records(records):
    """Process each record in a list of records, returning lists of subrecords for each."""
    import struct

    count = 0
    record_subrecords = []
    for record in records:
        count += 1
        record_header = record[0]
        record_data = record[1]

        # Subrecord data
        subrecords = []
        process_subrecords = True
        while process_subrecords:
            # Subrecord header
            # Obtain the header of the next sub-record.
            bytes_format = "<4sl"
            srhb_size = struct.calcsize(bytes_format)  # srhb = subrecord_header_buffer
            subrecord_header_buffer = record_data[:srhb_size]
            (subrecord_type, subrecord_size) = struct.unpack(
                bytes_format, subrecord_header_buffer
            )  # unpack from record data

            # Obtain the data of the next sub-record.
            subrecord_data_buffer = record_data[srhb_size : srhb_size + subrecord_size]
            if not len(subrecord_data_buffer) == subrecord_size:
                ValueError(
                    f"Subrecord data buffer slice has different length ({len(subrecord_data_buffer)}) than specified size ({subrecord_size})."
                )

            subrecords.append(
                (
                    # Subrecord header (unpacked)
                    subrecord_type,
                    subrecord_size,
                    # Subrecord data (bytes)
                    subrecord_data_buffer,
                )
            )

            try:
                record_data = record_data[srhb_size + subrecord_size :]
            except IndexError:
                process_subrecords = False

            if len(record_data) == 0:
                process_subrecords = False

        record_subrecords.append(subrecords)
    return (count, record_subrecords)
