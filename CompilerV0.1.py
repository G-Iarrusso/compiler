#remove whitespace from reading
#move to next buffer after reading runs out of chars
import re
from tkinter import Variable


def main():
    variable_regex = re.compile("[a-zA-Z][0-9a-zA-Z_]*")
    integer_regex = re.compile("([0-9][0-9]*)|(0(x|X)[0-9a-fA-F][0-9a-fA-F]*)")
    double_regex = re.compile("([0-9][0-9]*.[0-9]*)|([0-9][0-9]*.[0-9]*[eE][+-][0-9][0-9]*)")
    string_regex = re.compile('".*"')
    current_char = 0
    n = 4096
    buffer1 = ["null"]*n
    buffer2 = ["null"]*n
    keywords = []
    operators = []
    declarators=[]
    symbol_table = {}
    c = "s"
    with open("test.txt") as f:
        while c!="eof":
            c = f.read(1)
            if not c and current_char<n:
                buffer1[current_char] = "eof"
                c = "eof"
            elif not c and current_char>=n:
                buffer2[current_char-n] = "eof"
                c = "eof"
            elif c and current_char<n:
                buffer1[current_char] = c
            elif c and current_char>=n:
                buffer2[current_char - n] = c
            current_char = current_char + 1
    with open("keywords.txt") as f:
        while True:
            word = f.readline().strip()
            if not word:
                break
            keywords.append(word)
    with open("declarators.txt") as f:
        while True:
            word = f.readline().strip()
            if not word:
                break
            declarators.append(word)
    with open("operators.txt") as f:
        while True:
            word = f.readline().strip()
            if not word:
                break
            operators.append(word)

    token = "null"
    lexeme = ""
    cnt = 0
    prev = ""
    print("Printing keywords from buffer")
    print(buffer1[0:50])
    while token != "eof":
        token = buffer1[cnt]
        if token == "\n":
            lexeme = ""
        elif  "//" in lexeme:
            lexeme = lexeme + token
        elif token != " " and token!="eof" and token!=";":
            lexeme = lexeme + token
        elif token == " " or token=="eof" or token== ";":
            if (lexeme in keywords):
                print("keyword:" + lexeme)
            elif (lexeme in operators):
                print("operator:" + lexeme)
            else:
                if lexeme in symbol_table.keys():
                    #Do nothing for right now           
                    print("Do nothing for now")
                elif lexeme not in symbol_table.keys() and (prev not in keywords) and lexeme != "":
                    if integer_regex.fullmatch(lexeme):
                        print("integer lexeme:" + lexeme)
                    elif double_regex.fullmatch(lexeme):
                        print("double lexeme:" + lexeme)
                    elif string_regex.fullmatch(lexeme):
                        print("string lexeme:" + lexeme)
                    else:
                        print("non idenfied lexeme:" + lexeme)
                elif lexeme not in symbol_table.keys() and (prev in keywords):
                    if prev in declarators and variable_regex.fullmatch(lexeme) != None:
                        print("compare variables")
                        print(lexeme)
                        symbol_table[lexeme] = prev
                    else:
                        print("not a valid Variable: "+ lexeme)
                    print("\nSymbol Table:")
                    print(symbol_table.keys())
                    print("")

                #print(lexeme)
            prev = lexeme 
            lexeme = ""
        cnt = cnt + 1
        
if __name__ == "__main__":
    main()
    


