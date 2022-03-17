import requests
import json
from flask import jsonify

def getLength(length) :
    if length < 1000 : return str(round(length)) + " metr"
    else : return str(round(length / 1000, 1)) + " kilometr"

def getTime(time) :
    return str(round(time/3600)) + " godzin " + str(round((time%3600) / 60)) + " minut"

def getDescription(self, name, number = 0) :
        mean = " pieszo"
        if self.vehicle == 'car' :
            mean = " samochodem"
        elif self.vehicle == 'bike' :
            mean = " rowerem"
        return "Najlepsza trasa Według " + name + " z " + self.start.name + " do " + self.destination.name + mean + " to:\nDystans: " + str(getLength(self.getDetail('distance', number))) + "ów\n" + "Czas: " + str(getTime(self.getDetail('time', number)))

class Point :
    def __init__(self, name) :
        self.name = name
        self.response = None
        self.latitude = 0
        self.longitude = 0
        self.error = False
        self.getResponse()
        self.getCoordinates()

    def getResponse(self) :
        try :
            self.response = requests.get('https://nominatim.openstreetmap.org/search?q=' + self.name + '&format=json&viewbox=10.151367187500002,49.90171121726089,27.026367187500004,52.395715477302105')
        except :
            self.error = True

    def getCoordinates(self) :
        if not self.error :
            try :
                self.latitude = self.response.json()[0]['lat']
                self.longitude = self.response.json()[0]['lon']
            except :
                self.error = True

class RouteGraphHooper() :
    def __init__(self, start, destination, vehicle = 'foot') :
        self.start = Point(start)
        self.destination = Point(destination)
        self.vehicle = vehicle
        self.error = self.start.error or self.destination.error
        try :
            self.responseRoute = requests.get('https://graphhopper.com/api/1/route?vehicle=' + vehicle + '&locale=pl&key=LijBPDQGfu7Iiq80w3HzwB4RUDJbMbhs6BU0dEnn&elevation=false&instructions=true&turn_costs=false&point=' + self.start.latitude + '%2C' + self.start.longitude + '&point=' + self.destination.latitude + '%2C' + self.destination.longitude)
            self.routeDetails = self.responseRoute.json()['paths']
        except :
            self.error = True
        
    def printDetail(self) :
        for i in range(len(self.routeDetails)) :
            print(self.getDetail('distance', i))

    def getBestRoute(self, type) :
        shortestRoute = 100000000000
        self.shortestIndex = -1
        for i in range(len(self.routeDetails)) :
            if shortestRoute > self.getDetail(type, i) :
                shortestRoute, self.shortestIndex = self.getDetail(type, i), i
        return self.shortestIndex, self.getDetail(type, self.shortestIndex)

    def getDetail(self, type, number = 0) :
        if type == 'time' : return self.routeDetails[number][type] / 1000
        return self.routeDetails[number][type]  

    def getHints(self, number = 0) :
        text = ""
        for instruction in self.routeDetails[number]['instructions'] :
            t = instruction['text']
            distance = getLength(instruction['distance'])
            streetName = instruction['street_name']
            if streetName == "" : streetName = "nieznana"
            if t[0] in ['T', 'K'] : text += (t + " przez " + distance + "ów")
            else : text += ("Za " + distance + "ów" + " " + t )
            text += (" Ulica: " + streetName + "\n")
        return text

    def getDescription(self, number = 0) :
        return getDescription(self, "GraphHooper", number)

