from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import datetime
import requests


mongoServerUrl = 'mongodb://localhost' # Docker-compose.yml required
mongoServerPort = 27017
urlsToScrap = [
    'https://www.popsci.com/technology',
    'https://www.science-et-vie.com/cerveau-et-intelligence',
    'https://www.zdnet.com/'
]

clientConnection = MongoClient(mongoServerUrl, mongoServerPort)


def getResultsCollection():
    try:
        # Try to validate a collection, if it fails, create collection (see except)
        clientConnection.db.validate_collection("Resultats")
        resultsCollection = clientConnection.db.Resultats
    except OperationFailure:
        #print("This collection doesn't exist. create it")
        resultsCollection = clientConnection.db.Resultats

    return resultsCollection


def saveItem(item):
    saved_id = clientConnection.db.Resultats.insert_one(item).inserted_id
    print('Enregistré!')

    if not saved_id:
        print('Attention, item non enregistré. A Débugguer!')


def listItems(dateStart = None, dateEnd = None):
    data = clientConnection.db.Resultats.find({})

    if dateEnd and not dateStart:
        data = clientConnection.db.Resultats.find({
            'date_creation': {'$lte': dateEnd}
        })

    if dateStart and not dateEnd:
        data = clientConnection.db.Resultats.find({
            'date_creation': {'$gte': dateStart}
        })

    if dateStart and dateEnd:
        data = clientConnection.db.Resultats.find({
            'date_creation': {'$gte': dateStart, '$lte': dateEnd}
        })

    '''
    if len(list(data)) == 0:
       print("Aucun enregistrement! La collection 'Resultats' est vide")
    '''

    for i in data:
        print(i)


def getUrlText(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }
    pageToScrap = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(pageToScrap.content, 'html.parser')

    # Extract body text using get_text()
    element = soup.find('body')
    text_content = element.get_text(separator=' ', strip=True)
    # print("Text: \n", text_content)
    return text_content


def searchWord():
    print(' Entrez le mot à rechercher: ')
    word = input()

    for url in urlsToScrap:
        txt = getUrlText(url)
        wordCount = sum(elt.lower() == word.lower() for elt in txt.split())

        if wordCount > 1:
            item = {'lien': url, 'mot': word, 'nombre': wordCount, 'date_creation': datetime.datetime.now()}
            saveItem(item)


def manageDates():
    dateStart = input("Entrez date DEBUT au format YYYY-MM-DD : ")

    dateEnd = input("Entrez date FIN au format YYYY-MM-DD : ")

    if dateStart > dateEnd:
        print("La date debut doit etre avant la date de fin")

    if dateStart:
        dateStart = datetime.datetime.strptime(dateStart, '%Y-%m-%d')

    if dateEnd:
        dateEnd = datetime.datetime.strptime(dateEnd, '%Y-%m-%d')

    return (dateStart, dateEnd)


def menu():
    choixUser = True
    while choixUser:
        menuList = """
        1 = Rechercher un mot et enregistrer
        2 = Lister le contenu de la collection Resultats
        3 = Lister le contenu de la collection Resultats suivant un intervalle de dates
        0 =  Quitter"""

        print(menuList)

        try:
            choixUser = int(input())
            print("Votre choix est {}".format(choixUser))
            if choixUser == 0:
                exit()
            elif choixUser == 1:
                searchWord()
            elif choixUser == 2:
                listItems()
            elif choixUser == 3:
                (dateStart, dateEnd) = manageDates()
                listItems(dateStart, dateEnd)
        except TypeError:
            print("Votre choix n'est pas valide")
            #print(type(choixUser))


if __name__ == '__main__':
    getResultsCollection()
    menu()