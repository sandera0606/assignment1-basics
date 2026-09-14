# 2.1 The Unicode Standard

a) What Unicode character dose chr(0) return?
NULL symbol!

b) chr(0) is null (doesn't show up), repr(chr(0)) is '\x00'

c) in text, literally doesn't show up

# 2.2 Unicode Encodings

a) What are some reasons to prefer training our tokenizer on UTF-8 encoded bytes, rather than UTF-16 or UTF-32? It may be helpful to compare the output of these encodings for various input strings.
UTF16 and UTF32 encodings start to get really long.

b) Consider the following incorrect function...
They try to convert each byte to a unicode character, but not every unicode character is represented by a single byte; many are represented by multiple.

Example: any chinese text

c) Give a two-byte sequence that does not decode to any Unicode character(s)

0xFF 0xFF
* Unicode starting characters only go up to 0xF4

# 2.5 