import cherrypy
import os
import psycopg2
import smtplib
from datetime import datetime

from psycopg2 import Error
from psycopg2.extras import DictCursor
from jinja2 import Environment, FileSystemLoader

 env = Environment(loader=FileSystemLoader('html'))

Config = 0
conn = 0

CompName = os.environ._data['COMPUTERNAME']

class ClimatServer(object):
    @cherrypy.expose
    def index(self):
        data_to_show = 'Hello'+ ' world'
        tmpl = env.get_template('index.html')
        return tmpl.render(data=data_to_show)
        return

    @cherrypy.expose
    def createtable(self):

        local_conn()
        cur = conn.cursor()
        try:
            cur.execute("CREATE TABLE test (id serial PRIMARY KEY, temp varchar, wet varchar, date timestamp );")
            conn.commit()
        except (Exception, Error) as error:
             return error.args[0]
        finally:
            if conn:
                cur.close()
                conn.close()

    @cherrypy.expose
    def climat(self,tem):
        local_conn()
        cur = conn.cursor(cursor_factory=DictCursor)
        currenttime = datetime.today()
        sql = "INSERT INTO test (temp,date) VALUES (%s,%s)"
        cur.execute(sql, (tem, currenttime))

        conn.commit()
        conn.close()

        if int(float(tem)) < 0:
            mail(tem)

        return "ok"

    @cherrypy.expose
    def lastemp(self):
      #  index_html = ''' <strong>{{ temp }}</strong>'''
        lasttemp = givetemp()
        return lasttemp

def givetemp():
       local_conn()

       cur = conn.cursor(cursor_factory=DictCursor)

       #      currenttime = datetime.today()
       sql = "SELECT * FROM test order by date DESC limit 1"
       cur.execute(sql)
       results = cur.fetchall()
       conn.close()
       x = results[0]["date"]
       st = "{:%d %b, %H:%M} -> {} C".format(results[0]["date"],results[0]["temp"])
       return st

def mail(temp):
    fromaddr = "exidan.alert@gmail.com"
    toaddrs = "exidan@ya.ru"
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.starttls()
    smtpObj.login(fromaddr, '8ik(OL0p')
    msg = ("From: %s\r\nTo: %s\r\n\r\n" % (fromaddr, ", ".join(toaddrs)))
    smtpObj.sendmail(fromaddr, toaddrs, msg + "Temp: "+temp)
    smtpObj.quit()
    return

def heroku():
    global DATABASE_URL
    DATABASE_URL = os.environ['DATABASE_URL']
    global conn
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    global config
    config = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': int(os.environ.get('PORT', 5000)),
        },
        '/assets': {
            'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'assets',
        }
    }
def local_conn():

    global conn
    if CompName == 'ServEx':
        conn = psycopg2.connect(user="postgres",
                                password="1007",
                                host="127.0.0.1",
                                port="5432",
                                database="climat"
                                )
    elif CompName == 'EOPT':
        conn = psycopg2.connect(user="postgres",
                                password="E0bMq4",
                                host="pa-324-serv",
                                port="5432",
                                database="opt_test"
                                )
    else:
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

def local():
    global config
    config = {
        'global': {
            'server.socket_host': '127.0.0.1',
                  },
        '/css': {
            'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'css',
        }
    }

if CompName == 'ServEx' or CompName == 'EOPT':
    local()
else:
    heroku()


cherrypy.quickstart(ClimatServer(), '/', config=config)