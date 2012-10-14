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
                'dictionary'    : 'dict1.txt',
                'dictionary2'   : 'dict2.txt',
                'bingapikey'    : ''
               }

    gender = leGenderary(options)
    fullName = "Dr. Richard P. Feynman"

    firstName = gender.determineFirstName(fullName.split())
    gPeters   = gender.gPetersDotCom(firstName)

    print gPeters

