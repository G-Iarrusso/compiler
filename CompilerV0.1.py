#remove whitespace from reading
def main():
    current_char = 0
    n = 4096
    buffer1 = ["null"]*n
    buffer2 = ["null"]*n
    keywords = []
    operators = []
    c = "s"
    with open("C:\\Users\\Lowfa\\Documents\\test.txt") as f:
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
    with open("C:\\Users\\Lowfa\\Documents\\keywords.txt") as f:
        while True:
            word = f.readline()
            if not word:
                break
            keywords.append(word)
    with open("C:\\Users\\Lowfa\\Documents\\operators.txt") as f:
        while True:
            word = f.readline()
            if not word:
                break
            operators.append(word)

    token = "null"
    thing = ""
    cnt = 0
    while cnt < len(buffer1) and buffer1[cnt]!="eof":
        print(buffer1[cnt])
        cnt = cnt + 1

if __name__ == "__main__":
    main()
    


