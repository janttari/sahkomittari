# sudo pip3 install flask
# sudo pip3 install flask_socketio
import __main__ #tuodaan pääohjelma
from flask import Flask, request, make_response, redirect, render_template
from flask_socketio import SocketIO, emit
import threading, time, logging, sys, pathlib, os.path, sys
'''pääohjelmassa metodit on_liittynyt '''
class FlaskPalvelin():
    __kaynnissa=False
    def __init__(self):
        if FlaskPalvelin.__kaynnissa==False:
            FlaskPalvelin.__kaynnissa = True
            self.palvelin=threading.Thread(target=self.__flaskPalvelin).start()
        else:
            sys.stderr.write("Tämä on jo käynnissä eikä käynnistetä uutta.\n")

    def __flaskPalvelin(self):
        self.clients = [] # [[asiakas,sid][asiakas,sid]]
        #self.app = Flask(__name__, template_folder='templates', static_url_path='/static', static_folder='static')
        self.app = Flask(__name__, template_folder='./templates', static_url_path='/static', static_folder='static')
        self.app.logger.disabled = True #hide flask messages
        log = logging.getLogger('werkzeug') #hide flask messages
        log.disabled = True #hide flask messages
        cli = sys.modules['flask.cli'] #hide flask messages
        cli.show_server_banner = lambda *x: None #hide flask messages
        self.app.config['SECRET_KEY'] = 'ines'
        socketio = SocketIO(self.app, async_mode='threading')

        @socketio.on('client_connect')
        def liittyi(data):
            uusi=data["nickname"] #selaimen lähettämässä nickname:ssa on asiakkaan nimi jota käytämme yksityisviesteihin
            self.clients.append([uusi,request.sid]) 
            if 'on_liittyi' in dir(__main__): #jos pääohjelmassa on tämän niminen metodi...
                __main__.on_liittyi(uusi)

        @socketio.on('disconnect') #poistetaan lähtenyt asiakas listalta
        def on_disconnect_test():
            #print("discon:",request.sid)
            for asindeksi in range(len(self.clients)):
                #print(asindeksi)
                if self.clients[asindeksi][1]==request.sid:
                    #print("remove:",request.sid)
                    if 'on_poistui' in dir(__main__): #jos pääohjelmassa on tämän niminen metodi...
                        __main__.on_poistui(self.clients[asindeksi])
                        del self.clients[asindeksi]
                    break

        @self.app.route('/', methods=['GET']) 
        def __index():
            #print("index")
            resp=make_response(render_template('index.html'))
            return resp

        @self.app.route('/txt', methods=['GET']) 
        def __indextxt():
            if os.path.isfile("/dev/shm/kwh"):
                with open("/dev/shm/kwh", "r") as kwhtiedosto:
                    kwh=kwhtiedosto.read()
            else:
                kwh="---"
            resp=make_response(kwh)
            return resp

        @socketio.on('client_message') #selaimelta tulevaa dataa
        def __receive_message(data):
            if 'on_selaimelta' in dir(__main__): #jos pääohjelmassa on tämän niminen metodi...
                __main__.on_selaimelta(data)
        self.app.run(host='0.0.0.0', port=5555, threaded=True) #Huomaa että tän paikka on lopussa!

    def elemArvot(self, json): #[vastaanottajat] jsondata
        jsondata='{"elementit": '+json+'}'
        #print(jsondata)
        with self.app.test_request_context('/'):
            emit("elem_arvot", jsondata, namespace="/", broadcast=True) #lähetetään kyseisen asiakkaan sid-numerolla


