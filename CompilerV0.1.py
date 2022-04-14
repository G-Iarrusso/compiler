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
from anytree import Node, RenderTree, AsciiStyle, PreOrderIter, findall

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
    global flag
    flag = 0
    output.write(str(line)+"\n")
    

def lexer():
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
    c = "s"
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
    print("We done")
    return symbol_table, read_order, line_num, lines

def parser(symbol_table, read_order, line_num, lines):
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
        root = Node("Program")
        if not decl(root):
            return False
        while decl(root):
            print("Start of Program")
        if tokens[tokens_current][0] == "$":
            return root
        else:
            return False
    def decl(parentprime):
        root = Node("Decl")
        if VariableDeclAux2(root) == 1:
            root.parent = parentprime
            return True
        if FunctionDecl(root):
            root.parent = parentprime
            return True
        if tokens[tokens_current][0] == "class":
            if ClassDecl(root):
                root.parent = parentprime
                return True
        if tokens[tokens_current][0] == "interface":
            if InterfaceDecl(root):
                root.parent = parentprime
                return True
        return False
    def InterfaceDecl(parentprime):
        root = Node("InterfaceDecl")
        if not Terminals("interface",root):
            return False
        if not ident(root):
            return False
        if not Terminals("{",root):
            return False
        while True:
            troupleProto = Prototype(root)
            if troupleProto == 0:
                break
            elif troupleProto == -1:
                return False
        if not Terminals("}",root):
            return False
        else:
            root.parent = parentprime
            return True
    def Prototype(parentprime):
        root = Node("Prototype")
        if tokens[tokens_current][0]!="}":
            if not Terminals("void",root) and not Type(root):
                return -1
            if not ident(root):
                return -1
            if not Terminals("(",root):
                return -1
            if not Formals(root):
                return -1
            if not Terminals(")",root):
                return -1
            if not Terminals(";",root):
                return -1
            else:
                root.parent = parentprime
                return 1
        else:
            return 0
    def ClassDecl(parentprime):
        root = Node("ClassDecl")
        if not Terminals("class",root):
            return False
        if not ident(root):
            return False
        if tokens[tokens_current][0] == "extends":
            if not Terminals("extends",root):
                return False
            if not ident(root):
                return False
        if tokens[tokens_current][0] == "implements":
            if not Terminals("implements",root):
                return False
            if not ident(root):
                return False
            while tokens[tokens_current][0] == ",":
                if not Terminals(",",root):
                    return False
                if not ident(root):
                    return False
        if not Terminals("{",root):
            return False
        while True:
            troupleField = Field(root)
            if troupleField == 0:
                break
            elif troupleField == -1:
                return False
        if not Terminals("}",root):
            return False
        else:
            root.parent = parentprime
            return True
    def Field(parentprime):
        root = Node("Field")
        if tokens[tokens_current][0] == "int" or tokens[tokens_current][0] == "string" or tokens[tokens_current][0] == "double" or tokens[tokens_current][0] == "bool" or tokens[tokens_current][0] in symbol_table.keys():
            state = VariableDeclAux2(root)
            if state == -1:
                return -1
            if state == 1:
                root.parent = parentprime
                return 1
        #If this messes with things make it an if
        if tokens[tokens_current][0] == "int" or tokens[tokens_current][0] == "string" or tokens[tokens_current][0] == "double" or tokens[tokens_current][0] == "bool" or tokens[tokens_current][0] == "void" or tokens[tokens_current][0] in symbol_table.keys():    
            if FunctionDecl(root):
                root.parent = parentprime
                return 1
            else:
                return -1
        else:
            return 0
    def VariableDeclAux2(parentprime,is_ident = False):
        global tokens_current
        root = Node("VariableDecl")
        if not Var(root):
            return -1
        if not Terminals(";",root):
            tokens_current = tokens_current - 2
            return 0
        root.parent = parentprime
        return 1
    def VariableDecl(parentprime):
        root = Node("VariableDecl")
        if not Var(root):
            return False
        if not Terminals(";",root):
            return False
        root.parent = parentprime
        return True
    def FunctionDecl(parentprime):
        root = Node("FunctionDecl")
        if not Terminals("void",root) and not Type(root):
            return False
        
        if not ident(root):
            return False

        if not Terminals("(",root):
            return False

        if not Formals(root):
            return False

        if not Terminals(")",root):
            return False

        if not StmtBlock(root):
            return False

        else:
            root.parent = parentprime
            return True
    def Formals(parentprime):
        root = Node("Formals")
        if Var(root):
            root.parent = parentprime
            while tokens[tokens_current][0] == ",":
                Terminals(",",root)
                if not Var(root):
                    return False 
        return True 
    def VariableDeclAux(parentprime,is_ident = False):
        global tokens_current
        root = Node("VariableDecl")
        if not Var(root):
            if is_ident:
                tokens_current = tokens_current - 1
            return 0
        if not Terminals(";",root):
            return -1
        root.parent = parentprime
        return 1

    def StmtBlock(parentprime):
        root = Node("StmtBlock")
        if not Terminals("{",root):
            return False
        while True:
            if tokens[tokens_current][0] in symbol_table.keys():
                troupleVar = VariableDeclAux(root,is_ident = True)
            else:
                troupleVar = VariableDeclAux(root)
            if troupleVar == -1:
                return False
            elif troupleVar == 0:
                break
        while True:
            trouple = Stmt(root)
            if trouple == 0:
                break
            elif trouple == -1:
                return False
        if not Terminals("}",root):
            return False
        else: 
            root.parent = parentprime
            return True 
    def Stmt(parentprime):
        root = Node("Stmt")
        print("Found a statement")
        if tokens[tokens_current][0] in symbol_table.keys() or "Constant" in tokens[tokens_current][1] or tokens[tokens_current][0] == "this" or tokens[tokens_current][0] == "new" or tokens[tokens_current][0] == "NewArray" or tokens[tokens_current][0] == "ReadInteger" or tokens[tokens_current][0] == "ReadLine" or tokens[tokens_current][0] == "!" or tokens[tokens_current][0] == "(" or tokens[tokens_current][0] == "-":
            if not Expr(root):
                return -1
            if not Terminals(";",root):
                return -1
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "{":
            if StmtBlock(root):
                root.parent = parentprime
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "while":
            if WhileStmt(root):
                root.parent = parentprime
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "for":
            if ForStmt(root):
                root.parent = parentprime
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "return":
            if ReturnStmt(root):
                root.parent = parentprime
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "if":
            if IfStmt(root):
                root.parent = parentprime
                return True
            else:
                return -1
        elif tokens[tokens_current][0] == "Print":
            if PrintStmt(root):
                root.parent = parentprime
                return True
            else:
                -1
        elif tokens[tokens_current][0] == "break":
            if BreakStmt(root):
                root.parent = parentprime
                return True
            else:
                return -1
        else:
            return 0  
    def WhileStmt(parentprime):
        root = Node("WhileStmt")
        if not Terminals("while",root):
            return False
        if not Terminals("(",root):
            return False
        if not Expr(root):
            return False
        if not Terminals(")",root):
            return False
        if not Stmt(root):
            return False
        else:
            root.parent = parentprime
            return True
    #Needs to be re-tooled
    def ForStmt(parentprime):
        root = Node("ForStmt")
        if not Terminals("for",root):
            return False
        if not Terminals("(",root):
            return False
        Expr(root)
        if Terminals(";",root):
            if not Expr(root):
                return False
            if Terminals(";",root):
                if not Expr(root):
                    return False
        if not Terminals(")",root):
            return False
        if not Stmt(root):
            return False
        else:
            root.parent = parentprime
            return True
    def ReturnStmt(parentprime):
        root = Node("ReturnStmt")
        if not Terminals("return",root):
            return False
        Expr(root)
        if not Terminals(";",root):
            return False
        else:
            root.parent = parentprime
            return True
    def IfStmt(parentprime):
        root = Node("IfStmt")
        if not Terminals("if",root):
            return False
        if not Terminals("(",root):
            return False
        if not Expr(root):
            return False
        if not Terminals(")",root):
            return False
        if not Stmt(root):
            return False
        if Terminals("else",root):
            if not Stmt(root):
                return False
        else:
            root.parent = parentprime
            return True
    def PrintStmt(parentprime):
        root = Node("PrimtStmt")
        if not Terminals("Print",root):
            return False
        if not Terminals("(",root):
            return False
        if not Expr(root):
            return False
        while tokens[tokens_current][0] == ",":
            Terminals(",",root)
            if not Expr(root):
                return False
        if not Terminals(")",root):
            return False
        if not Terminals(";",root):
            return False
        else:
            root.parent = parentprime
            return True
    def BreakStmt(parentprime):
        root = Node("BreakStmt")
        if not Terminals("break",root):
            return False
        if not Terminals(";",root):
            return False
        else:
            root.parent = parentprime
            return True  
    
    def Expr(parentprime):
        root = Node("Expr")
        if tokens[tokens_current][0] in symbol_table.keys() and ("Constant" not in tokens[tokens_current][1]):
            if not ident(root):
                return False
            if tokens[tokens_current][0] == "=":
                if not Terminals("=",root):
                    return False
                if not Expr(root):
                    return False
                if not ExprPrime(root):
                    return False
                else:
                    root.parent = parentprime
                    return True
            elif tokens[tokens_current][0] == "(":
                if not Terminals("(",root):
                    return False
                if not Actuals(root):
                    return False
                if not Terminals(")",root):
                    return False
                if not ExprPrime(root):
                    return False
                else:
                    root.parent = parentprime
                    return True
            else:
                if not ExprPrime(root):
                    return False
                else:
                    root.parent = parentprime
                    return True
        elif tokens[tokens_current][0] == "this":
            if not Terminals("this",root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "new":
            if not Terminals("new",root):
                return False
            if not ident(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "NewArray":
            if not Terminals("NewArray",root):
                return False
            if not Terminals("(",root):
                return False
            if not Expr(root):
                return False
            if not Terminals(",",root):
                return False
            if not Type(root):
                return False
            if not Terminals(")",root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "ReadInteger":
            if not Terminals("ReadInteger",root):
                return False
            if not Terminals("(",root):
                return False
            if not Terminals(")",root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "ReadLine":
            if not Terminals("ReadLine",root):
                return False
            if not Terminals("(",root):
                return False
            if not Terminals(")",root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "!":
            if not Terminals("!",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "(":
            if not Terminals("(",root):
                return False
            if not Expr(root):
                return False
            if not Terminals(")",root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "-":
            if not Terminals("-",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][1] == "intConstant" or tokens[tokens_current][1] == "doubleConstant" or tokens[tokens_current][1] == "boolConstant" or tokens[tokens_current][1] == "stringConstant" or tokens[tokens_current][1] == "null":
            print("Found a Cosntant")
            if not Constant(root):
                return False
            else: 
                root.parent = parentprime
                return True
        return False
    def Actuals(parentprime):
        root = Node("Actuals")
        if Expr(root):
            while tokens[tokens_current][0] == ",":
                if not Terminals(",",root):
                    return False
                if not Expr(root):
                    return False
            root.parent = parentprime
        return True 
    def ExprPrime(parentprime):
        root = Node("ExprPrime")
        if tokens[tokens_current][0] == "&&":
            if not Terminals("&&",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "||":
            if not Terminals("||",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == ".":
            if not Terminals(".",root):
                return False
            if not ident(root):
                return False
            if tokens[tokens_current][0] == "=":
                if not Terminals("=",root):
                    return False
                if not Expr(root):
                    return False
            elif tokens[tokens_current][0] == "(":
                if not Terminals("(",root):
                    return False
                if not Actuals(root):
                    return False
                if not Terminals(")",root):
                    return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "[":
            if not Terminals("[",root):
                return False
            if not Expr(root):
                return False
            if not Terminals("]",root):
                return False
            if tokens[tokens_current][0] == "=":
                if not Terminals("=",root):
                    return False
                if not Expr(root):
                    return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "+":
            if not Terminals("+",root):
                return False
            if not Expr(root):
                return False  
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "-":
            if not Terminals("-",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True  
        elif tokens[tokens_current][0] == "*":
            if not Terminals("*",root):
                return False
            if not Expr(root):
                return False 
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "/":
            if not Terminals("/",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "%":
            if not Terminals("%",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "<":
            if not Terminals("<",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "<=":
            if not Terminals("<=",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == ">":
            if not Terminals(">",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == ">=":
            if not Terminals(">=",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "==":
            if not Terminals("==",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        elif tokens[tokens_current][0] == "!=":
            if not Terminals("!=",root):
                return False
            if not Expr(root):
                return False
            if not ExprPrime(root):
                return False
            else:
                root.parent = parentprime
                return True
        else:
            return True

    def Var(parentprime):
        root = Node("Variable")
        if not Type(root):
            return False
        if not ident(root):
            return False
        root.children[1].children[0].typing = root.children[0].children[0].name
        root.parent = parentprime
        return True
   
    def Type(parentprime):
        root = Node("Type")
        if Terminals("int",root):
            if TypePrime(root):
                root.parent = parentprime
                return True
            else:
                return False
        if Terminals("string",root):
            if TypePrime(root):
                root.parent = parentprime
                return True
            else:
                return False
        if Terminals("bool",root):
            if TypePrime(root):
                root.parent = parentprime
                return True
            else:
                return False
        if Terminals("double",root):
            if TypePrime(root):
                root.parent = parentprime
                return True
            else:
                return False
        if ident(root):
            if TypePrime(root):
                root.parent = parentprime
                return True
            else:
                return False
        else:
            return False
    def TypePrime(parentprime):
        root = Node("TypePrime")
        if tokens[tokens_current][0] == "[":
            if not Terminals("[",root):
                return False
            if not Terminals("]",root):
                return False
            if TypePrime(root):
                root.parent = parentprime
                return True
            else:
                return False
        else:
            return True

    def Constant(parentprime):
        global tokens_current
        root = Node("Constant")
        print("Looking For " + "Constant" + " at " + str(tokens_current))
        if tokens[tokens_current][1] == "intConstant" or tokens[tokens_current][1] == "doubleConstant" or tokens[tokens_current][1] == "boolConstant" or tokens[tokens_current][1] == "stringConstant" or tokens[tokens_current][1] == "null":
            print("Found" + tokens[tokens_current][0] + " at " + str(tokens_current))
            temp = Node(tokens[tokens_current][1],root)
            temp2 = Node(tokens[tokens_current][0],temp, line_num=tokens[tokens_current][2])
            root.parent = parentprime
            tokens_current = tokens_current + 1
            print("Now Looking for " + tokens[tokens_current][0] + " at " + str(tokens_current))
            return True
        else:
            return False
    
    def Terminals(terminal,parentprime):
        global tokens_current
        print("Looking For " + terminal + " at " + str(tokens_current))
        if tokens[tokens_current][0] == terminal:
            print("Found" + tokens[tokens_current][0] + " at " + str(tokens_current))
            tokens_current = tokens_current + 1
            temp = Node(terminal,parentprime, line_num=tokens[tokens_current][2])
            print("Now Looking for " + tokens[tokens_current][0] + " at " + str(tokens_current))
            return True
        else: 
            print("Did not find " + terminal + " Found:" + tokens[tokens_current][0])
            return False
    def ident(parentprime):
        global tokens_current
        root = Node("ident", None)
        print("Looking For " + tokens[tokens_current][0] + " at " + str(tokens_current))
        if tokens[tokens_current][0] in symbol_table.keys():
            print("Found" + tokens[tokens_current][0] + " at " + str(tokens_current))
            temp = Node(tokens[tokens_current][0],root, line_num=tokens[tokens_current][2], typing = None)
            root.parent = parentprime
            tokens_current = tokens_current + 1
            print("Now Looking for " + tokens[tokens_current][0] + " at " + str(tokens_current))
            return True
        else: 
            return False
    
    while (tokens[tokens_current][0] != "$" and len(tokens)>tokens_current):
        previous = tokens[tokens_current]
        output = program()
        print(read_order)
        if output:
            for pre, fill, node in RenderTree(output,style = AsciiStyle()):
                print("%s%s" % (pre, node.name))
            break
        if tokens[tokens_current] == previous:
            tokens_current = tokens_current +1
        error_line = "Line in Question: "
        if tokens_current > 0:
            line = tokens[tokens_current-1][2]
        else:
            line = tokens[0][2]
        log_error("SYNTAX ERROR ON LINE " + str(line))
        if line < len(lines):
            if lines[line][-2:] == "\n":
                error_line = error_line + lines[line-1][0:-2]
            else:
                error_line = error_line + lines[line-1]
        else:
            error_line = error_line + lines[line-1]
        log_error(error_line)
        for item in tokens[tokens_current:]:
            if item[2] ==line:
                tokens_current = tokens_current +1
                print(tokens_current)
            else:
                break
            if tokens_current >= len(tokens):
                tokens_current = len(tokens) -1
                break
        print(tokens[tokens_current:])
    return output

def semantic(ast,symbol_table):
    known_idents = []
    alg_operators = parse("algebraic_ops.txt")
    log_operators = parse("logical_ops.txt")
    class ident:
        def __init__(self,name,type,context):
            self.name = name
            self.type = type
            self.context = context
    def handle_expr(expr_tree):
        print("Literal")
        prev_type = None
        prev_return_type= None
        for node in PreOrderIter(expr_tree):
            if node.children != None and node != expr_tree:
                print(node)
                type, return_type = handle_expr_aux(node, prev_type, prev_return_type)
                if type == -1:
                    log_error("Semantic Error")
                    log_error("Bad Type")
                    return False
                if return_type == -1:
                    log_error("Semantic Error")
                    log_error("Bad Return")
                    return False
                if prev_type == None and type != None:
                    prev_type = type
                if prev_return_type == None and return_type != None:
                    prev_return_type = return_type
        return True

    def handle_expr_aux(node, prev_type, prev_return_type):
        print("New itteration")
        type = None
        return_type = None
        print("Went Else")
        if node.name in symbol_table.keys():
            for idents in known_idents:
                if node.name == idents.name:
                    print("ident type")
                    type = idents.type
        elif "Constant" in node.parent.name and len(node.parent.name) > 8:
            print("constants type")
            print(node.name)
            type = ""
            for letter in node.parent.name[0:-8]:
                type = type + letter
            print("Type")
            print(type)
        elif node.name in log_operators:
            return_type = "Bool"
        elif node.name in alg_operators:
            return_type = "Alg"
        if prev_type == None and type != None:
            return type, None
        if prev_return_type == None and return_type != None:
            return None, return_type
        if type!=None:
            print("Type compare")
            print(type)
            print(prev_type)
            if type == prev_type:
                return type, None
            else:
                return -1, None
        if return_type != None:
            if prev_return_type == "Bool":
                return None, "Bool"
            if prev_return_type == return_type:
                return None, return_type
            if prev_return_type == "Alg" and return_type == "Bool":
                return None, return_type
        return type, return_type

    def type_checking():
        for node in PreOrderIter(ast):
            if node.name == "Variable":
                new_ident = ident(node.children[1].children[0].name,node.children[0].children[0].name, "Var")
                known_idents.append(new_ident)

            if node.name == "FunctionDecl":
                if node.children[0].name == "Type":
                    new_ident = ident(node.children[1].children[0].name, node.children[0].children[0].children[0].name, "Func")
                else:
                    new_ident = ident(node.children[1].children[0].name,node.children[0].name, "Func")
                known_idents.append(new_ident)

            if node.name == "ClassDecl":
                new_ident = ident(node.children[1].children[0].name,node.children[0].name, "Class")
                known_idents.append(new_ident)
            
            if node.name == "Expr":
                out_come = handle_expr(node)
                print(out_come)
        print("Done Type Checking")
            
    type_checking()
    print([node.name for node in PreOrderIter(ast)])
    scope = 0
    scope_stack = [] 
    symbol_table = []
    in_class = False
    in_function = False
    in_interface = False
    for node in PreOrderIter(ast):
        #Find a new function(Still need interface and Prototypes)
        if node.name == "FunctionDecl" and scope == 0:
            if in_function == True:
                return False
            in_function = True
            scope = node.children[1].children[0].name
            if node.children[0].name == "Type":
                type = node.children[0].children[0].name
            else:
                type = "void"
            args = 0
            if node.children[3].name == "Formals":
                arg = findall(node.children[3], filter_=lambda node: node.name in ("Variable"))
                args = len(arg)
                type_arg = []
                for item in arg:
                    type_arg.append(item.children[0].children[0].name)
                print(type_arg)
                symbol_table.append([node.children[1].children[0].name,0,type,"Function",args,type_arg])
            else:
                args = 0
                symbol_table.append([node.children[1].children[0].name,0,type,"Function",args])
            scope_stack.append([scope,0])
        #Find a new class
        elif node.name == "ClassDecl" and scope == 0:
            in_class = True
            scope = node.children[1].children[0].name
            symbol_table.append([node.children[1].children[0].name,0,"Class"])
            scope_stack.append([scope,0])
        
        elif node.name == "InterfaceDecl" and scope == 0:
            print("Found interface")
            in_interface = True
            scope = node.children[1].children[0].name
            symbol_table.append([node.children[1].children[0].name,0,"Interface"])
            scope_stack.append([scope,0])

        #Gets us out of the class scope
        if node.name == "Decl":
            print("New Declaration")
            scope_stack = [s for s in scope_stack if s[1] == 0]
            scope = 0
            in_class = False
            in_function = False
            in_interface = False

        #Rules for scope
        #Variable Duplicates
        if node.name == "Variable":
            dupee = False
            symbol = node.children[1].children[0].name
            for entry in scope_stack:
                if entry[0] == symbol and (entry[1] == scope or entry[1]==0):
                    log_error("SEMANTIC ERROR ON LINE "+str(node.children[1].children[0].line_num))
                    log_error("Duplicate Declaration: " + symbol) 
                    dupee = True   
            if dupee != True:    
                if len(node.children[0].children)>1:
                    symbol_table.append([symbol,scope,node.children[0].children[0].name + "[]","Variable"])
                else:
                    symbol_table.append([symbol,scope,node.children[0].children[0].name,"Variable"])
                scope_stack.append([symbol,scope])
        #Function/Class Duplicates & adding novel functions to the scope if in class
        if (in_class == True or scope == 0 or in_interface == True) and (node.name == "FunctionDecl" or node.name == "Prototype"):
            print("class function")
            dupee = False
            symbol = node.children[1].children[0].name
            for entry in scope_stack:
                if entry[0] == symbol:
                    log_error("SEMANTIC ERROR ON LINE "+str(node.children[1].children[0].line_num))
                    log_error("Duplicate Declaration: " + symbol) 
                    dupee = True
            if in_class == True or in_interface == True:
                if node.children[0].name == "Type":
                    type = node.children[0].children[0].name
                else:
                    type = "void"
                symbol_table.append([node.children[1].children[0].name,scope,type,"Function"])
                scope_stack.append([symbol,scope])
        #NewArray Checking
        if node.name == "NewArray":
            possible_array = node.parent.parent.children[0].children[0].name
            found = False
            for entry in symbol_table:
                if entry[0] == possible_array and ("[]" in entry[2]):
                    print("Found an array")
                    arr = entry
                    found = True 
            if found:
                arr_type = node.parent.children[4].children[0].name
                
                if not(arr_type in arr[2]):
                    log_error("SEMANTIC ERROR ON LINE "+str(node.line_num))
                    log_error("Incorrect Array Type: " + "NewArray") 
                amount = node.parent.children[2].children[0].children[0]
                if amount.name != "intConstant":
                    log_error("SEMANTIC ERROR ON LINE "+str(node.line_num))
                    log_error("Incorrect length: " + "NewArray") 
                if int(amount.children[0].name) <=0:
                    log_error("SEMANTIC ERROR ON LINE "+str(node.line_num))
                    log_error("Arrays cannot be 0: " + "NewArray") 
        #Undeclared Identifiers
        if node.name == "ident":
            found = False
            symbol2 = node.children[0].name
            for entry in scope_stack:
                if entry[0] == symbol2 and (entry[1] == scope or entry[1] == 0): 
                    found = True 
            if found != True:
                log_error("SEMANTIC ERROR ON LINE "+str(node.children[0].line_num))
                log_error("Undeclared Identifier: " + symbol2)
        #Funciton Checking
        if node.name == "ident":
            search = node.children[0].name
            is_function = False
            #if we find the function get the number of arguments
            for item in symbol_table:
                if item[0] == search and item[3] == "Function":
                    is_function = True
                    args = item[4]
                    function = item
            #get the number of arguments in the call
            if is_function and node.parent.children[2].name == "Actuals":
                arg = findall(node.parent.children[2], filter_=lambda node: node.name in ("ident","Constant"))
                if args != len(arg):
                    log_error("SEMANTIC ERROR ON LINE "+str(node.children[0].line_num))
                    log_error("Incorret number of Arguments: " + search)
                if args>0:
                    comparators = []
                    for item in arg:
                        to_compare = item.children[0].name
                        if "Constant" in to_compare:
                            comparators.append(to_compare[0:-8])
                        for item in symbol_table:
                            if item[0] == to_compare and item[1] == scope:
                                comparators.append(item[2])
                    if comparators != function[5]:
                        log_error("SEMANTIC ERROR ON LINE "+str(node.children[0].line_num))
                        log_error("Incorret type of Arguments: " + search)
    has_main = False
    for item in symbol_table:
        if item[0] == "main":
            has_main = True
    if has_main == False:
        log_error("SEMANTIC ERROR ON LINE "+str(0))
        print("Error No Main Function")
    print(symbol_table)
    return symbol_table
global var_num
var_num = 0
def search_table(ident,table):
    for item in table:
        if item[0] == ident:
            return item
    return -1
def cgen(expr,symbol_table,temp_vars):
    if "=" in expr:
        print(expr[0] + expr[1] + cgen(expr[2:],symbol_table,temp_vars))
    if expr[0] == ";":
        return
    if len(expr) == 1 and (search_table(expr[0],symbol_table) or expr[0].isdigit()):
        temp_vars.append(expr[0])
        print("_t"+str(len(temp_vars)-1)+" = " + expr[0])
        return ("_t"+str(len(temp_vars)-1))

def intermediate_representation(symbol_table,ast):
    for item in PreOrderIter(ast):
        if item.name == "FunctionDecl":
            print(item.children[1].children[0].name)
        if item.name == "Stmt":
            protoexpression = findall(item, filter_=lambda node: len(node.children) <= 0)
            expression = []
            for item in protoexpression:
                expression.append(item.name)
            print(expression)
            cgen(expression,symbol_table,[])

        
        


if __name__ == "__main__":
    flag = 1
    symbol_table, read_order, line_num, lines = lexer()
    if flag:
        ast = parser(symbol_table, read_order, line_num, lines)
        if flag:
            symbol_table = semantic(ast, symbol_table)
            if flag:
                #intermediate_representation(symbol_table,ast)
                print()
                if flag:
                    log_error("No Errors, Compiled Correctly")
                else:
                    log_error("Failed On Intermediate Code Representation Step")
                    log_error("Will Not Complete Compile")
            else:
                log_error("Failed On Semantic Analyzer Step")
                log_error("Will Not Advance To Intermediate Code Representation Step")
        else:
            log_error("Failed On Syntax Analyzer Step")
            log_error("Will Not Advance To Semantic Analyzer Step")

    else:
        log_error("Failed On Lexical Analyzer Step")
        log_error("Will Not Advance To Syntax Analyzer Step")