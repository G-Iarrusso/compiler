#Gianluca Iarrusso 170315920
#John Barber-Ormerod 170148230
#Phase 1 of CP 471 Project
#2022-02-21
#remove whitespace from reading
#move to next buffer after reading runs out of chars
from cmath import log
from queue import Empty
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
    

def main():
    variable_regex = re.compile("[a-zA-Z][0-9a-zA-Z_]*")
    integer_regex = re.compile("(-)?(([0-9]+)|(0(x|X)[0-9a-fA-F]+))")
    double_regex = re.compile("(-)?(([0-9]+.[0-9]*)|([0-9]+.[0-9]*[eE][+-][0-9]+))")
    string_regex = re.compile('"[^"]*"')
    current_char = 0
    n = 4096
    buffer1 = ["null"]*n
    buffer2 = ["null"]*n
    keywords = []
    operators = []
    declarators=[]
    symbol_table = {}
    read_order = []
    bracket_stack =[]
    open_bracket = {"(": "round","[": "square","{": "squigly"}
    close_bracket = {")": "round","]": "square","}": "squigly"}
    c = "s"

    def determine_error(is_unknown=False):
        log_error("ERROR LEXEME IS: " + lexeme)
        if not(lexeme[0] == '"' and lexeme[-1] == '"') and '"' in lexeme:
            log_error("ERROR: Invalid String\n")
        elif "." in lexeme:
            log_error("ERROR: Invalid Double\n")
        elif is_unknown:
            log_error("UNKNOWN ERROR duplicate declaration\n")
        elif lexeme not in symbol_table.keys():
            log_error("UNKNOWN SYMBOL\n")
        elif not lexeme.isnumeric():
            log_error("ERROR: Invalid Integer\n")


    def handle_lexeme():
        #Know identifier if statements
        #Most likely used in semantic analysis
        if lexeme in symbol_table.keys():
            #Do nothing for right now
            if prev == symbol_table[lexeme] or prev in declarators:
                log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1][:-1])
                determine_error(True)
            read_order.append([lexeme, symbol_table.get(lexeme)])
            print(lexeme)
            print("Do nothing for now")
        #Unkonwn identifyer and previous was not a keyword
        #Most likely two literals following each other
        elif lexeme not in symbol_table.keys() and (prev not in keywords) and lexeme != "" :
            if integer_regex.fullmatch(lexeme):
                print("integer lexeme:" + lexeme)
                read_order.append([lexeme, "int"])
            elif double_regex.fullmatch(lexeme):
                print("double lexeme:" + lexeme)
                read_order.append([lexeme, "double"])
            elif string_regex.fullmatch(lexeme):
                print("string lexeme:" + lexeme)
                read_order.append([lexeme, "string"])
            else:
                log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1][:-1])
                determine_error()
        
        #New identifier 
        elif lexeme not in symbol_table.keys() and  prev in declarators and lexeme != "":
            if variable_regex.fullmatch(lexeme) != None:
                print("compare variables")
                print(lexeme)
                symbol_table[lexeme] = prev
                read_order.append([lexeme, symbol_table.get(lexeme)])
            else:
                log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1][:-1])
                log_error("ERROR not a valid Variable: "+ lexeme)

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
        
        if (token in operators or token =="&" or token == "|" or token =="!") and '"' not in lexeme:
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
            elif (token + token2) == "->":
                token = token + token2
                cnt = cnt+1
                log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1])
                log_error("UNKNOWN SYMBOL:" + token)
                lexeme = ""
                token = ""

        # multi line comment handler
        if "/*"in lexeme:
            if "*/" in lexeme:
                print("done multi line comment")
                prev = lexeme 
                lexeme = ""
                if token == "\n":
                    line_num = line_num + 1
            elif token == "eof":
                log_error("ERROR on line number: " + str(line_num))
                log_error("ERROR origin: " + lines[line_num-1][:-1])
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
                log_error("ERROR on line " + str(line_num) + ": " + lines[line_num-1][:-1])
                log_error("UNKNOWN ERROR broken line:" + lexeme)
            prev = lexeme 
            lexeme = ""
            line_num = line_num + 1
        #comment handler
        elif  "//" in lexeme:
            lexeme = lexeme + token
        #handle lexeme
        elif (token == " " and '"' not in lexeme)or token=="eof" or token== ";" or token == ".":

            if (lexeme in keywords):
                read_order.append([lexeme, "Keyword"])
                if token == ".":
                    read_order.append([token, "operator"])
                prev = lexeme 
            elif (lexeme in operators):
                read_order.append([lexeme, "Operator"])
                prev = lexeme 
            elif lexeme !="":
                handle_lexeme()
                prev = lexeme 
            if token == ";":
                read_order.append([";", "Operator"])
            lexeme = ""
        elif token in operators and '"' not in lexeme:
            handle_lexeme()
            read_order.append([token, "Operator"])
            prev = lexeme 
            lexeme = ""
        elif token == '"' and '"' in lexeme:
            lexeme = lexeme +token
            handle_lexeme()
            prev = lexeme 
            lexeme = ""
        else:
            lexeme = lexeme + token
        cnt = cnt + 1
    print(line_num)
    print(read_order)
    print(symbol_table)
    
    def parser(tokens):
        expr_block_constant = [["Expr","=","LValue"],["LValue"],["Call"],["Expr","+","Expr"],["Expr","-","Expr"],["Expr","*","Expr"],["Expr","/","Expr"],["Expr","%","Expr"],["Expr","<","Expr"],["Expr","<=","Expr"],["Expr",">","Expr"],["Expr",">=","Expr"],["Expr","==","Expr"],["Expr","!=","Expr"],["Expr","&&","Expr"],["Expr","||","Expr"],["Constant"]]
        expr_block = [["Expr","=","LValue"],["LValue"],["Call"],["Expr","+","Expr"],["Expr","-","Expr"],["Expr","*","Expr"],["Expr","/","Expr"],["Expr","%","Expr"],["Expr","<","Expr"],["Expr","<=","Expr"],["Expr",">","Expr"],["Expr",">=","Expr"],["Expr","==","Expr"],["Expr","!=","Expr"],["Expr","&&","Expr"],["Expr","||","Expr"]]
        lval_block = [["ident",".","Expr"],["]","Expr","[","Expr"]]
        call = [")","Actuals","(","ident",".","Expr"]
        parse_table = [["terminals","ident","intConstant","doubleConstant","boolConstant","stringConstant","null","int","double","bool","string","class","void","interface","this","extends","implements","for","while","if","else","return","break","new","NewArray","Print","ReadInteger","ReadLine","true","false",";","&&","||","!",";",",",".","[","{","(","=","+","-","*","/","%","<=","==","!="],
                    ["Program","Decl",None,None,None,None,None,"Decl","Decl","Decl","Decl","Decl","Decl","Decl"],
                    ["Decl",[["VariableDecl"],["FunctionDecl"]],None,None,None,None,None,[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],"ClassDecl","FunctionDecl","InterfaceDecl"],
                    ["VariableDecl",[";","Variable"],None,None,None,None,None,[";","Variable"],[";","Variable"],[";","Variable"],[";","Variable"]],
                    ["Variable",["ident","Type"],None,None,None,None,None,["ident","Type"],["ident","Type"],["ident","Type"],["ident","Type"]],
                    ["Type",[["]","[","Type"],["ident"]],None,None,None,None,None,[["int"],["ident","Type"]],[["double"],["ident","Type"]],[["bool"],["ident","Type"]],[["string"],["ident","Type"]]],
                    ["FunctionDecl",["StmtBlock",")","Formals","(","ident","Type"],None,None,None,None,None,["StmtBlock",")","Formals","(","ident","Type"],["StmtBlock",")","Formals","(","ident","Type"],["StmtBlock",")","Formals","(","ident","Type"],["StmtBlock",")","Formals","(","ident","Type"],None,["StmtBlock",")","Formals","(","ident","void"]],
                    ["Formals",[[",","Variable"],["Variable"]],None,None,None,None,None,[[",","Variable"],["Variable"]],[[",","Variable"],["Variable"]],[[",","Variable"],["Variable"]],[[",","Variable"],["Variable"]]],
                    ["ClassDecl",None,None,None,None,None,None,None,None,None,None,["}","Field","{",",","ident","implements","ident","extends","ident","class"]],
                    ["Field",[["VariableDecl"],["FunctionDecl"]],None,None,None,None,None,[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],None,"FunctionDecl"],
                    ["Interface",None,None,None,None,None,None,None,None,None,None,None,None,["}","Prototype","{","ident","interface"]],
                    ["Prototype",[";",")","Formals","(","ident","Type"],None,None,None,None,None,[";",")","Formals","(","ident","Type"],[";",")","Formals","(","ident","Type"],[";",")","Formals","(","ident","Type"],[";",")","Formals","(","ident","Type"],None,[";",")","Formals","(","ident","void"]],
                    ["StmtBlock",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,["}","Stmt","VariableDecl","{"]],
                    ["Stmt",[";","Expr"],[";","Expr"],[";","Expr"],[";","Expr"],[";","Expr"],None,None,None,None,None,None,None,None,[";","Expr"],None,None,"ForStmt","WhileStmt","IfStmt",None,"ReturnStmt","BreakStmt",[";","Expr"],[";","Expr"],"PrintStmt",[";","Expr"],[";","Expr"],None,None,None,None,None,[";","Expr"],None,None,None,None,["}","Stmt","VariableDecl","{"],[";","Expr"],None,None,[";","Expr"]],
                    ["IfStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,["Stmt","else","Stmt",")","Expr","(","if"],None],
                    ["WhileStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,["Stmt",")","Expr","(","while"]],
                    ["ForStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,["Stmt",")","Expr",";","Expr",";","Expr","(","for"]],
                    ["ReturnStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,[";","Expr","return"]],
                    ["BreakStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,[";","break"]],
                    ["PrintStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,[";",")",",","Expr","(","Print"]],
                    ["Expr",expr_block,expr_block_constant,expr_block_constant,expr_block_constant,expr_block_constant,None,None,None,None,None,None,None,None,expr_block.append(["this"]),None,None,None,None,None,None,None,None,expr_block.append(["ident","new"]),expr_block.append([")","Type",",","Expr","(","NewArray"]),None,expr_block.append([")","(","ReadInteger"]),expr_block.append([")","(","ReadLine"]),None,None,None,None,None,expr_block.append(["Expr","!"]),None,None,None,None,None,expr_block.append([")","Expr","("]),None,None,expr_block.append(["Expr","-"])],
                    ["LValue",lval_block.append("ident"),lval_block,lval_block,lval_block,lval_block,None,None,None,None,None,None,None,None,lval_block,None,None,None,None,None,None,None,None,lval_block,lval_block,None,lval_block,lval_block,None,None,None,None,None,lval_block,None,None,None,None,None,lval_block,None,None,lval_block],
                    ["Call",[")","Actuals","(","ident"],call,call,call,call,None,None,None,None,None,None,None,None,call,None,None,None,None,None,None,None,None,call,call,None,call,call,None,None,None,None,None,call,None,None,None,None,call,None,None,call],
                    ["Actuals",[",","Expr"],[",","Expr"],[",","Expr"],[",","Expr"],[",","Expr"],None,None,None,None,None,None,None,None,[",","Expr"],None,None,None,None,None,None,None,None,[",","Expr"],[",","Expr"],None,[",","Expr"],[",","Expr"],None,None,None,None,None,[",","Expr"],None,None,None,None,[",","Expr"],None,None,[",","Expr"]],
                    ["Constant","intConstant","doubleConstant","boolConstant","stringConstant","null"]]
        parser_stack =["Program"]
        code_queue = tokens
        code_queue_pointer = 0
        parser_push_loc =[0,len(parser_stack)-1]
        stars = [("Prototype", "InterfaceDecl"),("Field", "ClassDecl"),("VariableDecl", "StmtBlock"),("Stmt","StmtBlock")] #Tuple(thing with *, Thing producing it)
        pluses = [("Decl", "Program"),("implements ident", "ClassDecl"),("Expr", "PrintStmt"),("Expr", "Actuals"),("Variable", "Formals")]
        already_attempted =[]
        already_handled= []
        is_complete=0
        bad_push =0
        pushmode = 1
        def parse(code_queue, code_queue_pointer, parser_stack, parser_push_loc, already_attempted, bad_push, pushmode):
            cnt = 0
            while not code_queue_pointer >= len(code_queue):
                cnt = cnt +1
                print("""\n\nNext iteration: """ + str(cnt) +"""\n"""+
                    """Pushmode: """+ str(pushmode) +"\n"+
                    """Looking for: """+ str(code_queue[code_queue_pointer])+"\n"+
                    """Current parse stack """ + str(parser_stack) +"\n"+
                    """Current parse locs """+ str(parser_push_loc) + "\n" +
                    """Already tried """ + str(already_attempted) + "\n" +
                    """Length of the code queue """ + str(len(code_queue))+"\n"+
                    """Code queue pointer """ + str(code_queue_pointer) + "\n" +
                    """Bad Push """ + str(bad_push))
                if pushmode:
                    """
                    Pushing logic
                    mini pop, if last item is a non terminal that doesn t have a + or * pop it and replace it with its production
                    only push if the addition isnt in already tried
                    is single item
                        push it to stack
                        update the parser loc
                    is a list
                        push it to stack
                        update the parser loc
                    is a list of lists
                        for list in lists
                            push to parser stack
                            update stack loc
                            parse ??? Need to flush out more
                    if last item not terminal
                        retain push mode
                    if no good push:
                        bad_push = 1
                        pushmode = 0
                    """
                    pushmode = 0
                    leave_on = 0
                    x =-1
                    for row in range(0,len(parse_table)):
                        for col in range(0,len(parse_table[row])):
                            if parser_stack[-1] == parse_table[row][0] and parse_table[row][col] != None and parse_table[row][col] not in already_attempted:
                                x = row
                                break
                    #Find the column containing our terminal 
                    if code_queue[code_queue_pointer][0] in parse_table[0]:
                        y = parse_table[0].index(code_queue[code_queue_pointer][0])
                    elif code_queue[0][0] in symbol_table.keys():
                        y = 1
                    if x == -1:
                        pushmode = 0
                        break
                    transaction = parse_table[x][y]
                    print("found transaction: "+ str(transaction) + " at " + str(x) + " "+str(y))
                    if transaction not in already_attempted :
                        print("new transaction: "+ str(transaction))
                        already_attempted.append(transaction)
                        #Check if there are multiple values to append
                        print("pushloc value before:"+str(parser_push_loc))
                        if isinstance(transaction, list):
                            #Check if we're at a branching point
                            if isinstance(transaction[0],list):
                                print("list of lists")
                                for item in pluses:
                                    if item[1] == parser_stack[-1]:
                                        leave_on = 1
                                if not leave_on:
                                    parser_stack.pop()
                                    parser_push_loc.pop()
                                    if len(parser_stack)>1:
                                        parser_push_loc.append(len(parser_stack)-1)
                                for components in transaction:
                                    for component in components:
                                        parser_stack.append(component)
                                    parser_push_loc.append(len(parser_stack)-1)
                                    outcome, code_queue_pointer=parse(code_queue, code_queue_pointer, parser_stack, parser_push_loc, already_attempted, bad_push, 1)
                                    if outcome:
                                        print("Good Outcome")
                                        break
                            else:
                                for item in pluses:
                                    if item[1] == parser_stack[-1]:
                                        leave_on = 1
                                if not leave_on:
                                    parser_stack.pop()
                                    parser_push_loc.pop()
                                    if len(parser_stack)>1:
                                        parser_push_loc.append(len(parser_stack)-1)
                                for component in transaction:
                                    parser_stack.append(component)
                                parser_push_loc.append(len(parser_stack)-1)
                        else:
                            for item in pluses:
                                if item[1] == parser_stack[-1]:
                                    leave_on = 1
                            if not leave_on:
                                parser_stack.pop()
                                parser_push_loc.pop()
                                if len(parser_stack)>1:
                                    parser_push_loc.append(len(parser_stack)-1)
                            parser_stack.append(transaction)
                            parser_push_loc.append(len(parser_stack)-1)
                        print("pushloc value after:"+str(parser_push_loc))
                        print("After itteration parser stack: " + str(parser_stack))
                    else:
                        print("Bad Push")
                        bad_push = 1
                        pushmode = 0
                    if 0 < len(parser_stack):
                        if parser_stack[-1] not in parse_table[0] and not bad_push:
                            pushmode=1
                else:  
                    """
                    Popping logic
                    if bad_push:
                        add push to already tried
                        purge back to last push
                        bad_push = 0
                    if terminal not same trerminal in code
                        bad_push=1
                    if good pop
                        pop latest
                        update code queue pointer
                        update parse stack loc
                        clear already tried
                    if next is terminal 
                        retain pop mode
                    """
                    pushmode = 1
                    if bad_push:
                        print("clensing the bad")
                        while len(parser_stack)>parser_push_loc[-2]+1:
                            parser_stack.pop()
                        parser_push_loc.pop()
                        already_attempted=[]
                        bad_push = 0
                    elif parser_stack[-1] == code_queue[code_queue_pointer][0] or (parser_stack[-1] == "ident" and code_queue[code_queue_pointer][0] in symbol_table.keys()):
                        print("Match found")
                        already_attempted=[]
                        parser_stack.pop()
                        code_queue_pointer = code_queue_pointer + 1
                    elif parser_stack[-1] != code_queue[code_queue_pointer][0] or (parser_stack[-1] == "ident" and code_queue[code_queue_pointer][0] not in symbol_table.keys()):
                        bad_push = 1
                    if code_queue_pointer < len(code_queue):
                        if parser_stack[-1] == code_queue[code_queue_pointer][0] or (parser_stack[-1] == "ident" and code_queue[code_queue_pointer][0] in symbol_table.keys()):
                            pushmode=0
                    print(parser_stack)
            return 1, code_queue_pointer
        print("coutcome " + str(parse(code_queue, code_queue_pointer, parser_stack, parser_push_loc, already_attempted, bad_push, pushmode)[0]))        
    parser(read_order)
if __name__ == "__main__":
    main()
    


