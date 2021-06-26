def get_info_stream(stream_url: str) -> dict:
    """
    Given the URL of a conda packaged binary (either `.tar.bz2` or `.conda`)
    obtain its info from decompressing the stream.
    """
    if stream_url.endswith(".tar.bz2"):
        legacy_compression = True
    elif stream_url.endswith(".conda"):
        legacy_compression = False
    else:
        raise ValueError(f"{stream_url=}")
    return info_dict
