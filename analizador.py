from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import tkinter.scrolledtext as tkst
from requests import get
import socket
import urllib
from urllib.request import urlopen
import subprocess
import os


win = Tk()
pestañas = ttk.Notebook(win)
win.title("ANALIZADOR RPI")
win.geometry('320x240')
win.attributes('-fullscreen',True)

pestaña1 = ttk.Frame(pestañas)
pestañas.add(pestaña1, text='REDES')

pestaña4 = ttk.Frame(pestañas)
pestañas.add(pestaña4, text='INFO')

pestaña2 = ttk.Frame(pestañas)
pestañas.add(pestaña2, text='HOSTS')

pestaña3 = ttk.Frame(pestañas)
pestañas.add(pestaña3, text='DUMP')

pestaña5 = ttk.Frame(pestañas)
pestañas.add(pestaña5, text='CONF')

pestañas.grid(row=0 , column=0)

def exitProgram():
    print("Exit Button pressed")
    win.destroy()


def ippublica():
    ip_text.delete("1.0", END)
    print("Buscando IP publica")
    ip = get('https://api.ipify.org').text
    print("La ip publica es: ".format(ip))
    ip_text.insert("1.0", format(ip))
    ip_text.config(state=DISABLED)
    subprocess.call("echo '%s'>ip_publica" %ip, shell=True)


def ipprivada():
    privada_text.delete("1.0", END)
    subprocess.call("ifconfig | grep -w inet | awk {'print $2'}>ip_privada", shell=True)
    if os.path.isfile('ip_privada'):
            with open('ip_privada', 'r') as resultados:
                for ip in resultados:
                    if ip != "127.0.0.1\n":
                        global privada
                        print("IP: %s" %ip)
                        privada_text.insert("1.0", "%s" %ip)
                        privada = ip
                    privada_text.config(state=DISABLED)
    #subprocess.call("rm ip_privada", shell=True)
    privada_text.config(state=DISABLED)
    
def testconnect():
    try:
        response = urlopen('https://www.google.com/', timeout=10)
        print("OK")
        test_text.delete("1.0", END)
        test_text.insert("1.0", "OK")
        test_text.config(state=DISABLED)
        return True
    except:
        print("NO")
        test_text.delete("1.0", END)
        test_text.insert("1.0", "FALLO")
        test_text.config(state=DISABLED)
        return False
        
def buscarredes():
    wifi_text.delete("1.0", END)
    subprocess.call("sudo iwlist wlan0 scan | grep -E 'ESSID|Encryption' | awk {'print $1 $2'}>resultados_wifis", shell=True)
    if os.path.isfile('resultados_wifis'):
        with open('resultados_wifis', 'r') as resultados:
            for wifi in resultados:
                print("WIFI: %s" %wifi)
                wifi_text.insert("1.0", "%s" %wifi)
        wifi_text.config(state=DISABLED)
    #subprocess.call("rm resultados_wifis", shell=True)


def hostsactivos():
        global privada
        pos = privada.rfind(".")
        privada = privada[:pos]
        privada += ".0"
        print(privada)
        subprocess.call("sudo nmap -sP -n '%s'/24 | grep -v \"Starting Nmap\" | grep -v \"Nmap done\"|grep 'Nmap'|sudo sed 's/Nmap scan report for//' > hosts_activos" %privada, shell=True)
        if os.path.isfile('hosts_activos'):
                with open('hosts_activos', 'r') as resultados:
                        for activos in resultados:
                            print("ACTIVOS: %s" %activos)
                            activos_text.insert("1.0", "%s" %activos)
                activos_text.config(state=DISABLED)
def servicios():
    if messagebox.askyesno('IMPORTANTE', 'Esta operación puede tardar bastante ¿Desea continuar?', icon='warning' ) == True:
        subprocess.call("sudo nmap -sSV -iL hosts_activos -oX servicios.xml", shell=True)
        print("Escaneo de servicios finalizado")
    else:
        print("Cancelado por el usuario")
        
        
def capturaeth():
    if messagebox.askyesno('IMPORTANTE', 'Esta operación puede llevar unos minutos. ¿Desea continuar?', icon='warning' ) == True:
        subprocess.call("sudo tcpdump -i eth0 -c 1000 -W 1 -w captura_eth.pcap", shell=True)
        print("Captura finalizada")
    else:
        print("Cancelado por el usuario")
    
