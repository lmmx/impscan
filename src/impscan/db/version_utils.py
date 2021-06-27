__all__ = ["sort_package_json_by_version"]


def strip_ver_alpha_chars(version_str: str) -> str:
    REPLACING = False
    new_str = ""
    for char in version_str:
        if char.isalpha():
            if not REPLACING and new_str and new_str[-1] != ".":
                new_str += "."
            REPLACING = True
        elif REPLACING:
            REPLACING = False
            new_str += "0"
            if char != ".":
                new_str += "."
            new_str += char
        else:
            new_str += char
    if new_str.endswith("."):
        new_str += "0"
    return new_str


def version_as_tuple(version_str: str, imply_epoch=False) -> tuple:
    """
    Convert string representing version number to order-able integer tuple.
    If alphabetical characters are in the string, cheat and move these to an
    earlier position by inserting a ".0." within the string which will push
    them back before the entire series they are within (as the use case involves
    looking at most recent first, so deprioritise these builds if possible).
    """
    # print(f"{version_str=}") # uncomment to print out all versions to debug faster
    try:
        if imply_epoch and "!" in version_str:
            version_str = version_str.replace("!", ".")
            imply_epoch = False  # it's explicit not implicit
        if "_" in version_str:
            version_str = version_str.replace("_", "")
        if "+" in version_str:
            version_str = version_str.replace("+", ".")
        if any(map(str.isalpha, version_str)):
            version_str = strip_ver_alpha_chars(version_str)
        if version_str == "":
            version_str = "0"
        if imply_epoch:  # implicit
            version_str = f"0.{version_str}"
        return tuple(map(int, version_str.split(".")))
    except:
        breakpoint()
        raise


def sort_package_json_by_version(j: list[dict]) -> list[dict]:
    has_epoch = any(d for d in j if "!" in d["version"])
    return sorted(
        j,
        key=lambda d: version_as_tuple(d["version"], imply_epoch=has_epoch),
        reverse=True,
    )
