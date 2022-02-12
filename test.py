import re
test1 = "123."
test2  ="12.3"
test3 ="1.0E+3"
test4= "0x012r"
integer_regex_hex = re.compile("([0-9][0-9]*.[0-9]*)|([0-9][0-9]*.[0-9]*[eE][+-][0-9][0-9]*)")
print(integer_regex_hex.fullmatch(test1))
print(integer_regex_hex.fullmatch(test2))
print(integer_regex_hex.fullmatch(test3))
print(integer_regex_hex.fullmatch(test4))