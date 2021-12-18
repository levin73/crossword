import argparse
import copy
import json
from collections import Counter,defaultdict
from crossword_utilities import cleanclue,stopwords,cleananswer

def exact_matches(grams,solution,current_dict, weight):
    answer = current_dict.get(solution,None)
    if answer:
        answers = grams.get(solution,{solution:{}})
        for a in answer:
            answers[solution][a] = answers[solution].get(a,0) + answer[a] * weight
        grams[solution] = answers
    return grams


def gram_matches(grams,solution,current_dict):
    keys = [x for x in current_dict.keys() if ' ' + solution + ' ' in ' ' + x + ' ' and x != solution]
    for key in keys:
        try:
            answers = grams[solution]
            answers[key] = current_dict[key]
            grams[solution] = answers
        except:
            grams[solution] = {key: current_dict[key]}
    return grams


def subgram_matches(grams,solution,current_dict):
    keys = [x for x in current_dict.keys() if ' ' + x + ' ' in ' ' + solution + ' ' and ' ' in x and x != solution]
    for key in keys:
        words = key.split(' ')
        n = len(words)
        try:
            answers = grams[key]
            answers[key] = current_dict[key]
            for k in answers[key]:
                answers[key][k] = n * answers[key][k]
            grams[key] = answers
        except:
            copy_dict = {}
            for k in current_dict[key]:
                copy_dict[k] = n * current_dict[key][k]
            grams[key] = {key: copy_dict}
    return grams



def word_matches(grams,word,current_dict,weight):
    keys = [x for x in current_dict.keys() if ' ' + word + ' ' in ' ' + x + ' ' and word not in stopwords]
    for key in keys:
        answer = current_dict[key]
        answers = grams.get(word,{})
        if key not in answers:
            answers.update({key:{}})
        for a in answer:
            answers[key].update({a : answers[key].get(a,0) + answer[a] * weight})
        grams[word]= answers
    return grams



def solve(solution, answer_dict,reverse_dict,reversewords_dict):


    #with open('answers.txt','r') as f:  # open in readonly mode
    #    content = f.readlines()
    #    for line in content:
    #        items = line.split(' | ')
    #        if items[0].strip() == str(answerlength):
    #            key = items[1].strip()
    #            answer_dict[key] = items[2].strip()


    # solution order:
    # 1) exact match
    # 2) logged solutions containing entire clue ngram
    # 3) logged soltuions entirely within clue ngram
    grams = {}
    cluewords = list(set(solution.split(' ')))
    results = exact_matches(grams,solution, answer_dict,1.) # TYPE 1
    if not results:
        print 'No exact matches'
    #else:
    #    print results
    grams = results
    reverse_results = exact_matches(grams,solution, reverse_dict,0.5) # TYPE 2
    if not reverse_results:
        print 'No reverse matches'
    #else:
    #    print reverse_results
    grams = reverse_results
    newgrams = gram_matches(grams,solution,answer_dict) # TYPE 3
    if newgrams == {}:
        print 'No logged clues containing entire clue'
    #else:
    #    print grams
    grams = copy.deepcopy(newgrams)
    subgrams = subgram_matches(newgrams,solution,answer_dict) # TYPE 4
    if subgrams == grams:
        print 'No logged ngram clues within clue'
    #else:
    #    print subgrams
    grams = subgrams
    if len(cluewords) > 1: #
        for word in cluewords: # TYPE 5 (skip for one-word clues as is same as TYPE 3)
            grams = word_matches(grams,word,answer_dict,1.)
            grams = word_matches(grams,word,reverse_dict,0.5)
            grams = word_matches(grams,word,reversewords_dict,0.25)
    dictwords = {}
    wordvalue = {}
    for gram in grams:
        wordvalue[gram] = 0
        listword = []
        for key in grams[gram]:
            word_dict = grams[gram][key]
            for word in word_dict:
                if word.lower() not in cluewords:
                    listword.append((word,word_dict[word]))

        d = defaultdict(int)
        for key, value in listword:
            d[key] += value
            wordvalue[gram] += value
        dictwords[gram] = d

    d = {}
    for gram in dictwords:
        a = dictwords[gram]
        b = 1. * wordvalue[gram]
        for key,val in a.items():
            try:
                d.update({key: a[key]/b + d[key]})
            except:
                d.update({key: a[key]/b})
    out = sorted(d.items(), key=lambda x: x[1], reverse=True)[:29]
    print out
    return out