def capturawlan():
    activos_text.delete("1.0", END)
    if messagebox.askyesno('IMPORTANTE', 'Esta operación puede llevar unos minutos. ¿Desea continuar?', icon='warning' ) == True:
        subprocess.call("sudo tcpdump -i wlan0 -c 1000 -W 1 -w captura_wlan.pcap", shell=True)
        print("Captura finalizada")
    else:
        print("Cancelado por el usuario")

def lanzaws():
    if os.path.isfile('captura_eth.pcap'):
        subprocess.call("sudo wireshark captura_eth.pcap", shell=True)
    if os.path.isfile('captura_wlan.pcap'):
        subprocess.call("sudo wireshark captura_wlan.pcap", shell=True)
    else:
        print("No existen capturas")
        
def peque():
    if messagebox.askyesno('IMPORTANTE', 'Esta operación reiniciará el sistema. ¿Desea continuar?', icon='warning' ) == True:
        subprocess.call("sudo sed -i -e 's/framebuffer_width=1280/framebuffer_width=320/;s/framebuffer_height=720/framebuffer_height=240/' /boot/config.txt", shell=True)
        print("Resolución cambiada")
        subprocess.call("sudo reboot", shell=True)
        win.destroy()        
    else:
        print("Cancelado por el usuario")

def grande():
    if messagebox.askyesno('IMPORTANTE', 'Esta operación reiniciará el sistema. ¿Desea continuar?', icon='warning' ) == True:
        subprocess.call("sudo sed -i -e 's/framebuffer_width=320/framebuffer_width=1280/;s/framebuffer_height=240/framebuffer_height=720/' /boot/config.txt", shell=True)
        print("Resolución cambiada")
        subprocess.call("sudo reboot", shell=True)
        win.destroy()
    else:
        print("Cancelado por el usuario")
   
exitButton  = Button(win, text = "Exit", command = exitProgram, height =2 , width = 6)
exitButton.grid(row=5, column=0)

scan_wifi = Button(pestaña1, text = "BUSCAR REDES", command = buscarredes,  height = 2, width =10 )
scan_wifi.grid(row=0, column=0)

IPprivada = Button(pestaña4, text = "IP PRIVADA", command = ipprivada,  height = 2, width =10 )
IPprivada.grid(row=0, column=0)

IPpublica = Button(pestaña4, text = "IP PUBLICA", command = ippublica,  height = 2, width =10 )
IPpublica.grid(row=0, column=1)

test_connect = Button(pestaña4, text = "¿CONEXION?", command = testconnect,  height = 2, width = 10 )
test_connect.grid(row=0, column=2)

hosts_activo = Button(pestaña2, text = "HOSTS ACTIVOS", command = hostsactivos,  height = 2, width = 12)
hosts_activo.grid(row=0, column=0)

hosts_activo = Button(pestaña2, text = "BUSCAR SERVICIOS", command = servicios,  height = 2, width = 12 )
hosts_activo.grid(row=0, column=1)

captura1 = Button(pestaña3, text = "CAPTURA ETH0", command = capturaeth,  height = 2, width =10 )
captura1.grid(row=0, column=0)

captura2 = Button(pestaña3, text = "CAPTURA WLAN0", command = capturawlan,  height = 2, width =10 )
captura2.grid(row=1, column=0)

lanzawireshark = Button(pestaña3, text = "ABRE CAPTURA", command = lanzaws,  height = 2, width =10 )
lanzawireshark.grid(row=0, column=1, rowspan=2)

captura2 = Button(pestaña5, text = "320x240", command = peque,  height = 2, width =10 )
captura2.grid(row=1, column=0)

captura2 = Button(pestaña5, text = "1280x720", command = grande,  height = 2, width =10 )
captura2.grid(row=1, column=1)


wifi_text = tkst.ScrolledText(pestaña1, width=30, height=8)
wifi_text.grid(row=1, column=0)

privada_text = Text(pestaña4, width=15, height=2)
privada_text.grid(row=1, column=0)

ip_text = Text(pestaña4, width=15, height=2)
ip_text.grid(row=1, column=1)

test_text = Text(pestaña4, width=15, height=2)
test_text.grid(row=1, column=2)

activos_text = tkst.ScrolledText(pestaña2, width=20, height=8)
activos_text.grid(row=1, column=0)

win.mainloop()

