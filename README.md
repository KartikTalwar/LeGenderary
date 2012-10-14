# LeGenderary - Determining gender from name


## Methods

#### determineFirstName(nameArray)

```python
fullName = "Dr. Richard P. Feynman"
print gender.determineFirstName(fullName.split()) # Richard
```

#### gPetersDotCom(firstName)

```python
firstName = 'Richard'
print gender.gPetersDotCom(firstName) # male
```

#### determineFromDictionary(firstName)

```python
firstName = 'Richard'
print gender.determineFromDictionary(firstName) # male
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
gPeters    = gender.gPetersDotCom(firstName)
dictionary = gender.determineFromDictionary(firstName)

print dictionary
```
