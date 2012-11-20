"""
leGenderary.py

Copyright 2012 Kartik Talwar

Licensed under the BSD License

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import re
import sys
import time
import json
import fuzzy
import random
import urllib
import codecs
import base64
import urllib2


class leGenderary:

    def __init__(self, options):
        self.options    = options
        self.firstDict  = self.parseFirstDataSet(options['dict1'])
        self.secondDict = self.parseSecondDataSet(options['dict2'])
        self.customDict = self.parseSecondDataSet(options['customDict'])


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


    def determineFromGPeters(self, name):
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
            gender     = self.options['unknown']

        return gender


    def determineFromDictionary(self, firstName):
        firstName = self._sanitizeName(firstName)

        if firstName in self.customDict:
            gender = self.customDict[firstName]
            if gender == '00':
                return self.options['maleConfirm']
            if gender == '11':
                return self.options['femaleConfirm']
            return gender

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


    def determineFromPhonetic(self, firstName):
        soundex   = self.determineFromSoundex(firstName)
        nysiis    = self.determineFromNysiis(firstName)
        metaphone = self.determineFromMetaphone(firstName)

        genders = [soundex, nysiis, metaphone]

        if len(set(genders)) == len(genders):
            return self.options['unknown']

        return self._mostCommon(genders)


    def randomGuess(self, firstName):
        male      = self.options['male']
        female    = self.options['female']
        firstName = self._sanitizeName(firstName)

        def rand(m, f):
            prob = [self.options['male']] * m + [self.options['female']] * f
            return random.choice(prob)

        if len(firstName) > 2:
            last       = firstName[-1]
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
                return rand(m=40, f=60)
            if last is 'l':
                if secondlast in ['a', 'e', 'i', 'o', 'u', 'l']:
                    return rand(m=80, f=20)
            if last is 'e':
                if secondlast in ['i', 't', 'l']:
                    return female
                if secondlast in ['v', 'm', 'g']:
                    return male
                if secondlast in ['n', 'c', 's', 'e', 'd']:
                    return rand(m=35, f=65)
            if last is 'h':
                if secondlast in ['t', 'a']:
                    return female
                return male
            if last is 't':
                if secondlast in ['e', 'i']:
                    return female
                return male
            if last is 'm':
                return rand(m=90, f=10)

        return rand(m=65, f=35)


    def determineFromBing(self, name):
        sequence = [{"male"   : "%s and his",
                     "female" : "%s and her",
                     "idm"    : "his",
                     "idf"    : "her"},
                   #{"male"   : "his * and %s",
                   # "female" : "her * and %s",
                   # "idm"    : "his",
                   # "idf"    : "her"},
                   #{"male"   : "%s himself",
                   # "female" : "%s herself",
                   # "idm"    : "himself",
                   # "idf"    : "herself"},
                    {"male"   : "Mr %s",
                     "female" : "Mrs %s",
                     "idm"    : "mr",
                     "idf"    : "mrs"}]

        male, female, prob  = 0.0, 0.0, 0.0

        for q in sequence:
            p_m = self.bingSearch(q["male"]   % name, name, q['idm'])
            p_f = self.bingSearch(q["female"] % name, name, q['idf'])

            tot     = p_m + p_f + 10.0
            prob   += 1.0
            male   += (p_m*1.0) / tot
            female += (p_f*1.0) / tot

        male   /= prob
        female /= prob

        if abs(male-female) < 0.02:
            gender = self.options['unknown']
        elif male > female:
            gender = self.options['male']
        elif male < female:
            gender = self.options['female']
        else:
            gender = self.options['unknown']

        return gender


    def determineFromInternet(self, fullName):
        firstName = self.determineFirstName(fullName.split())
        gpeters   = self.determineFromGPeters(firstName)
        bing      = self.determineFromBing(fullName)

        genders = [gpeters, bing]

        if len(set(genders)) == len(genders):
            return self.options['unknown']

        return self._mostCommon(genders)


    def determineGender(self, fullName, **kwargs):

        required   = True

        if 'required' in kwargs:
            required = kwargs['required']

        firstName  = self.determineFirstName(fullName.split())
        definite   = [self.options['male'], self.options['female']]
        indefinite = [self.options['androgynous'], self.options['unknown']]

        dictionary = self.determineFromDictionary(firstName)
        if dictionary in definite:
            return dictionary

        phonetics  = self.determineFromPhonetic(firstName)
        if phonetics in definite:
            self._addToDictionary(firstName, phonetics, self.options['customDict'])
            return phonetics

        usetheweb  = self.determineFromInternet(fullName)
        if usetheweb in definite:
            if usetheweb == self.options['male']:
                self._addToDictionary(firstName, self.options['maleConfirm'], self.options['customDict'])
                return self.options['maleConfirm']
            if usetheweb == self.options['female']:
                self._addToDictionary(firstName, self.options['femaleConfirm'], self.options['customDict'])
                return self.options['femaleConfirm']

        if not required:
            return self.options['unknown']

        random     = self._mostCommon([self.randomGuess(firstName) for i in range(0,5)])
        if random in definite:
            if random == self.options['male']:
                return self.options['maleConfirm']
            if random == self.options['female']:
                return self.options['femaleConfirm']


    def parseFirstDataSet(self, fileName):
        names = {}
        f     = codecs.open(fileName, 'r', encoding='iso8859-1')
        line  = f.readline()

        while line:
            if line.startswith("#") or line.startswith("="):
                pass

            parts = filter(lambda p: p.strip() != "", line.split(" "))

            if "F" in parts[0]:
                name   = parts[1].lower()
                gender = self.options['female']
            elif "M" in parts[0]:
                name   = parts[1].lower()
                gender = self.options['male']
            else:
                name   = parts[1].lower()
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
        f     = codecs.open(fileName, 'r', encoding='iso8859-1').read()
        f     = set(f.split("\n"))

        for person in f:
            try:
                separate = person.split(',')
                name     = separate[0].lower()

                if int(separate[1]) == 0:
                    gender  = self.options['male']
                elif int(separate[1]) == 1:
                    gender  = self.options['female']
                else:
                    gender  = self.options['androgynous']

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
                self._appendToDict(soundhash, gender, soundexHash)

        return soundexHash


    def generateNysiisHash(self, dictionary, table=None):
        nysiisHash = {} if table is None else table

        for name, gender in dictionary.iteritems():
            name = self._sanitizeName(name)

            if len(name) > 1:
                nysiishash = fuzzy.nysiis(name)
                self._appendToDict(nysiishash, gender, nysiisHash)

        return nysiisHash


    def generateMetaphoneHash(self, dictionary, table=None):
        metaphoneHash = {} if table is None else table

        for name, gender in dictionary.iteritems():
            name = self._sanitizeName(name)

            if len(name) > 1:
                metaphonehash = fuzzy.DMetaphone()(name)
                self._appendToDict(metaphonehash, gender, metaphoneHash)

        return metaphoneHash


    def bingSearch(self, query, name, identifier):
        query   = urllib.quote_plus(query.encode('utf-8', 'ignore'))
        url     = "https://api.datamarket.azure.com/Data.ashx"
        url    += "/Bing/Search/Web?$format=json&Query='%s'" % query

        if len(self.options['bingAPIKey']) == 0:
            return 0

        request = urllib2.Request(url)
        apikey  = self.options['bingAPIKey']
        auth    = base64.encodestring("%s:%s" % (apikey, apikey)).replace("\n", "")

        request.add_header("Authorization", "Basic %s" % auth)

        res     = urllib2.urlopen(request)
        data    = res.read()
        parse   = json.loads(data)['d']['results']
        count   = 0

        for i in parse:
            title       = i['Title'].lower().replace(' ', '')
            description = i['Description'].lower().replace(' ', '')

            idx1 = description.find(name)
            idx2 = description.find(identifier)

            # Random weights ya'll
            if name.replace(' ', '') in title:
                count += 20
                if identifier in title:
                    count += 50

            if identifier in title:
                count += 5

            if idx1 != -1 and idx1 != -1:
                if idx1 < idx2:
                    count += 10
                if (idx2 - idx1) >= 0 and (idx2 - idx1) <= 35:
                    count += 50
                if idx2 < idx1:
                    count += 10

            count += 2

        return count


    def _appendToDict(self, soundhash, gender, array):
        if type(soundhash) in [str, unicode]:
            soundhash = [soundhash]

        male   = self.options['male']
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


    def _addToDictionary(self, name, gender, customDict):
        if gender == self.options['male']:
            gender = '0'
        if gender == self.options['female']:
            gender = '1'
        if gender == self.options['maleConfirm']:
            gender = '00'
        if gender == self.options['femaleConfirm']:
            gender = '11'

        if gender not in ['0', '1', '00', '11']:
            return

        data = name.lower() + ',' + gender
        f = open(customDict, 'a').write(data.encode('utf-8')+"\n")


    def _mostCommon(self, array):
        return max(set(array), key=array.count)


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
                'customDict'    : 'custom.txt',
                'bingAPIKey'    : ''
               }

    gender   = leGenderary(options)
    fullName = "Dr. Richard P. Feynman"
    detect   = gender.determineGender(fullName, required=False)

    print detect
