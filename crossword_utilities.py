
stopwords = [
    'the',
    'a',
    'of',
    'and',
    'to',
    'in',
    'for',
    'that',
    'on',
    'is',
    'with',
    'at',
    'by',
    'it',
    'as',
    'but',
    'from',
    'be',
    'an',
    'have',
    'was',
    'not',
    'this',
    'are',
    'has',
    'or',
]

def while_replace(string):
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string

def acrossdown(clue): # get rid of local -across or -down clues without losing other clues containing those terms
    for i in xrange (0,10):
        if str(i)+'-down' in clue:
            return True
        if str(i)+'-across' in clue:
            return True
    return False

def cleananswer(answer):
    answer =  answer.replace('-','').replace("'",'').replace('"','')
    answer = while_replace(answer)
    answer = answer.strip().upper()
    for i in answer:
        if not i.isalpha():
            return ''
    return answer

def cleanreverseanswer(answer):
    answer = answer.replace('&#34;','"').replace('__','_').replace('  ',' ').replace('--','-')
    answer = answer.replace('.',' ').replace(',',' ').replace('?',' ').replace('!',' ').replace(':',' ').replace(';',' ')
    answer = answer.replace('_','-').replace('"',"")
    answer = answer.replace('-','').replace("'",'').replace('"','')
    answer = while_replace(answer)
    answer = answer.strip().upper()
    for i in answer:
        if not i.isalpha():
            return ''
    return answer

def stripacrossdown(clue):
    cluesplit = clue.split()
    newclue = ' '
    for word in cluesplit:
        if '-across' not in word.lower() and '-down' not in word.lower():
            newclue = newclue + word + ' '
    return newclue.strip()

def cleanclue(clue):
    raw = clue.lower().strip()
    if len(clue) == 1:
        return clue.lower()
    clue = stripacrossdown(clue)
    clue = ' ' + clue + ' '
    clue = clue.replace('*','')
    clue = clue.replace('&#34;','"').replace('__','_').replace('--','-')
    clue = clue.replace('.','').replace(',',' ').replace('?','').replace('&amp;',' and')
    clue = clue.replace('!','').replace(':',' ').replace(';',' ')
    clue = clue.replace('(',' ').replace(')',' ').replace('[',' ').replace(']',' ')
    clue = clue.replace('_','-').replace('"',"")
    clue = clue.replace("-"," ")
    clue = clue.replace("' "," ").replace(" '"," ")
    clue = clue.replace("' "," ").replace(" '"," ")
    clue = while_replace(clue)
    clue = clue.lower().strip()
    if len(clue) == 0:
        return raw
    return clue
