import re
"""
regex est une manier de rechercher un texte qui respecte un certain modèle
extrer les informations les information importantes des ligne de logs et a les transformer en données structurées
"""
def extract(row:str):
    #row paramétre qui recoit une ligne de log
    #str indique que row est de type string
    pattern=re.compile(r'(?P<month>\w{3})\s(?P<day>\d{1,2})\s(?P<time>\d{2}:\d{2}:\d{2})\s.+:\s(?P<message>\w+)')
    match=re.search(pattern,row)
    if match:
        print(match.groupdict())

       