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

    def determine_error():
        log_error("ERROR LEXEME IS: " + lexeme)
        if not(lexeme[0] == '"' and lexeme[-1] == '"') and '"' in lexeme:
            log_error("ERROR: Invalid String\n")
        elif "." in lexeme:
            log_error("ERROR: Invalid Double\n")
        elif lexeme not in symbol_table.keys():
            log_error("UNKNOWN SYMBOL\n")
        elif not lexeme.isnumeric():
            log_error("ERROR: Invalid Integer\n")


    def handle_lexeme():
        #Know identifier if statements
        #Most likely used in semantic analysis
        if lexeme in symbol_table.keys():
            #Do nothing for right now
            read_order.append([lexeme, symbol_table.get(lexeme), line_num])
            print(lexeme)
            print("Do nothing for now")
        #Unkonwn identifyer and previous was not a keyword
        #Most likely two literals following each other
        elif lexeme not in symbol_table.keys() and lexeme != "" :
            if integer_regex.fullmatch(lexeme):
                print("integer lexeme:" + lexeme)
                read_order.append([lexeme, "intConstant", line_num])
            elif double_regex.fullmatch(lexeme):
                print("double lexeme:" + lexeme)
                read_order.append([lexeme, "doubleConstant", line_num])
            elif string_regex.fullmatch(lexeme):
                print("string lexeme:" + lexeme)
                read_order.append([lexeme, "stringConstant", line_num])
            elif variable_regex.fullmatch(lexeme) != None:
                print("compare variables")
                print(lexeme)
                symbol_table[lexeme] = prev
                read_order.append([lexeme, symbol_table.get(lexeme), line_num])
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
    panic = parse("panic_symbols.txt")

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
                handle_lexeme()
            prev = lexeme 
            lexeme = ""
            line_num = line_num + 1
        #comment handler
        elif  "//" in lexeme:
            lexeme = lexeme + token
        #handle lexeme
        elif (token == " " and '"' not in lexeme)or token=="eof" or token== ";" or token == ".":

            if (lexeme in keywords):
                read_order.append([lexeme, "Keyword", line_num])
                if token == ".":
                    read_order.append([token, "operator", line_num])
                prev = lexeme 
            elif (lexeme in operators):
                read_order.append([lexeme, "Operator", line_num])
                prev = lexeme 
            elif lexeme !="":
                handle_lexeme()
                prev = lexeme 
            if token == ";":
                read_order.append([";", "Operator", line_num])
            lexeme = ""
        elif token in operators and '"' not in lexeme:
            handle_lexeme()
            read_order.append([token, "Operator", line_num])
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

    #Start of Parser-------------------------------------------------------------------------------------------------------------------------------------
    read_order.append(["$","eof",line_num])
    global tokens
    global tokens_current

    tokens = read_order
    tokens_current = 0
    # one line of inputs is not then falses with an else of true
    # multiple is any of them are true then true otherwise false
    def program():
        global tokens_current
        if not decl():
            return False
        while decl():
            print("Start of Program")
        if tokens[tokens_current][0] == "$":
            return True
        else:
            return False
    #Add other Declarations
    def decl():
        print("Current Token: " + tokens[tokens_current][0])
        if VariableDecl():
            return True
        if FunctionDecl():
            return True
        if tokens[tokens_current][0] == "class":
            if ClassDecl():
                return True
        if tokens[tokens_current][0] == "interface":
            if InterfaceDecl():
                return True
        return False
    def InterfaceDecl():
        if not Terminals("interface"):
            return False
        if not ident():
            return False
        if not Terminals("{"):
            return False
        while True:
            troupleProto = Prototype()
            if troupleProto == 0:
                break
            elif troupleProto == -1:
                return False
        if not Terminals("}"):
            return False
        else:
            return True
    def Prototype():
        if tokens[tokens_current][0]!="}":
            if not Terminals("void") and not Type():
                return -1
            if not ident():
                return -1
            if not Terminals("("):
                return -1
            if not Formals():
                return -1
            if not Terminals(")"):
                return -1
            if not Terminals(";"):
                return -1
            else:
                return 1
        else:
            return 0
    def ClassDecl():
        if not Terminals("class"):
            return False
        if not ident():
            return False
        if tokens[tokens_current][0] == "extends":
            if not Terminals("extends"):
                return False
            if not ident():
                return False
        if tokens[tokens_current][0] == "implements":
            if not Terminals("implements"):
                return False
            if not ident():
                return False
            while tokens[tokens_current][0] == ",":
                if not Terminals(","):
                    return False
                if not ident():
                    return False
        if not Terminals("{"):
            return False
        while True:
            troupleField = Field()
            if troupleField == 0:
                break
            elif troupleField == -1:
                return False
        if not Terminals("}"):
            return False
        else:
            return True
    def Field():
        if tokens[tokens_current][0] == "int" or tokens[tokens_current][0] == "string" or tokens[tokens_current][0] == "double" or tokens[tokens_current][0] == "bool" or tokens[tokens_current][0] in symbol_table.keys():
            state = VariableDeclAux2()
            if state == -1:
                return -1
            if state == 1:
                return 1
            
        if tokens[tokens_current][0] == "int" or tokens[tokens_current][0] == "string" or tokens[tokens_current][0] == "double" or tokens[tokens_current][0] == "bool" or tokens[tokens_current][0] == "void" or tokens[tokens_current][0] in symbol_table.keys():    
            if FunctionDecl():
                return 1
            else:
                return -1
        else:
            return 0
    def VariableDeclAux2(is_ident = False):
        global tokens_current
        if not Var():
            return -1
        if not Terminals(";"):
            tokens_current = tokens_current - 2
            return 0
        return 1
    def VariableDecl():
        if not Var():
            return False
        if not Terminals(";"):
            return False
        return True
    def FunctionDecl():
        if not Type() and not Terminals("void"):
            return False
        if not ident():
            return False
        if not Terminals("("):
            return False
        if not Formals():
            return False
        if not Terminals(")"):
            return False
        if not StmtBlock():
            return False
        else:
            return True
    def Formals():
        if Var():
            while tokens[tokens_current][0] == ",":
                Terminals(",")
                if not Var():
                    return False 
        return True 
    def VariableDeclAux(is_ident = False):
        global tokens_current
        if not Var():
            if is_ident:
                tokens_current = tokens_current - 1
            return 0
        if not Terminals(";"):
            return -1
        return 1

    def StmtBlock():
        if not Terminals("{"):
            return False
        while True:
            if tokens[tokens_current][0] in symbol_table.keys():
                troupleVar = VariableDeclAux(is_ident = True)
            else:
                troupleVar = VariableDeclAux()
            if troupleVar == -1:
                return False
            elif troupleVar == 0:
                break
        while True:
            trouple = Stmt()
            if trouple == 0:
                break
            elif trouple == -1:
                return False
        if not Terminals("}"):
            return False
        else: 
            return True 
    def Stmt():
        print("Found a statement")
        if tokens[tokens_current][0] in symbol_table.keys() or "Constant" in tokens[tokens_current][1] or tokens[tokens_current][0] == "this" or tokens[tokens_current][0] == "new" or tokens[tokens_current][0] == "NewArray" or tokens[tokens_current][0] == "ReadInteger" or tokens[tokens_current][0] == "ReadLine" or tokens[tokens_current][0] == "!" or tokens[tokens_current][0] == "(" or tokens[tokens_current][0] == "-":
            if not Expr():
                print("Oops no expression")
                return -1
            if not Terminals(";"):
                return -1
            else:
                return True
        elif tokens[tokens_current][0] == "{":
            if StmtBlock():
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "while":
            if WhileStmt():
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "for":
            if ForStmt():
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "return":
            if ReturnStmt():
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "if":
            if IfStmt():
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "Print":
            if PrintStmt():
                return True
            else:
                -1
        elif tokens[tokens_current][0] == "break":
            if BreakStmt:
                return True
            else:
                return -1
        else:
            return 0  
    def WhileStmt():
        if not Terminals("while"):
            return False
        if not Terminals("("):
            return False
        if not Expr():
            return False
        if not Terminals(")"):
            return False
        if not Stmt():
            return False
        else:
            return True
    #Needs to be re-tooled
    def ForStmt():
        if not Terminals("for"):
            return False
        if not Terminals("("):
            return False
        if Expr():
            if not Terminals(";"):
                return False
        if not Expr():
            return False
        if not Terminals(";"):
            return False
        Expr()
        if not Terminals(")"):
            return False
        if not Stmt():
            return False
        else:
            return True
    def ReturnStmt():
        if not Terminals("return"):
            return False
        Expr()
        if not Terminals(";"):
            return False
        else:
            return True
    def IfStmt():
        if not Terminals("if"):
            return False
        if not Terminals("("):
            return False
        if not Expr():
            return False
        if not Terminals(")"):
            return False
        if not Stmt():
            return False
        if Terminals("else"):
            if not Stmt():
                return False
        else:
            return True
    def PrintStmt():
        if not Terminals("Print"):
            return False
        if not Terminals("("):
            return False
        if not Expr():
            return False
        while tokens[tokens_current][0] == ",":
            Terminals(",")
            if not Expr():
                return False
        if not Terminals(")"):
            return False
        if not Terminals(";"):
            return False
        else:
            return True
    def BreakStmt():
        if not Terminals("break"):
            return False
        if not Terminals(";"):
            return False
        else:
            return True  
    
    def Expr():
        print("Here from statement")
        if tokens[tokens_current][0] in symbol_table.keys() and ("Constant" not in tokens[tokens_current][1]):
            if not ident():
                return False
            if tokens[tokens_current][0] == "=":
                print("Have an equals")
                if not Terminals("="):
                    return False
                print("Found Equals")
                if not Expr():
                    return False
                print("Found our expression")
                if not ExprPrime():
                    return False
                else:
                    return True
            elif tokens[tokens_current][0] == "(":
                if not Terminals("("):
                    return False
                if not Actuals():
                    return False
                if not Terminals(")"):
                    return False
                if not ExprPrime():
                    return False
                else:
                    return True
            else:
                if not ExprPrime():
                    return False
                else:
                    return True
        elif tokens[tokens_current][0] == "this":
            if not Terminals("this"):
                return False
            if not ExprPrime():
                return False
            else:
                return True
        elif tokens[tokens_current][0] == "new":
            if not Terminals("new"):
                return False
            if not ident():
                return False
            if not ExprPrime:
                return False
            else:
                return True
        elif tokens[tokens_current][0] == "NewArray":
            if not Terminals("NewArray"):
                return False
            if not Terminals("("):
                return False
            if not Expr():
                return False
            if not Terminals(","):
                return False
            if not Type():
                return False
            if not Terminals(")"):
                return False
            if not ExprPrime:
                return False
            else:
                return True
        elif tokens[tokens_current][0] == "ReadInteger":
            if not Terminals("ReadInteger"):
                return False
            if not Terminals("("):
                return False
            if not Terminals(")"):
                return False
            if not ExprPrime:
                return False
            else:
                return True
        elif tokens[tokens_current][0] == "ReadLine":
            if not Terminals("ReadLine"):
                return False
            if not Terminals("("):
                return False
            if not Terminals(")"):
                return False
            if not ExprPrime:
                return False
            else:
                return True
        elif tokens[tokens_current][0] == "!":
            if not Terminals("!"):
                return False
            if not Expr():
                return False
            if not ExprPrime:
                return False
            else:
                return True
        elif tokens[tokens_current][0] == "(":
            if not Terminals("("):
                return False
            if not Expr():
                return False
            if not Terminals(")"):
                return False
            if not ExprPrime:
                return False
            else:
                return True
        elif tokens[tokens_current][0] == "-":
            if not Terminals("-"):
                return False
            if not Expr():
                return False
            if not ExprPrime:
                return False
            else:
                return True
        elif tokens[tokens_current][1] == "intConstant" or tokens[tokens_current][1] == "doubleConstant" or tokens[tokens_current][1] == "boolConstant" or tokens[tokens_current][1] == "stringConstant" or tokens[tokens_current][1] == "null":
            print("Found a Cosntant")
            if not Constant():
                return False
            else: 
                return True
        return False
    def Actuals():
        if Expr():
            while tokens[tokens_current] == ",":
                Terminals(",")
                if not Expr():
                    return False
        return True 
    def ExprPrime():
        if tokens[tokens_current][0] == "&&":
            if not Terminals("&&"):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == "||":
            if not Terminals("||"):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == ".":
            if not Terminals("."):
                return False
            if not ident():
                return False
            if tokens[tokens_current][0] == "=":
                if not Terminals("="):
                    return False
                if not Expr():
                    return False
            elif tokens[tokens_current][0] == "(":
                if not Terminals("("):
                    return False
                if not Actuals():
                    return False
                if not Terminals(")"):
                    return False
            return ExprPrime()
        elif tokens[tokens_current][0] == "[":
            if not Terminals("["):
                return False
            if not Expr():
                return False
            if not Terminals("]"):
                return False
            if tokens[tokens_current][0] == "=":
                if not Terminals("="):
                    return False
                if not Expr():
                    return False
            return ExprPrime()
        elif tokens[tokens_current][0] == "+":
            if not Terminals("+"):
                return False
            if not Expr():
                return False  
            return ExprPrime() 
        elif tokens[tokens_current][0] == "-":
            if not Terminals("-"):
                return False
            if not Expr():
                return False
            return ExprPrime()  
        elif tokens[tokens_current][0] == "*":
            if not Terminals("*"):
                return False
            if not Expr():
                return False 
            return ExprPrime()
        elif tokens[tokens_current][0] == "/":
            if not Terminals("/"):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == "%":
            if not Terminals("%"):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == "<":
            if not Terminals("<"):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == "<=":
            if not Terminals("<="):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == ">":
            if not Terminals(">"):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == ">=":
            if not Terminals(">="):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == "==":
            if not Terminals("=="):
                return False
            if not Expr():
                return False
            return ExprPrime()
        elif tokens[tokens_current][0] == "!=":
            if not Terminals("!="):
                return False
            if not Expr():
                return False
            return ExprPrime()
        else:
            return True

    def Var():
        if not Type():
            return False
        if not ident():
            return False
        return True
   
    def Type():
        if Terminals("int"):
            return TypePrime()
        if Terminals("string"):
            return TypePrime()
        if Terminals("bool"):
            return TypePrime()
        if Terminals("double"):
            return TypePrime()
        if ident():
            return TypePrime()
        else:
            return False
    def TypePrime():
        if tokens[tokens_current][0] == "[":
            if not Terminals("["):
                return False
            if not Terminals("]"):
                return False
            return TypePrime()
        else:
            return True

    def Constant():
        global tokens_current
        print("Looking For " + "Constant" + " at " + str(tokens_current))
        if tokens[tokens_current][1] == "intConstant" or tokens[tokens_current][1] == "doubleConstant" or tokens[tokens_current][1] == "boolConstant" or tokens[tokens_current][1] == "stringConstant" or tokens[tokens_current][1] == "null":
            print("Found" + tokens[tokens_current][0] + " at " + str(tokens_current))
            tokens_current = tokens_current + 1
            return True
        else:
            return False
    
    def Terminals(terminal):
        global tokens_current
        print("Looking For " + terminal + " at " + str(tokens_current))
        if tokens[tokens_current][0] == terminal:
            print("Found" + tokens[tokens_current][0] + " at " + str(tokens_current))
            tokens_current = tokens_current + 1
            return True
        else: 
            return False
    def ident():
        global tokens_current
        print("Looking For " + tokens[tokens_current][0] + " at " + str(tokens_current))
        if tokens[tokens_current][0] in symbol_table.keys():
            print("Found" + tokens[tokens_current][0] + " at " + str(tokens_current))
            tokens_current = tokens_current + 1
            return True
        else: 
            return False
    
    
    
    
    #------------------------------------------------------------------------------------------------------------------------------------
    def parser(tokens):
        expr_block_constant = [["Expr'","LValue"],["Expr'","Call"],["Expr'","Actuals"],["Expr'","Expr","=","LValue"],["Expr'","Constant"]]
        expr_block = [["Expr'","LValue"],["Expr'","Call"],["Expr'","Actuals"],["Expr'","Expr","=","LValue"]]
        lval_block = [["ident",".","Expr"],["]","Expr","[","Expr"]]
        call = [")","Actuals","(","ident",".","Expr"]
        parse_table = [["terminals","ident","intConstant","doubleConstant","boolConstant","stringConstant","null","int","double","bool","string","class","void","interface","this","extends","implements","for","while","if","else","return","break","new","NewArray","Print","ReadInteger","ReadLine","true","false",";","&&","||","!",",",".","[","{","(","=","+","-","*","/","%","<",">","<=",">=","==","!=","]","}",")","/epsilon"],
                    ["Program",["Program","DeclMulti","Decl"],None,None,None,None,None,["Program","DeclMulti","Decl"],["Program","DeclMulti","Decl"],["Program","DeclMulti","Decl"],["Program","DeclMulti","Decl"],["Program","DeclMulti","Decl"],["Program","DeclMulti","Decl"],["Program","DeclMulti","Decl"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Decl",[["VariableDecl"],["FunctionDecl"]],None,None,None,None,None,[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],"ClassDecl","FunctionDecl","InterfaceDecl",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["DeclMulti",["DeclMulti","Decl"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["DeclMulti","Decl"],["DeclMulti","Decl"],["DeclMulti","Decl"],["DeclMulti","Decl"],["DeclMulti","Decl"],["DeclMulti","Decl"],["DeclMulti","Decl"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon"],
                    ["VariableDeclMulti",[["VariableDeclMulti","VariableDecl"],["/epsilon"]],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["VariableDeclMulti","VariableDecl"],["VariableDeclMulti","VariableDecl"],["VariableDeclMulti","VariableDecl"],["VariableDeclMulti","VariableDecl"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["VariableMulti",","],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon"],
                    ["VariableDecl",[";","Variable"],None,None,None,None,None,[";","Variable"],[";","Variable"],[";","Variable"],[";","Variable"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Variable",["ident","Type"],None,None,None,None,None,["ident","Type"],["ident","Type"],["ident","Type"],["ident","Type"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["VariableMulti",["VariableMulti","Variable"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["VariableMulti","Variable"],["VariableMulti","Variable"],["VariableMulti","Variable"],["VariableMulti","Variable"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["VariableMulti",","],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon"],
                    ["Type",["Type'","ident"],None,None,None,None,None,["Type'","int"],["Type'","double"],["Type'","bool"],["Type'","string"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Type'","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["Type'","]","["],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon"],
                    ["FunctionDecl",["StmtBlock",")","Formals","(","ident","Type"],None,None,None,None,None,["StmtBlock",")","Formals","(","ident","Type"],["StmtBlock",")","Formals","(","ident","Type"],["StmtBlock",")","Formals","(","ident","Type"],["StmtBlock",")","Formals","(","ident","Type"],None,["StmtBlock",")","Formals","(","ident","void"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Formals",["VariableMulti"],None,None,None,None,None,["VariableMulti"],["VariableMulti"],["VariableMulti"],["VariableMulti"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["ClassDecl",None,None,None,None,None,None,None,None,None,None,["}","FieldMulti","{",",","ident","implements","ident","extends","ident","class"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Field",[["VariableDecl"],["FunctionDecl"]],None,None,None,None,None,[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],[["VariableDecl"],["FunctionDecl"]],None,"FunctionDecl",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["FieldMulti",["FieldMulti","Field"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["FieldMulti","Field"],["FieldMulti","Field"],["FieldMulti","Field"],["FieldMulti","Field"],"/epsilon",["FieldMulti","Field"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon"],
                    ["InterfaceDecl",None,None,None,None,None,None,None,None,None,None,None,None,["}","PrototypeMulti","{","ident","interface"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Prototype",[";",")","Formals","(","ident","Type"],None,None,None,None,None,[";",")","Formals","(","ident","Type"],[";",")","Formals","(","ident","Type"],[";",")","Formals","(","ident","Type"],[";",")","Formals","(","ident","Type"],None,[";",")","Formals","(","ident","void"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["PrototypeMulti",["PrototypeMulti","Prototype"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["PrototypeMulti","Prototype"],["PrototypeMulti","Prototype"],["PrototypeMulti","Prototype"],["PrototypeMulti","Prototype"],"/epsilon",["PrototypeMulti","Prototype"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon""/epsilon","/epsilon","/epsilon"],
                    ["StmtBlock",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,["}","StmtMulti","VariableDeclMulti","{"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Stmt",[";","Expr"],[";","Expr"],[";","Expr"],[";","Expr"],[";","Expr"],None,None,None,None,None,None,None,None,[";","Expr"],None,None,"ForStmt","WhileStmt","IfStmt",None,"ReturnStmt","BreakStmt",[";","Expr"],[";","Expr"],"PrintStmt",[";","Expr"],[";","Expr"],None,None,None,None,None,[";","Expr"],None,None,None,["}","Stmt","VariableDecl","{"],[";","Expr"],None,None,[";","Expr"],None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["StmtMulti",["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["StmtMulti","Stmt"],"/epsilon","/epsilon",["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],"/epsilon",["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],["StmtMulti","Stmt"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["StmtMulti","Stmt"],"/epsilon","/epsilon","/epsilon",["StmtMulti","Stmt"],["StmtMulti","Stmt"],"/epsilon","/epsilon",["StmtMulti","Stmt"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon""/epsilon","/epsilon","/epsilon"],
                    ["IfStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,["Stmt","else","Stmt",")","Expr","(","if"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["WhileStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,["Stmt",")","Expr","(","while"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["ForStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,["Stmt",")","Expr",";","Expr",";","Expr","(","for"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["ReturnStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,[";","Expr","return"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["BreakStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,[";","break"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["PrintStmt",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,[";",")","ExprMulti","(","Print"],None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Expr",[["Expr'","Expr","=","ident"],["ident"],["Expr'",")","Actuals","(","ident"]],["Expr'","Constant"],["Expr'","Constant"],["Expr'","Constant"],["Expr'","Constant"],["Expr'","Constant"]
                    ,None,None,None,None,None,None,None,["Expr'","this"],None,None,None,None,None,None,None,None,["Expr'","ident","new"],["Expr'",")","Type",",","Expr","(","NewArray"],None,["Expr'",")","(","ReadInteger"],["Expr'",")","(","ReadLine"],None,None,None,None,None,["Expr'","Expr","!"],None,None,None,["Expr'",")","Expr","("],None,None,["Expr'","Expr","-"],None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Expr'","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",[["Expr'","Expr","&&"],["/epsilon"]],[["Expr'","Expr","||"],["/epsilon"]],"/epsilon","/epsilon",[["Expr'","Expr","=","ident","."],["Expr'","ident","."],["Expr'",")","Actuals","(","ident","."]],[["Expr'","]","Expr","["],["Expr'","Expr","=","]","Expr","["]],"/epsilon","/epsilon","/epsilon",[["Expr'","Expr","+"],["/epsilon"]],[["Expr'","Expr","-"],["/epsilon"]],[["Expr'","Expr","*"],["/epsilon"]],[["Expr'","Expr","/"],["/epsilon"]],[["Expr'","Expr","%"],["/epsilon"]],[["Expr'","Expr","<"],["/epsilon"]],[["Expr'","Expr",">"],["/epsilon"]],[["Expr'","Expr","<="],["/epsilon"]],[["Expr'","Expr",">="],["/epsilon"]],[["Expr'","Expr","=="],["/epsilon"]],[["Expr'","Expr","!="],["/epsilon"]],"/epsilon","/epsilon","/epsilon","/epsilon"],
                    ["ExprMulti",["ExprMulti","Expr"],["ExprMulti","Expr"],["ExprMulti","Expr"],["ExprMulti","Expr"],["ExprMulti","Expr"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["ExprMulti","Expr"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["ExprMulti","Expr"],["ExprMulti","Expr"],"/epsilon",["ExprMulti","Expr"],["ExprMulti","Expr"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon",["ExprMulti","Expr"],["ExprMulti",","],"/epsilon","/epsilon","/epsilon",["ExprMulti","Expr"],"/epsilon","/epsilon",["ExprMulti","Expr"],"/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon","/epsilon""/epsilon","/epsilon","/epsilon"],
                    ["Actuals","ExprMulti","ExprMulti","ExprMulti","ExprMulti","ExprMulti",None,None,None,None,None,None,None,None,"ExprMulti",None,None,None,None,None,None,None,None,"ExprMulti","ExprMulti",None,"ExprMulti","ExprMulti",None,None,None,None,None,"ExprMulti",None,None,None,None,"ExprMulti",None,None,"ExprMulti",None,None,None,None,None,None,None,None,None,None,None,None,None],
                    ["Constant",None, "intConstant","doubleConstant","boolConstant","stringConstant","null",None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]]     
    output = program()
    if not output:
        error_line = "Line in Question: "
        line = tokens[tokens_current-1][2]
        log_error("SYNTAX ERROR ON LINE " + str(tokens[tokens_current-1][2]))
        if lines[line][-2:] == "\n":
            error_line = error_line + lines[line-1][0:-2]
        else:
            error_line = error_line + lines[line-1]
        log_error(error_line)
    print(output) 
if __name__ == "__main__":
    main()