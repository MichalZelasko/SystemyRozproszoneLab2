from flask import Flask, render_template, request
from routeLogic import RouteGraphHooper, RouteOpenStreetMap, findBest
import os

app = Flask(__name__)

@app.route('/<type>/<mean>/<start>/<destination>')
def distance(type, mean, start, destination) :
    routeA = RouteGraphHooper(start, destination, mean)
    routeB = RouteOpenStreetMap(start, destination, mean)
    if routeA.error or routeB.error :
        return render_template('indexError.html')
    indexA, durationA = routeA.getBestRoute(type)
    indexB, durationB = routeB.getBestRoute(type)
    if durationA > durationB :
        best = routeB.getDescription(indexB)
        alternative = routeA.getDescription(indexA)
    else :
        best = routeA.getDescription(indexA)
        alternative = routeB.getDescription(indexB)
    link1 = '/' + type + '/' + mean + '/' + start + '/' + destination + '/' + 'best_detail'
    link2 = '/' + type + '/' + mean + '/' + start + '/' + destination + '/' + 'alternative_detail'
    return render_template('indexRoute.html', link1=link1, link2=link2, route1=best, route2=alternative)

@app.route('/<type>/<mean>/<start>/<destination>/best_detail')
def bestDetails(type, mean, start, destination) :
    routeA = RouteGraphHooper(start, destination, mean)
    routeB = RouteOpenStreetMap(start, destination, mean)
    if routeA.error or routeB.error :
        return render_template('indexError.html')
    indexA, durationA = routeA.getBestRoute(type)
    indexB, durationB = routeB.getBestRoute(type)
    if durationA > durationB :
        best = routeB.getDescription(indexB)
        hints = routeB.getHints(indexB)
    else :
        best = routeB.getDescription(indexA)
        hints = routeB.getHints(indexB)
    return render_template('indexDetails.html', route1=best, route2=hints)

@app.route('/<type>/<mean>/<start>/<destination>/alternative_detail')
def bestAlternative(type, mean, start, destination) :
    routeA = RouteGraphHooper(start, destination, mean)
    routeB = RouteOpenStreetMap(start, destination, mean)
    if routeA.error or routeB.error :
        return render_template('indexError.html')
    indexA, durationA = routeA.getBestRoute(type)
    indexB, durationB = routeB.getBestRoute(type)
    if durationA > durationB :
        best = routeB.getDescription(indexA)
        hints = routeB.getHints(indexA)
    else :
        best = routeB.getDescription(indexB)
        hints = routeB.getHints(indexB)
    return render_template('indexDetails.html', route1=best, route2=hints)

@app.route('/')
def mainPage() :
    return render_template('index.html')

@app.route('/forms', methods=['POST'])
def forms():
    start = request.form['start']
    destination = request.form['destination']
    mean = request.form['select']
    type = request.form['selecttype']
    dictionary = {"Pieszo": "foot", "Samochodem": "car", "Rowerem": "bike"}
    dictionary2 = {"Najszybsza": "time", "Najkrótsza": "distance"}
    return distance(dictionary2[type], dictionary[mean], start, destination)

if __name__ == '__main__' :
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)