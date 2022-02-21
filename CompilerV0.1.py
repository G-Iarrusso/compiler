#remove whitespace from reading
#move to next buffer after reading runs out of chars
import re
from tkinter import Variable

output = open("error_log.txt", "w")
output.write("Decaf Error Stack Trace\n")
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
    #print(line)
    output.write(str(line)+"\n")

def determine_error(lexeme, is_unknown=False):
    log_error("ERROR LEXEME IS: " + lexeme)
    if not(lexeme[0] == '"' and lexeme[-1] == '"') and '"' in lexeme:
        log_error("ERROR: Invalid String")
    elif "." in lexeme:
        log_error("ERROR: Invalid Double")
    elif is_unknown:
        log_error("UNKNOWN ERROR")
    elif not lexeme.isnumeric():
        log_error("ERROR: Invalid Integer")

    

def main():
    variable_regex = re.compile("[a-zA-Z][0-9a-zA-Z_]*")
    integer_regex = re.compile("(-)?(([0-9]+)|(0(x|X)[0-9a-fA-F]+))")
    double_regex = re.compile("(-)?(([0-9]+.[0-9]*)|([0-9]+.[0-9]*[eE][+-][0-9]+))")
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

    def handle_lexeme():
        #Know identifier if statements
        #Most likely used in semantic analysis
        if lexeme in symbol_table.keys():
            #Do nothing for right now
            if prev == symbol_table[lexeme] or prev in declarators:
                log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1])
                determine_error(lexeme,True)
            print(lexeme)     
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
    comments = parse("comments.txt")

    token = "null"
    token2 = "null"
    lexeme = ""
    cnt = 0
    prev = ""
    line_num = 1

    while token != "eof":
        if cnt<len(buffer1):
            token = buffer1[cnt]
        if cnt>=len(buffer1):
            token = buffer2[cnt-4096]
        
        if token in operators or token =="&" or token == "|" or token =="!":
            if cnt<len(buffer1):
                token2 = buffer1[cnt+1]
            if cnt>=len(buffer1):
                token2 = buffer2[cnt-4096+1]
            if token2 in operators and (token + token2) in operators:
                token = token + token2
                cnt = cnt+1
            elif (token2 == "/" or token2 == "*") and (token + token2) in comments:
                cnt = cnt+1
                token = token + token2
            elif (token2 =="&" or token2 == "|")and (token + token2) in operators:
                token = token + token2
                cnt = cnt+1
        # multi line comment handler
        if "/*"in lexeme:
            if "*/" in lexeme:
                print("done multi line comment")
                lexeme = ""
                if token == "\n":
                    line_num = line_num + 1
            elif token == "eof":
                log_error("Error on line number: " + line_num)
                log_error("ERROR origin: " + lines[line_num-1])
                log_error("ERROR: no closing comment")
            elif token == "\n":
                line_num = line_num + 1
            else:
                lexeme = lexeme + token
        #new line handler
        elif token == "\n":
            if "//" in lexeme:
                print("comment complete")
            elif lexeme != "":
                log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1])
                log_error("UNKNOWN ERROR:" + lexeme)
            lexeme = ""
            line_num = line_num + 1
        #comment handler
        elif  "//" in lexeme:
            lexeme = lexeme + token
        #handle lexeme
        elif token == " " or token=="eof" or token== ";":
            if (lexeme in keywords):
                print("keyword:" + lexeme)
                prev = lexeme 
            elif (lexeme in operators):
                print("operator:" + lexeme)
                prev = lexeme 
            elif lexeme !="":
                handle_lexeme()
                prev = lexeme 
            lexeme = ""
        elif token in operators:
            handle_lexeme()
            lexeme = ""
        else:
            lexeme = lexeme + token
        cnt = cnt + 1
    print(line_num)
    print(lines)
        
if __name__ == "__main__":
    main()
    


