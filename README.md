# LeGenderary - Determining gender from name

## Dependencies

**Fuzzy**

```sh
$ sudo pip install Fuzzy
```

## Methods

#### determineFirstName(nameArray)

```python
fullName = "Dr. Richard P. Feynman"
print gender.determineFirstName(fullName.split()) # Richard
```

#### determineFromGPeters(firstName)

```python
firstName = 'Richard'
print gender.determineFromGPeters(firstName) # male
```

#### determineFromDictionary(firstName)

```python
firstName = 'Richard'
print gender.determineFromDictionary(firstName) # male
```

#### determineFromSoundex(firstName)

```python
firstName = 'Rikard'
print gender.determineFromSoundex(firstName) # male
```

#### determineFromNysiis(firstName)

```python
firstName = 'Rikard'
print gender.determineFromNysiis(firstName) # male
```

#### determineFromMetaphone(firstName)

```python
firstName = 'Rikard'
print gender.determineFromMetaphone(firstName) # should be male
```

#### determineFromPhonetic(firstName)

```python
firstName = 'Rikard'
print gender.determineFromPhonetic(firstName) # male
```

#### randomGuess(firstName)

For the 2 given dictionaries, the success rate for male identification ranges between 39-43% and 80-82% for females

```python
firstName = 'Richard'
print gender.randomGuess(firstName) # male
```

#### determineFromBing(fullName)

```python
fullName = 'Richard P. Feynman'
print gender.determineFromBing(fullName) # male
```

#### determineFromInternet(fullName)

```python
fullName = 'Richard P. Feynman'
print gender.determineFromBing(fullName) # male
```


## Full Usage Example

```python
options = { 'male'          : 'male',
            'female'        : 'female',
            'androgynous'   : 'androgynous',
            'unknown'       : 'unknown',
            'maleConfirm'   : 'male needs confirmation',
            'femaleConfirm' : 'female needs confirmation',
            'dict1'         : 'dict1.txt',
            'dict2'         : 'dict2.txt',
           }

gender   = leGenderary(options)
fullName = "Dr. Richard P. Feynman"

firstName  = gender.determineFirstName(fullName.split())
gPeters    = gender.determineFromGPeters(firstName)
dictionary = gender.determineFromDictionary(firstName)

print dictionary
```
