import os
import re
import sys
import time
import json
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


    def _cut(self, start, end, data):
        rez = []
        one = data.split(start)

        for i in range(1, len(one)):
            two = one[i].split(end)
            rez.append(two[0])

        if len(rez) is 1:
            return rez[0]

        return rez


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

    print dictionary

