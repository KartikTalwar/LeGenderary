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



## Full Usage Example

```python
options = { 'male'          : 'male',
            'female'        : 'female',
            'androgynous'   : 'androgynous',
            'unknown'       : 'unknown',
            'maleConfirm'   : 'male needs confirmation',
            'femaleConfirm' : 'female needs confirmation',
            'dictionary'    : 'dict1.txt',
            'dictionary2'   : 'dict2.txt'
           }

gender   = leGenderary(options)
fullName = "Dr. Richard P. Feynman"

firstName = gender.determineFirstName(fullName.split())
gPeters   = gender.gPetersDotCom(firstName)

print gPeters # male
```
