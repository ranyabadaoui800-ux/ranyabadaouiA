import gzip 
import os 
"""
permet d'interagir avec le systeme d'exploitation mac... elle permet de cousulter les fichier d'un dossier 
creer un dossier , supp un fichier et de verifier certains chemains
"""
import os.path as pt
"""permet de manipuler le chemains des dossier et fichiers de manière portable et independante du systeme d'exploitation"""
from pathlib import Path
""" 
in:data
out:list of rows
 """
def ingest(path:str): 
    try:
        files=os.listdir(path) 
        
        """ permet de recuperer les noms des fichiers et dossiers qui se trouvent dans un dossier
        path indique le dossier examiner"""
        for file in files:
            file_path=pt.join(path,file)
            openner=gzip.open(file_path,mode='rt',encoding="utf-8") if file.endswith('.gz') else open(file_path)#operateur térnel
            #ouvrir le fichier pour lire son contenu sous forme de texte.
            # utiliser UTF-8 pour transformer les données du fichier en caractères lisibles.
            with openner as f:
                return f.readlines()
    except Exception as e:
        #Exception : représente une catégorie générale d'erreurs.
        print(e)
        return

if __name__=="__main__":
    data=ingest('./data')
    if data:
        print(data[:10])