####### MAIN ########
print 'LOADING...'
argparser = argparse.ArgumentParser()
argparser.add_argument("-c", "--cluetext", dest="cluetext", help="clue text", default=None) # eg singer sumac
argparser.add_argument("-l", "--length", dest="length", help="answer length", default=None) # eg 5
argparser.add_argument("-p", "--pattern", dest="pattern", help="answer pattern, ? for unkown", default=None) # Z?TOP
argparser.add_argument("-t", "--test", dest="test", help="test flag", type=bool, default=False) # if true, run test
args = argparser.parse_args()
testflag = args.test
answer_dict = {}
answer_dicts = {}
reverse_dict = {}
reverse_dicts = {}
reversewords_dict = {}
reversewords_dicts = {}
if testflag:
    successes = list()
    fails = list()
    ns = nf = 0
    for a in xrange(3,16):
        with open('answers'+str(a)+'.json') as json_file:
            answer_dicts[str(a)] = json.load(json_file)
        with open('reverse'+str(a)+'.json') as json_file:
            reverse_dicts[str(a)] = json.load(json_file)
        with open('reverseword'+str(a)+'.json') as json_file:
            reversewords_dicts[str(a)] = json.load(json_file)
    testfile = 'universal - dec 14 2021.txt'
    #testfile = 'new york times - may 31 2021.txt'
    n = 1
    with open('puzzles/'+testfile,'r') as f:  # open in readonly mode
        content = f.readlines()
        for line in content:
            print line
            if n % 2 == 0:
                answer = cleananswer(line[:-1])
                answerlength = str(len(answer))
                x = solve(clue,answer_dicts[answerlength],reverse_dicts[answerlength],reversewords_dicts[answerlength])
                if x and answer in [y[0] for y in x]:
                    successes.append(answer+' '+ clue)
                    ns += 1
                else:
                    fails.append(answer+' '+ clue)
                    nf += 1
            else:
                clue = cleanclue(line[:-1])
                print clue
            n += 1
    print
    print 'SUCCESSES:',ns
    for item in successes:
        print item
    print
    print 'FAILURES:',nf
    for item in fails:
        print item
    print
    print 'SUCCESS RATE:', ns/ (1. * nf + 1. * ns)
else:

    solution = args.cluetext.replace('_',' ')
    answerlength = args.length
    p = args.pattern
    with open('answers'+answerlength+'.json') as json_file:
        answer_dict = json.load(json_file)
    if p:
        for key,val in answer_dict.items():
            val2 = {}
            for key1 in val:
                val2[key1] = val[key1]
                for i,letter in enumerate(key1):
                    if p[i] not in ['?', letter]:
                        del val2[key1]
                        break
            answer_dict.update({key: val2})

    with open('reverse' + answerlength + '.json') as json_file:
        reverse_dict = json.load(json_file)
    if p:
        for key,val in reverse_dict.items():
            val2 = {}
            for key1 in val:
                val2[key1] = val[key1]
                for i,letter in enumerate(key1):
                    if p[i] not in ['?', letter]:
                        del val2[key1]
                        break
            reverse_dict.update({key: val2})

    with open('reverseword' + answerlength + '.json') as json_file:
        reversewords_dict = json.load(json_file)
    if p:
        for key,val in reversewords_dict.items():
            val2 = {}
            for key1 in val:
                val2[key1] = val[key1]
                for i,letter in enumerate(key1):
                    if p[i] not in ['?', letter]:
                        del val2[key1]
                        break
            reversewords_dict.update({key: val2})


    x = solve(solution,answer_dict,reverse_dict,reversewords_dict)