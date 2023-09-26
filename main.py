import requests
import json
import bs4
import datetime
import re
from pathlib import Path


def get_status(class_name):
    if class_name == 'game-fin':
        return 'finalizado'
    elif class_name == 'game-play':
        return 'jugando'
    elif class_name == 'game-time':
        return 'no empezado'
    elif class_name == 'game-sus':
        return 'suspendido'
    else:
        return ""

# import requests
# import bs4
# link = "https://www.promiedos.com.ar/copadeliga"
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}
# res = requests.get(link, headers=headers)
# soup = bs4.BeautifulSoup(res.text, 'html.parser')

# liga_nombre = ["primera","inglaterra","francia","italia","espana","alemania","paisesbajos","brasil","uruguay","paraguay","colombia","chile","mexico","usa"]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}
link = "https://www.promiedos.com.ar/primera"
res = requests.get(link, headers=headers)
soup = bs4.BeautifulSoup(res.text, 'html.parser')
arr = soup.select("#fixtseccion div")
liga = soup.select("#titulos")[0].text.strip()

fechas_totales = 0
codigo_liga = 14 # codigo argentina
fechas_arr = []
fecha_act = 1

for el in arr:
    if el.has_attr("class"):
        if el["class"][0] == "cfechact" or el["class"][0] == "cfecha":
            fechas_totales = fechas_totales + 1
        if el["class"][0] == "cfechact":
            fecha_act = el.text

fechas_cant = range(1, fechas_totales+1)



for fecha_num in fechas_cant:
    link_fecha = "https://www.promiedos.com.ar/verfecha.php?fecha=" + str(fecha_num) + "_"+ str(codigo_liga)
    res1 = requests.get(link_fecha, headers=headers)
    soup1 = bs4.BeautifulSoup(res1.content.decode('utf-8'), 'html.parser')
    partido_arr = soup1.select("#fixturein tr")
    dia = ""
    partidos = 0
    autores_arr = []
    fecha = {"fecha":fecha_num, "partidos":[]}

    for i in range(len(partido_arr)):
        if partido_arr[i].has_attr("class"):
            if partido_arr[i]["class"][0] == "goles":
                gl = partido_arr[i].select("td")[0].text
                gv = partido_arr[i].select("td")[1].text
                autores_arr.append([gl, gv])

    for i in range(len(partido_arr)):
        partido = ""
        if partido_arr[i].has_attr("class"):
            if partido_arr[i]["class"][0] == "diapart":
                dia = partido_arr[i].text
        elif partido_arr[i].has_attr("id"):
            
            pid = int(partido_arr[i]["id"][1:])
            row = partido_arr[i].select("td")
            estado = get_status(row[0]["class"][0])
            cronometro = row[0].text.strip()
            hay_ficha = len(row[5].select("a")) > 0

            local = row[1].text
            visitante = row[4].text

            escudo_local = row[1].select("img")[0]["src"]
            escudo_visitante = row[4].select("img")[0]["src"]

            rojas_local = len(row[2].select(".roja"))
            rojas_visitante = len(row[3].select(".roja"))

            goles_local = ""
            if row[2].text != "":
                goles_local = int(row[2].text)

            goles_visitante = ""
            if row[3].text != "":
                goles_visitante = int(row[3].text)

            resultado = ""
            if goles_local > goles_visitante:
                resultado = "L"
            elif goles_local < goles_visitante:
                resultado = "V"
            elif goles_local == goles_visitante and goles_local != "" and goles_visitante != "":
                resultado = "E"
            else:
                resultado = ""

            ficha = ""
            if hay_ficha:
                f = row[5].select("a")[0]["href"]
                ficha = re.search("=\w+",f)[0][1:]
            else:
                ficha = ""
            autores_local = autores_arr[partidos][0][:-2].split("; ")
            autores_visitante = autores_arr[partidos][1][:-2].split("; ")

            partidos = partidos+1
            partido = {"id":pid,"dia":dia,"estado":estado, "cronometro":cronometro, "escudo_local":escudo_local, "local":local, "goles_local":goles_local, "rojas_local":rojas_local,"escudo_visitante":escudo_visitante,"visitante":visitante, "goles_visitante":goles_visitante,"rojas_visitante":rojas_visitante,"ficha":ficha,"autores_local":autores_local,"autores_visitante":autores_visitante, "resultado":resultado}
    
        if partido != "":
            fecha["partidos"].append(partido)
    
    fechas_arr.append(fecha)
    print(str(fecha_num))

now = datetime.datetime.now()
updatetime =  str(now.year)+"/"+str(now.month)+"/"+str(now.day)+"_"+ str(now.hour)+":"+str(now.minute)+":"+str(now.second)

main_obj = { "fecha_actual":fecha_act , "fechas":fechas_arr, "actualizado":updatetime }
contenido = json.dumps(main_obj)

ruta = Path(__file__).parent.resolve().joinpath('datos.json')
archivo = open(ruta, 'w', encoding='UTF-8')
archivo.write(contenido)
archivo.close()






