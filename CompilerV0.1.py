#remove whitespace from reading
#move to next buffer after reading runs out of chars
import re
from tkinter import Variable

output = open("error_log.txt", "w")
output.write("Decaf Error Stack Trace")
output.close()
output = open("error_log.txt", "a")

def parse(file):
    arr = []
    with open(file) as f:
        while True:
            word = f.readline().strip()
            if not word:
                break
            arr.append(word)
    return arr

def log_error(line):
    print(line)
    output.write(str(line))

def determine_error(lexeme):
    if lexeme[0] == '"':
        log_error("ERROR: Invalid String")
    elif "." in lexeme:
        log_error("ERROR: Invalid Double")
    else:
        log_error("ERROR: Invalid Integer")

    

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
    code = open('test.txt')
    lines = code.readlines()

    keywords = parse("keywords.txt")
    declarators = parse("declarators.txt")
    operators = parse("operators.txt")

    token = "null"
    lexeme = ""
    cnt = 0
    prev = ""
    line_num = 1

    while token != "eof":
        if cnt<len(buffer1):
            token = buffer1[cnt]
        if cnt>=len(buffer1):
            token = buffer2[cnt-4096]
        
        if "/*"in lexeme:
            if "*/" in lexeme:
                print("done multi line comment")
                lexeme = ""
            elif token == "eof":
                log_error("Error on line number: " + line_num)
                log_error("ERROR origin: " + lines[line_num-1])
                log_error("ERROR: no closing comment")
            elif token == "\n":
                line_num = line_num + 1  
            else:
                lexeme = lexeme + token
        elif token == "\n":
            if "//" in lexeme:
                print("comment complete")
            elif lexeme != "":
                log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1])
                log_error("ERROR with COMMENT:" + lexeme)
            lexeme = ""
            line_num = line_num + 1
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

                #Know identifier if statements
                #Most likely used in semantic analysis
                if lexeme in symbol_table.keys():
                    #Do nothing for right now           
                    print("Do nothing for now")

                #Unkonwn identifyer and previous was not a keyword
                #Most likely two literals following each other
                elif lexeme not in symbol_table.keys() and (prev not in keywords) and lexeme != "":
                    if integer_regex.fullmatch(lexeme):
                        print("integer lexeme:" + lexeme)
                    elif double_regex.fullmatch(lexeme):
                        print("double lexeme:" + lexeme)
                    elif string_regex.fullmatch(lexeme):
                        print("string lexeme:" + lexeme)
                    else:
                        log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1])
                        determine_error(lexeme)
                
                #New identifier 
                elif lexeme not in symbol_table.keys() and  prev in declarators:
                    if variable_regex.fullmatch(lexeme) != None:
                        print("compare variables")
                        print(lexeme)
                        symbol_table[lexeme] = prev
                    else:
                        log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1])
                        log_error("ERROR: not a valid Variable: "+ lexeme)

                    print("\nSymbol Table:")
                    print(symbol_table.keys())
                    print("")
            prev = lexeme 
            lexeme = ""
        cnt = cnt + 1
    print(line_num)
        
if __name__ == "__main__":
    main()
    


