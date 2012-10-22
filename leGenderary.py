import os
import re
import sys
import time
import json
import fuzzy
import random
import urllib
import urllib2
import codecs
import base64


class leGenderary:

    def __init__(self, options):
        self.options = options
        self.firstDict = self.parseFirstDataSet(options['dict1'])
        self.secondDict = self.parseSecondDataSet(options['dict2'])


    def determineFirstName(self, nameArray):
        honorifics = ['mr', 'ms', 'md', 'mrs', 'dr', 'st', 'lcol', 'prince',
                      'mister', 'master', 'rev', 'revd', 'capt', 'lt',
                      'sri', 'smt', 'thiru', 'sir', 'maam', 'major', 'lord']

        length     = len(nameArray)
        cleanFirst = re.sub("[^A-Za-z]", "", nameArray[0]).lower()

        if length == 1:
            return nameArray[0]
        elif cleanFirst in honorifics:
            return self.determineFirstName(nameArray[1:])
        elif length >= 2:
            if len(cleanFirst) > 1:
                return nameArray[0]
            else:
                return ''
        else:
            return ' '.join(nameArray)


    def gPetersDotCom(self, name):
        url    = 'http://www.gpeters.com/names/baby-names.php?name=' + self._sanitizeName(name)
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        get    = opener.open(url).read()

        try:
            findGender  = self._cut("<b>It's a ", '</b>', get)
            findGender  = self.options['male'] if findGender.find('boy') == 0 else self.options['female']
            probability = self._cut("Based on popular usage", " times more common", get)
            probability = float(self._stripTags(probability).split()[-1])

            if probability < 1.20:
                gender = self.options['androgynous']
            else:
                gender = findGender
        except:
            gender = self.options['unknown']

        return gender


    def determineFromDictionary(self, firstName):
        firstName = self._sanitizeName(firstName)

        if firstName in self.firstDict:
            return self.firstDict[firstName]

        if firstName in self.secondDict:
            return self.secondDict[firstName]

        return self.options['unknown']


    def determineFromSoundex(self, firstName):
        hashTable = {}
        self.generateSoundexHash(self.firstDict, hashTable)
        self.generateSoundexHash(self.secondDict, hashTable)

        firstName = self._sanitizeName(firstName)
        nameHash  = fuzzy.Soundex(4)(firstName)

        if nameHash in hashTable:
            results = hashTable[nameHash]
            gender  = max(results, key=results.get)

            if results[gender] > 0:
                return gender

        return self.options['unknown']


    def determineFromNysiis(self, firstName):
        hashTable = {}
        self.generateNysiisHash(self.firstDict, hashTable)
        self.generateNysiisHash(self.secondDict, hashTable)

        firstName = self._sanitizeName(firstName)
        nameHash  = fuzzy.nysiis(firstName)

        if nameHash in hashTable:
            results = hashTable[nameHash]
            gender  = max(results, key=results.get)

            if results[gender] > 0:
                return gender

        return self.options['unknown']


    def determineFromMetaphone(self, firstName):
        hashTable = {}
        self.generateMetaphoneHash(self.firstDict, hashTable)
        self.generateMetaphoneHash(self.secondDict, hashTable)

        firstName = self._sanitizeName(firstName)
        nameHash  = fuzzy.nysiis(firstName)

        if nameHash in hashTable:
            results = hashTable[nameHash]
            gender  = max(results, key=results.get)

            if results[gender] > 0:
                return gender

        return self.options['unknown']


    def randomGuess(self, firstName):

        male = options['male']
        female = options['female']

        def rand(m, f):
            prob = [male] * m + [male] * f
            return random.choice(prob)

        if len(firstName) > 2:
            last = firstName[-1]
            secondlast = firstName[-2]

            if last in ['a', 'e', 'n', 'i']:
                if last is 'n' and secondlast in ['n', 'i', 'e']:
                    return female
                if last is not 'n':
                    return female
            if last in ['n', 's', 'd', 'r', 'o', 'k']:
                return male
            if last is 'y':
                if secondlast in ['a', 'o']:
                    return male
                if secondlast in ['l', 't']:
                    return female
                return rand(male=40, female=60)
            if last is 'l':
                if secondlast in ['a', 'e', 'i', 'o', 'u', 'l']:
                    return rand(male=80, female=20)
            if last is 'e':
                if secondlast in ['i', 't', 'l']:
                    return female
                if secondlast in ['v', 'm', 'g']:
                    return male
                if secondlast in ['n', 'c', 's', 'e', 'd']:
                    return rand(male=35, female=65)
            if last is 'h':
                if secondlast in ['t', 'a']:
                    return female
                return male
            if last is 't':
                if secondlast in ['e', 'i']:
                    return female
                return male
            if last is 'm':
                return rand(male=90, female=10)

        return rand(male=65, female=35)


    def parseFirstDataSet(self, fileName):
        names = {}
        f = codecs.open(fileName, 'r', encoding='iso8859-1')
        line = f.readline()

        while line:
            if line.startswith("#") or line.startswith("="):
                pass

            parts = filter(lambda p: p.strip() != "", line.split(" "))

            if "F" in parts[0]:
                name = parts[1].lower()
                gender = self.options['female']
            elif "M" in parts[0]:
                name = parts[1].lower()
                gender = self.options['male']
            else:
                name = parts[1].lower()
                gender = self.options['androgynous']

            if names.has_key(name):
                pass
            if "+" in name:
                for replacement in [ '', '-', ' ' ]:
                    name = name.replace('+', replacement).lower()
            else:
                names[name] = gender

            line = f.readline()

        f.close()

        return names


    def parseSecondDataSet(self, fileName):
        names = {}
        f = codecs.open(fileName, 'r', encoding='iso8859-1').read()

        for person in f.split("\n"):
            try:
                separate = person.split(',')
                name = separate[0].lower()

                if int(separate[1]) == 0:
                    gender = self.options['male']
                elif int(separate[1]) == 1:
                    gender = self.options['female']
                else:
                    gender = self.options['androgynous']

                names[name] = gender
            except:
                pass

        return names


    def generateSoundexHash(self, dictionary, table=None):
        soundexHash = {} if table is None else table

        for name, gender in dictionary.iteritems():
            name = self._sanitizeName(name)

            if len(name) > 1:
                soundhash = fuzzy.Soundex(4)(name)
                self._addToDict(soundhash, gender, soundexHash)

        return soundexHash


    def generateNysiisHash(self, dictionary, table=None):
        nysiisHash = {} if table is None else table

        for name, gender in dictionary.iteritems():
            name = self._sanitizeName(name)

            if len(name) > 1:
                nysiishash = fuzzy.nysiis(name)
                self._addToDict(nysiishash, gender, nysiisHash)

        return nysiisHash


    def generateMetaphoneHash(self, dictionary, table=None):
        metaphoneHash = {} if table is None else table

        for name, gender in dictionary.iteritems():
            name = self._sanitizeName(name)

            if len(name) > 1:
                metaphonehash = fuzzy.DMetaphone()(name)
                self._addToDict(metaphonehash, gender, metaphoneHash)

        return metaphoneHash


    def _addToDict(self, soundhash, gender, array):
        if type(soundhash) in [str, unicode]:
            soundhash = [soundhash]

        male = self.options['male']
        female = self.options['female']

        for i in soundhash:
            if i != None:
                if len(i) < 2:
                    break

                if gender == male:
                    if i in array:
                        array[i] = {str(male)   : 1 + array[i][str(male)],
                                    str(female) : array[i][str(female)]}
                    else:
                        array[i] = {str(male)   : 0,
                                    str(female) : 0}

                if gender == female:
                    if i in array:
                        array[i] = {str(male)   : array[i][str(male)],
                                    str(female) : 1 + array[i][str(female)]}
                    else:
                        array[i] = {str(male)   : 0,
                                    str(female) : 0}


    def _cut(self, start, end, data):
        rez = []
        one = data.split(start)

        for i in range(1, len(one)):
            two = one[i].split(end)
            rez.append(two[0])

        return rez[0] if len(rez) == 1 else rez


    def _stripTags(self, html):
        return re.sub("(<[^>]*?>|\n|\r|\t)", '', html)


    def _sanitizeName(self, name):
        name = name.lower()
        name = re.sub("[^A-Za-z]", "", name)
        return name



if __name__ == '__main__':

    options = { 'male'          : 'male',
                'female'        : 'female',
                'androgynous'   : 'androgynous',
                'unknown'       : 'unknown',
                'maleConfirm'   : 'male needs confirmation',
                'femaleConfirm' : 'female needs confirmation',
                'dict1'         : 'dict1.txt',
                'dict2'         : 'dict2.txt',
               }

    gender = leGenderary(options)
    fullName = "Dr. Richard P. Feynman"

    firstName  = gender.determineFirstName(fullName.split())
    gPeters    = gender.gPetersDotCom(firstName)
    dictionary = gender.determineFromDictionary(firstName)
    soundexH   = gender.generateSoundexHash(gender.secondDict)
    nysiishH   = gender.generateNysiisHash(gender.secondDict)
    metaphoneH = gender.generateMetaphoneHash(gender.secondDict)
    soundex    = gender.determineFromSoundex('Rikard')
    nysiis     = gender.determineFromNysiis('Rikard')
    metaphone  = gender.determineFromMetaphone('Rikard')
    takeaguess  = gender.randomGuess(firstName)

    print takeaguess

