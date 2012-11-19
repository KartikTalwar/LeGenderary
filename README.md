# LeGenderary - Determining gender from name

## Dependencies

**Fuzzy**

```sh
$ sudo pip install Fuzzy
```

**Name-Gender Dictionaries**

The dictionaries can be found on [downloads page] (https://github.com/KartikTalwar/LeGenderary/downloads)

## Methods


### Construct Options
______________________________________________________________

This are the keys and values associated with the dictionary you need to provide when the class 
is initialized.

|        Key        |                                   Values                                    |
|:-----------------:|:---------------------------------------------------------------------------:|
| **male**          | Output you'd like for male gender *(male, 0, man etc)*                      |
| **female**        | Output you'd like for female gender *(female, 1, women etc)*                |
| **androgynous**   | Output you'd like for androgynous name *(andro, 2 etc)*                     |
| **unknown**       | Output you'd like for indeterminant gender *(unknown, -1 etc)*              |
| **maleConfirm**   | Output you'd like for male where the gender confidence is low               |
| **femaleConfirm** | Output you'd like for female where the gender confidence is low             |
| **dict1**         | Path to first dictionary file *(dict1.txt or /home/user/docs/dict1.txt)*    |
| **dict2**         | Path to first dictionary file *(dict2.txt or /home/user/docs/dict2.txt)*    |
| **customDict**    | Path to custom dictionary file *(custom.txt or /home/user/docs/custom.txt)* |
| **bingAPIKey**    | Your Bing/Azure marketplace API Key. Register [here] (http://bit.ly/JmuoZW) |


### Hierarchy
______________________________________________________________

Each method listed below can be called an a standalone function. The basic function to be called is `determineGender()` 
which in turn calls `determineFromDictionary()`, `determineFromPhonetic()`, `determineFromInternet()` and `randomGuess()`
which call their respective sub-functions.


- determineFirstName(fullName)
- **determineGender(fullName, required)**
  - **determineFromDictionary(firstName)**
  - **determineFromPhonetic(firstName)**
     - determineFromSoundex(firstName)
     - determineFromNysiis(firstName)
     - determineFromMetaphone(firstName)
  - **determineFromInternet(fullName)**
     - determineFromBing(fullName)
     - determineFromGPeters(firstName)
  - **randomGuess(firstName)**


### Details
______________________________________________________________

- ### **determineFirstName(fullName)**

    Cleans out the common honorifics (Mr, Dr, Mrs, Sri etc) from the given name and returns the first name

    ```python
    fullName = "Dr. Richard P. Feynman"
    print gender.determineFirstName(fullName) # Richard
    ```

- ### **determineGender(fullName, required)**

    Calls the 4 main functions that check for gender from dictionary, internet, phonetics and random guessing.
    if `required` is set to True (default is True), the output will return either male of female (upon guessing).
    If set to False the output will be *unknown* upon failure to determine.


    ```python
    fullName = "Dr. Richard P. Feynman"
    print gender.determineGender(fullName, required=False) # male
    ```

    - #### **determineFromDictionary(firstName)**

        Checks for the first name in all 3 dictionaries, 2 built in and the one custom dictionary which contains tha values
        of names and genders that phonetic search and internet search find.

        ```python
        firstName = 'Richard'
        print gender.determineFromDictionary(firstName) # male
        ```

    - #### **determineFromPhonetic(firstName)**

        Performs all 3 phonetic searches and returns the most common predicted gender.

        ```python
        firstName = 'Rikard'
        print gender.determineFromPhonetic(firstName) # male
        ```

       - **determineFromSoundex(firstName)**

            Uses soundex algorithm to generate hashes for all dictionary items and finds the male and female 
            ratios for the given hash and returns the most common.

            ```python
            firstName = 'Rikard'
            print gender.determineFromSoundex(firstName) # male
            ```

       - **determineFromNysiis(firstName)**

            Uses nysiis algorithm to generate hashes for all dictionary items and finds the male and female 
            ratios for the given hash and returns the most common.

            ```python
            firstName = 'Rikard'
            print gender.determineFromNysiis(firstName) # male
            ```

       - **determineFromMetaphone(firstName)**

            Uses metaphone algorithm to generate hashes for all dictionary items and finds the male and female 
            ratios for the given hash and returns the most common.

            ```python
            firstName = 'Rikard'
            print gender.determineFromMetaphone(firstName) # should be male
            ```

    - #### **determineFromInternet(fullName)**

        Performs search through the web using the Bing API and gpeters.com

        ```python
        fullName = 'Richard P. Feynman'
        print gender.determineFromBing(fullName) # male
        ```

       - **determineFromBing(fullName)**

            Uses [Bing API] (https://datamarket.azure.com/dataset/5BA839F1-12CE-4CCE-BF57-A49D98D29A44) to predict 
            the gender by scanning the content excerpts from the first page results. Each method call uses 4 queries
            to determine the gender but the final gender is saved in the custom dictionary.

            ```python
            fullName = 'Richard P. Feynman'
            print gender.determineFromBing(fullName) # male
            ```

       - **determineFromGPeters(firstName)**

            Queries [gpeters.com] (http://www.gpeters.com/names/baby-names.php) and returns the gender based on commonality

            ```python
            firstName = 'Richard'
            print gender.determineFromGPeters(firstName) # male
            ```

    - #### **randomGuess(firstName)**

        Guesses the gender based on the alphabets used in a particular name
        For the 2 given dictionaries, the success rate for male identification 
        ranges between 39-43% and 80-82% for females

        ```python
        firstName = 'Richard'
        print gender.randomGuess(firstName) # male
        ```





## Full Usage Example


**myProgram.py**

```python
from leGenderary import leGenderary

options = { 'male'          : 'male', 
            'female'        : 'female',
            'androgynous'   : 'androgynous',
            'unknown'       : 'unknown',
            'maleConfirm'   : 'male needs confirmation',
            'femaleConfirm' : 'female needs confirmation',
            'dict1'         : 'dict1.txt',
            'dict2'         : 'dict2.txt',
            'customDict'    : 'custom.txt',
            'bingAPIKey'    : 'ABC123478ZML'
          }

gender      = leGenderary(options)
fullName    = "Dr. Richard P. Feynman"

firstName   = gender.determineFirstName(fullName.split()) # Richard
dictionary  = gender.determineFromDictionary(firstName)   # male
takeaguess  = gender.randomGuess(firstName)               # male

phonetic    = gender.determineFromPhonetic('Rikard')      # male
#soundex    = gender.determineFromSoundex('Rikard')
#nysiis     = gender.determineFromNysiis('Rikard')
#metaphone  = gender.determineFromMetaphone('Rikard')

internet    = gender.determineFromInternet(fullName)      # male
#gPeters    = gender.determineFromGPeters(firstName)
#usebing    = gender.determineFromBing(fullName)

getgender   = gender.determineGender(fullName)            # male

print firstName, getgender                               # Richard, male
```

## Authors

- [Kartik Talwar] (http://kartikt.com)


## Legal Stuff

Copyright (C) 2012 Kartik Talwar. See [LICENSE](https://github.com/KartikTalwar/LeGenderary/blob/master/LICENSE.md) for details.