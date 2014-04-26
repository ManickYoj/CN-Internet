import utilities

morseDict = { "A":".-","B":"-...","C":"-.-.","D":"-..","E":".","F":"..-.",
    "G":"--.","H":"....","I":"..","J":".---","K":"-.-","L":".-..",
    "M":"--","N":"-.","O":"---","P":".--.","Q":"--.-","R":".-.",
    "S":"...","T":"-","U":"..-","V":"...-","W":".--","X":"-..-",
    "Y":"-.--","Z":"--..","1":".----","2":"..---","3":"...--",
    "4":"....-","5":".....","6":"-....","7":"--...","8":"---..",
    "9":"----.","0":"-----",".":".-.-.-",",":"--..--","?":"..--..",
    "'":".----.","!":"-.-.--","/":"-..-.","(":"-.--.",")":"-.--.-",
    "&":".-...",":":"---...",";":"-.-.-.","=":"-...-","+":".-.-.",
    "-":"-....-","_":"..--.-","\"":".-..-.","$":"...-..-","@":".--.-."}

charDict = {v:k for(k,v) in morseDict.items()}

transDict = {"-":"111",".":"1","c":"00","s":"0","w":"0000"}

transMorseDict = {v:k for(k,v) in transDict.items()}

def trans2Mess(trans_string):
    """
    Translates transmission code into a human readable message.
    Arguments: trans_string - transmission code (1s and 0s) to translate as string.
                              Assumes that the transmission code is already compressed
                              1:1.
    Returns: message as a string
    """

    #Change strings to a list for the next step
    if isinstance(trans_string, str):
        trans_array = [i for i in trans_string];
    else:
        trans_array = trans_string;

    #Trims off leading and trailing zeros
    trans_array = utilities.trimZeros(trans_array);

    #Translates the message
    return transMess2Word(''.join(trans_array));


def transMess2Word(data):
    
    returnString = "";
    lengthOfSpace = transDict["c"]+transDict["s"]+transDict["w"];
    index = data.find(lengthOfSpace);
    
    while not(index == -1):
        returnString+= transWord2Word(data[:index]) + " ";
        data = data[index+len(lengthOfSpace):];
        index = data.find(lengthOfSpace);

    returnString+= transWord2Word(data);
            
    return returnString;


def transWord2Word(data):
    returnString = "";
    lengthOfSpace =transDict["c"]+transDict["s"];
    index = data.find(lengthOfSpace);
    
    while not(index == -1):
        returnString+= transChar2Char(data[:index]);
        data = data[index+len(lengthOfSpace):];
        index = data.find(lengthOfSpace);

    returnString+= transChar2Char(data);
            
    return returnString;


def transChar2Char(data):
    morseString = "";
    lengthOfSpace = transDict["s"];
    index = data.find(lengthOfSpace);
    
    while not(index == -1):
        morseString+= trans2Morse(data[:index]);
        data = data[index+len(lengthOfSpace):];
        index = data.find(lengthOfSpace);

    morseString+= trans2Morse(data);

    if charDict.get(morseString) is not None:
        return charDict.get(morseString);
    else:
        return '?';

def trans2Morse(trans):
    if trans=='0':
        return '';
    elif transMorseDict.get(trans) is not None:
        return transMorseDict.get(trans);
    else:
        return '?';




def mess2Trans(message):
    message = message.upper()
    return ''.join([char2Trans(char) for char in message])

def char2Trans(char):
    if char == " ":
        return ''.join(transDict["w"])

    if morseDict.get(char) is not None:
        return ''.join(morse2Trans(morseDict[char]))
    else:
        return '';

def morse2Trans(morse):
    return ''.join([symbol2Trans(symbol) for symbol in morse]) + ''.join(transDict["c"])

def symbol2Trans(symbol):
    if transDict.get(symbol) is not None:
        return ''.join(transDict[symbol])+"".join(transDict["s"])
    else:
        return '';
