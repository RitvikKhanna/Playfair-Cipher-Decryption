#a10


import sys,re

def main():
    
    # Get arguments from standard input
    # If no file is specified generate the error and exit
    if len(sys.argv) == 1:
        print("Ciphertext file must be specified!")
        sys.exit()

    # If the file is specified open the file and use 'wells.txt'
    # as the corpus file
    c = getFile(sys.argv[1])
    corpus = getFile('wells.txt')

    # If n is specified in the command line use that or just use 3 as the default value    
    if len(sys.argv) > 2:
        n = int(sys.argv[2])
    else:
        n = 3 # default value
    
    # get bigrams from the corpus and the ciphertext file
    bigramsRef = getCorpusBigrams(corpus)
    ctbigrams = getCTBigrams(c)
    
    # map the n most frequent ciphertext bigrams to the most frequent corpus bigrams
    mapping = mapNBigrams(bigramsRef, ctbigrams, n)
    
    while True:
        # loops infinitely
        # get input ciphertext from user
        enciphered = input()

        if enciphered == 'quit':        # for testing
            break
        
        # for each word in the input:
        for word in enciphered.split():
            # construct regular expressions for known bigrams
            regexp = subBigrams(word, mapping)
            regexList = searchWords(regexp)
            finalList = corpusFreq(corpus,regexList)
            finalwords = ' '.join(finalList)
            print(finalwords.lower())
    
    return

def getFile(filename):
    # returns a string of the contents of a file
    f = open(filename, 'r')
    s = f.read()
    f.close()
    return s

def preproc(aString):
    # convert to uppercase, remove non-alpha chars (keep spaces), split into words
    s = aString.upper()
    for c in s:
        if c not in ' ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            s = s.replace(c, ' ')
            
    s = s.split()
    return s

def dictToSortedList(dictionary, n):
    # returns a list of n keys in order of their values, highest to lowest
    # for tiesbreaking, goes in alphabetical order
    
    result = []
    for i in range(len(dictionary)):
        if n == 0:
            break
        # get the maximum
        maxkey = ''
        maxval = -1
        for item in dictionary:
            if dictionary[item] > maxval:
                # found max
                maxkey = item
                maxval = dictionary[item]
            elif dictionary[item] == maxval:
                # found something equal to the current max
                # tie breaking by alphabetical order
                if item < maxkey:
                    maxkey = item
        # so that this key will no longer be considered for max
        dictionary[maxkey] = -2
        result.append(maxkey)
        
        n -= 1
    # return the keys in order
    return result
                
    
    

def getCTBigrams(ciphertext):
    # different than corpus bigrams bc these must not overlap
    bigrams = {}
    
    # remove non-alpha chars, convert to uppercase etc
    ciphertext = preproc(ciphertext)
    
    for word in ciphertext:
        # get bigrams and their counts
        if len(word) ==1:
            # word is too small to have bigrams
            continue
        
        # word is large enough to have bigrams
        i = 0
        while i < len(word)-1:
            bigram = word[i]+word[i+1]
            if bigram in bigrams:
                # increment its count
                bigrams[bigram] +=1
            else:
                # set count to 1
                bigrams[bigram] = 1
            # go to the next 2 chars
            i += 2
    
    # return the dict of bigram counts
    return bigrams
    

def getCorpusBigrams(corpus):
    # counts the bigrams in the corpus file
    # DOES overlap bigrams
    bigrams = {}
    
    # remove non-alpha chars, convert to uppercase, etc
    corpus = preproc(corpus)
    
    for word in corpus:
        # get bigrams and their count
        if len(word) ==1:
            # word is too short to have bigrams
            continue
        for i in range(len(word)-1):
            bigram = word[i]+word[i+1]
            if bigram in bigrams:
                # increment its count
                bigrams[bigram] +=1
            else:
                # set its count to 1
                bigrams[bigram] = 1
                
        # return dict of bigrams and their counts
    return bigrams

def mapNBigrams(reference, cipherBGs, n):
    # maps the n most frequent ciphertext bigrams to the n most frequent corpus bigrams
    
    # get the lists of n most frequent bigrams
    reference = dictToSortedList(reference, n)
    cipherBGs = dictToSortedList(cipherBGs, n)
   
    mapping = {}
    # map the bigrams
    for i in range(n):
        mapping[cipherBGs[i]] = reference[i] 
    return mapping

def subBigrams(ciphertext, mapping):
    # returns a LIST of regex
    # the reason why its a list is because the ciphertext word will always have 
    # an even numbered length, even if the word is of odd length. so, we need 2 
    # regular expressions, one for each case
    # note: will not replace if there are two bigrams overlapping (ex. ABC where AB and BC both have mappings)
    # assumes no whitespace
    
    # to keep track of what characters have been changed
    changed = [False]* len(ciphertext)

    ciphertext = list(ciphertext)
    
    for i in range(len(ciphertext)-1):
        # if this has already been replaced, go to the next char
        if changed[i]:
            continue
        
        # for each character that has a neighbor to the right
        bigram = ciphertext[i] + ciphertext[i+1]
        
        if bigram in mapping:
            # this character has not been changed yet
            changed[i] = True
            changed[i+1] = True
            
            # replace with the mapping
            ciphertext[i], ciphertext[i+1] = mapping[bigram][0], mapping[bigram][1]
   
   # replace characters that have not been changed with . 
    for i in range(len(ciphertext)):
        if changed[i] == False:
            ciphertext[i] = '.'
        
    regexp = ['^'+ ''.join(ciphertext) + '$'] # this is for the even case
    
    # for the odd case - if the end of the ciphertext is a known bigram, there
    # is no odd case
    if ciphertext[len(ciphertext)-1] == '.':
        odd = '^'+ ''.join(ciphertext)[:-1] + '$'
        regexp.append(odd)
    
    return regexp

def searchWords(regexp):

    # regexp is a list of the regular expressions generated.
    # regexList is a list of all the words found in the dictionary
    # after compiling the regular expression
    # This method returns the list with all the possible words for all the
    # regular expressions i.e for both odd and even cases if any
    regexList = []
    words = getFile("dictionary.txt")
    words = words.split()
        
    for item in regexp:
        for word in words:
            item = re.compile(item)
            if re.match(item,word):
                regexList.append(word)

    return regexList
        

def corpusFreq(corpus,regexList):

    # This method first processes the corpus file and returns
    # a list of the words

    # The frequencyDict is a dictionary with word as the key
    # and the frequency (i.e the count) as the value

    # After getting the frequencyDict we use the dicToSortedList
    # method to sort it in the order of increasing frequency and
    # in case of same frequency list them alphabetically

    # The sorted list is then returned

    newCorpus = preproc(corpus)

    frequencyDict = {}

    for word in regexList:
        
        count = 0
        for item in newCorpus:

            if word == item:
                count = count + 1

        frequencyDict[word]=count

    frequencyDict = dictToSortedList(frequencyDict,len(frequencyDict))

    return frequencyDict

                


main()