class RouteOpenStreetMap() :
    def __init__(self, start, destination, vehicle = 'foot') :
        self.start = Point(start)
        self.destination = Point(destination)
        self.vehicle = vehicle
        self.error = self.start.error or self.destination.error
        try :
            self.responseRoute = requests.get('https://routing.openstreetmap.de/routed-' + vehicle + '/route/v1/driving/' + self.start.longitude + ',' + self.start.latitude + ';' + self.destination.longitude + ',' + self.destination.latitude + '?overview=false&geometries=polyline&steps=true&hints=3toMhiTbDIYAAAAADQAAAAAAAAB6AAAAAAAAAFQwtUAAAAAAjP1YQgAAAAANAAAAAAAAAHoAAAC66QAAYzYwAdXl-wJYNjABe-L7AgAAzxIy831_%3BRIzsjbSM7I0eAAAAEQAAAAAAAAArAAAAWuVIQeGW30AAAAAAiaCQQR4AAAARAAAAAAAAACsAAAC66QAAV4xAAbf_HAOFiUABFv8cAwAADwoy831_')
            self.routeDetails = self.responseRoute.json()['routes']
        except :
            self.error = True
        self.dictionary = {"continue": "Kontynuuj", "depart": "Jedź", "turn": "skręć", "uturn": "skręć", "end of road": "na końcu drogi skręć", "new name": "Jedź", "roundabout": "na rondzie", "roundabout turn": "na rondzie", "left" : "w lewo", "right": "w prawo", "straight": "prosto", "slight right": "lekko w prawo", "exit roundabout": "zjedź z ronda", "slight left": "lekko w lewo", "on ramp": "na zjeździe", "off ramp": "zjedź", "merge": "włącz się", "rotary": "na rondzie", "exit rotary": "zjedź z ronda", "arrive": "jesteś na miejscu", "fork": "na rozjeździe", "notification": "uwaga", "sharp right": "ostro w prawo", "sharp left": "ostro w lewo"}

    def printDetail(self) :
        for i in range(len(self.routeDetails)) :
            print(self.getDetail('distance', i))

    def getBestRoute(self, type) :
        shortestRoute = 100000000000
        self.shortestIndex = -1
        for i in range(len(self.routeDetails)) :
            if shortestRoute > self.getDetail(type, i) :
                shortestRoute, self.shortestIndex = self.getDetail(type, i), i
        return self.shortestIndex, self.getDetail(type, self.shortestIndex)

    def getDetail(self, type, number = 0) :
        if type == 'time' : type = 'duration'
        return self.routeDetails[number][type]  

    def getText(self, maneuver) :
        type = maneuver['type']
        try :
            modifier = maneuver['modifier']
        except :
            modifier = "straight"
        try :
            type = self.dictionary[type]
        except :
            type = "Jedź"
        try :
            modifier = self.dictionary[modifier]
        except :
            type = "Prosto"
        return type + " " + modifier

    def getHints(self, number = 0) :
        text = ""
        distance = str(0)
        for instruction in self.routeDetails[number]['legs'][0]['steps'] :
            maneuver = instruction['maneuver']
            t = self.getText(maneuver)
            dist = getLength(instruction['distance'])
            streetName = instruction['name']
            if streetName == "" : streetName = "nieznana"
            if t[0] in ['J', 'K'] : text += (t + " przez " + distance + "ów")
            else : text += ("Za " + distance + "ów" + " " + t )
            text += (" Ulica: " + streetName + "\n")
            distance = dist
        return text

    def getDescription(self, number = 0) :
        return getDescription(self, "OpenStreetMap", number)

def findBest(routeA, routeB, type) :
    indexA, durationA = routeA.getBestRoute(type)
    indexB, durationB = routeB.getBestRoute(type)
    Type = 'Najszybsza'
    if type == 'distance' :
        Type = 'Najkrótsza'
    if durationA > durationB :
        return Type + ": \n" + routeB.getDescription(indexB) + "\n\nAlternatywna trasa: \n" + routeA.getDescription(indexA) + "\n\n"
    else :
        return Type + ": \n" + routeA.getDescription(indexA) + "\n\nAlternatywna trasa: \n" + routeB.getDescription(indexB) + "\n\n"



if __name__ == '__main__' :
    routeA = RouteGraphHooper('Kraków', 'Krynica-Zdrój', 'bike')
    print(routeA.getDescription())
    print(routeA.getHints())      

    routeB = RouteOpenStreetMap('Kraków', 'Krynica-Zdrój', 'bike')
    print(routeB.getDescription())
    print(routeB.getHints()) 

    print(findBest(routeA, routeB, 'distance'))
    print(findBest(routeA, routeB, 'time'))