ENCODING_TO_NATIVE = {
    "bool": "?",
    "i8": "b",
    "u8": "B",
    "i16": "h",
    "u16": "H",
    "i32": "i",
    "u32": "I",
    "i64": "q",
    "u64": "Q",
    "f32": "f",
    "f64": "d",
}
DECODING_TO_GENERIC = {v: k for k, v in ENCODING_TO_NATIVE.items()}


# maps from generic to struct c encoding
def to_native_encoding(generic_encoding):
    encoding_str = ""
    for encoding in generic_encoding.split(","):
        c = ENCODING_TO_NATIVE.get(encoding)
        if c is None:
            raise ValueError(f"Encoding {encoding} not defined")
        encoding_str += c
    return "!" + encoding_str  # use network byte order ("!")


def to_generic_encoding(native_encoding):
    encoding = DECODING_TO_GENERIC.get(native_encoding)
    if encoding is None:
        raise ValueError(f"Encoding {native_encoding} not defined")
    return encoding
