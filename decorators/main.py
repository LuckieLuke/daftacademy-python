def greetings(callable):
    def reformat(*args):
        result = callable(*args).lower().split()
        reformatted = ' '.join([x[0].upper() + x[1:] for x in result])
        reformatted = 'Hello ' + reformatted
        return reformatted
    return reformat


@greetings
def name_surname():
    return 'kasia basia'


def is_palindrome(callable):
    def check(*args):
        sentence = callable(*args)
        clean_sentence = [x.lower() for x in sentence if x.isalnum()]
        rev = clean_sentence[::-1]
        if clean_sentence == rev:
            return f'{sentence} - is palindrome'
        else:
            return f'{sentence} - is not palindrome'
    return check


@is_palindrome
def sentence():
    return 'Łapał za kran, a kanarka złapał'


print(sentence())
