#remove whitespace from reading
#move to next buffer after reading runs out of chars
def main():
    current_char = 0
    n = 4096
    buffer1 = ["null"]*n
    buffer2 = ["null"]*n
    keywords = []
    operators = []
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
    with open("operators.txt") as f:
        while True:
            word = f.readline().strip()
            if not word:
                break
            operators.append(word)

    token = "null"
    lexeme = ""
    cnt = 0
    print("Printing keywords from buffer")
    while token != "eof":
        token = buffer1[cnt]
        if token != " " and token!="eof":
            lexeme = lexeme + token
        elif token == " " or token=="eof":
            if (lexeme in keywords):
                print("keyword:" + lexeme)
            elif (lexeme in operators):
                print("operator:" + lexeme)
            else:
                if lexeme in symbol_table.values():
                    #Do nothing for right now
                    print("Do nothing for now")
                elif lexeme not in symbol_table.values() and (prev not in keywords):
                    print(lexeme)
                elif lexeme not in symbol_table.values() and (prev in keywords):
                    symbol_table[lexeme] = prev
                    print(symbol_table)

                #print(lexeme)

            prev = lexeme 
            lexeme = ""
        cnt = cnt + 1

        
if __name__ == "__main__":
    main()
    


