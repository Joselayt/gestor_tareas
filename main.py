import tkinter.ttk as ttk
from tkinter import *
import os
from tkinter import messagebox
import datetime
import random
import json
import threading
import queue
import time
import pygame
import sys


class app:

    def __init__(self):
        pygame.init()

        self.root = None
        self.p = None
        self.id = 1
        self.num_tareas = 0
        self.notificando = False
        self.tareas = None
        self.tareaS = None
        self.tareaSS = None
        
        self.cola = queue.Queue()
        self.T = threading.Event()
        self.starting = True
        self.tareas_notificadas = set()

        try:
            self.ruta = sys._MEIPASS
        except:
            self.ruta = "./"

        self.audio = pygame.mixer.Sound(os.path.join(self.ruta, 'audio.wav'))
        self.archivo = os.path.join(self.ruta, "tareas.txt")
        with open(os.path.join(self.ruta, 'mensajes.json'), "r", encoding="utf-8") as j:
            self.mensajes = json.load(j)
        

        hilo_hablar = threading.Thread(target=self.text_to_speech, daemon=True)
        hilo_hablar.start()
        self.loop()

    def loop(self):

        self.root = Tk()
        self.root.iconbitmap(bitmap=os.path.join(self.ruta, 'icono.ico'))
        self.root.title('Gestor de tareas')
        self.root.resizable(False, False)
        self.tareaS = StringVar()

        titulo = Label(self.root, text='Gestor de tareas', font=('cambria', 30, 'bold'), fg="#1E1E2E")
        titulo.grid(row=0, column=0, pady=20, padx=20)

        proximo_label = Label(self.root, text="Proxima tarea", relief="groove", font=('gelvetica', 20, 'bold'), fg="#3E3E1E")
        proximo_label.grid(row=1, column=0, padx=20)

        proximo = Label(self.root, textvariable=self.tareaS, font=('gelvetica', 12, 'bold'), fg="maroon", relief="flat")
        proximo.grid(row=2, column=0)


        columnas = ('hora', 'tarea', 'estado')
        style = ttk.Style()
        style.configure(
            'tareas.Treeview',
            background="#1E1E2E",
            foreground="#FFFFFF",
            rowheight=30
        )

        self.p = ttk.Treeview(self.root, columns=columnas, show="headings", style="tareas.Treeview")
        self.p.heading('hora', text="Hora")
        self.p.heading('tarea', text="Tarea")
        self.p.heading('estado', text="Estado")

        self.p.column('hora', width=100, anchor="center")
        self.p.column('tarea', width=300)
        self.p.column('estado', width=120, anchor="center")

        self.p.grid(row=3, column=0, pady=10, padx=10, ipady=5, ipadx=5)

        # botones

        crear = Button(self.root, text="Crear", bg="spring green", width=8, relief="groove", font=('cambria', 16, 'bold'), command=lambda:self.creacion())
        crear.grid(row=4, column=0, sticky="w", pady=10, padx=10, ipady=5, ipadx=5)
        administrar = Button(self.root, text="Administrar", bg="violet red", width=8, relief="flat", font=('cambria', 16), command=lambda: self.admin())
        administrar.grid(row=4, column=0, pady=10, padx=10, ipady=5, ipadx=5)

        self.root.after(2000, self.verificar_tareas)
        self.root.after(3000, self.tarea_proxima)
        self.root.after(4000, self.entrada)

        self.root.mainloop()
    
    def entrada(self):
        mañana_inicio = "6:00"
        mañana_final = "12:59"
        tarde_inicio = "13:00"
        tarde_final = "23:59"
        ahora = datetime.datetime.now()

        horas = [ahora.replace(hour=datetime.datetime.strptime(c, "%H:%M").hour, minute=datetime.datetime.strptime(c, "%H:%M").minute, second=0, microsecond=0) for c in [mañana_inicio, mañana_final, tarde_inicio, tarde_final]]
        m_i, m_f, t_i, t_f = horas

        if m_i <= ahora <= m_f:
            txt = random.choice(self.mensajes['saludos']['manana'])
        else:
            txt = random.choice(self.mensajes['saludos']['tarde'])
        
        self.cola.put(txt)


    def text_to_speech(self):

        import pyttsx3


        
        while not self.T.is_set():

            if not self.cola.empty():
                model = pyttsx3.Engine()
                voces = model.getProperty('voices')
                voz = None
                for voz_ in voces:
                    for c in str(voz_).split("\n"):
                        if "languages" in c.lower():
                            if "es-ES" in c:
                                voz = voz_
                if voz is not None:
                    model.setProperty('voice', voz.id)
                model.setProperty('rate', 130)
                texto =  self.cola.get()
                model.say(texto)
                model.runAndWait()
                self.cola.task_done()
            
            time.sleep(1)

    
    def tarea_proxima(self):

        datos = []
        if self.tareas is not None:
            try:
                
                with open(self.archivo, "r", encoding="utf-8") as t:
                    for linea in t.read().split('\n'):                        
                        datos.append(linea.split('|'))
                if datos != []:
                    new_datos = []
                    for dato in datos:
                        try:
                            hora = dato[3]
                        except:
                            continue
                        ahora = datetime.datetime.now()
                        hora = datetime.datetime.strptime(hora, "%d-%m-%Y %H:%M")
                        # hora = ahora.replace(hour=hora.hour, minute=hora.minute, second=0, microsecond=0)

                        dato[3] = hora
                        new_datos.append(dato)
                    
                    todos = list(map(lambda x: x[3]-datetime.datetime.now(), new_datos))
                    menos = min(todos)
                    menos = new_datos[todos.index(menos)]
                    self.tareaS.set(f"Próxima tarea {'es para hoy' if menos[3].day == datetime.datetime.now().day else 'será para mañana'}: {', '.join([c.strftime('%d-%m-%Y %H:%M') if isinstance(c, datetime.datetime) else c for c in menos][-3:])}")
                if self.starting:
                    self.cola.put(random.choice(self.mensajes['notificaciones']['recordatorio']))
                    self.cola.put(f"Próxima tarea {'es para hoy' if menos[3].day == datetime.datetime.now().day else 'será para mañana'}: {', '.join([c.strftime('%d-%m-%Y %H:%M') if isinstance(c, datetime.datetime) else c for c in menos][-3:])}")
                    self.starting = False
            except:
                self.tareas = None
        else:
            self.tareaS.set('No tienes ninguna tarea pendiente. ¡Porque no agregas una ahora!')
            if self.starting:
                self.cola.put('No tienes ninguna tarea pendiente. ¡Porque no agregas una ahora!')
                self.starting = False

        self.root.after(1000, self.tarea_proxima)



    def creacion(self):

        root = Toplevel()
        root.iconbitmap(bitmap=os.path.join(self.ruta, 'icono.ico'))
        root.resizable(False, False)
        titulo = Label(root, text="Crear tarea", relief="flat", font=('gelvetica', 20, 'bold'), fg="#3E3E1E")
        titulo.grid(row=0, column=0, padx=20, pady=20)

        self.tareaSS = StringVar()

        frecuencia = ttk.Combobox(root, font=('cambria', 14, 'bold'), values=('Solo esta vez', 'Todos los dias'), state="readonly")
        frecuencia.set('Solo esta vez')
        frecuencia.grid(row=1, column=0, padx=8, pady=8)

        tarea = Entry(root, font=('cambria', 14, 'bold'), textvariable=self.tareaSS)
        tarea.insert(END, '¿Cual es la tarea?')
        tarea.config(state="disable")
        tarea.grid(row=2, column=0, padx=8, pady=8)
        def pul(event):
            tarea.config(state="normal")
            tarea.delete(0, END)

        tarea.bind('<Button-1>', pul)

        hora = ttk.Combobox(root, values=[i for i in range(0, 24)], width=10, font=('cambria', 12))
        hora.grid(row=3, column=0, sticky="w")
        hora.insert(0, 'Elija la hora')
        hora.config(state="readonly")

        minuto = ttk.Combobox(root, values=[i for i in range(0, 60)], width=10, font=('cambria', 12))
        minuto.grid(row=3, column=0, sticky="e")
        minuto.insert(0, 'Elija minutos')
        minuto.config(state="readonly")

        crear = Button(root, text="Crear", relief="groove", font=('cambria', 14, 'bold'), fg="spring green", bg="#1E1E2E", command=lambda: self.guardar_tarea(frecuencia.get(), self.tareaSS.get().capitalize(), hora.get(), minuto.get()))
        crear.grid(row=4, column=0)
        root.mainloop()

    def admin(self):

        if self.tareas is not None:
            root_admin = Toplevel(self.root)
            root_admin.iconbitmap(bitmap=os.path.join(self.ruta, 'icono.ico'))

            # root_admin.configure(background="black")
            root_admin.resizable(False, False)
            column = 0
            for row, tarea in enumerate(self.tareas):
                prompt= f"{'Todos los dias' if tarea[1] == 'todos los dias' else 'Hoy'}, a las {tarea[3]} tienes {tarea[2]}"    
                Label(root_admin, text=prompt, foreground="#1E1E1E", font=('cambria', 14, 'bold')).grid(row=row, column=column, padx=5, pady=5, ipadx=5, ipady=5)
                Button(root_admin, text="Modificar", foreground="blue", font=('cambria', 12, 'bold'), command=lambda x=tarea: self.eliminar(x, accion="modificar")).grid(row=row, column=column+1, padx=5, pady=5, ipadx=5, ipady=5)
                Button(root_admin, text="Eliminar", foreground="red", font=('cambria', 12, 'bold'), command=lambda x=tarea: self.eliminar(x, ventana=root_admin)).grid(row=row, column=column+2, padx=5, pady=5, ipadx=5, ipady=5)

            root_admin.mainloop()

    def eliminar(self, data_o_nombre, accion="eliminar", ventana=None):
        
        def mod_(freq, tar, hor, min_, id_, ventana):
            if tar.strip() == "¿Cual es la tarea?" or tar.strip() == "":
                self.notificacion("Lo siento, no puedo crear una tarea sin tarea")
                self.cola.put("Lo siento, no puedo crear una tarea sin tarea")

                return

            if hor.lower().strip() == "elija la hora" or hor.lower().strip() == "" or min_.lower().strip() == "elija minutos":
                self.notificacion("Lo siento, no puedo crear una tarea sin la hora y los minutos establecidos")
                self.cola.put("Lo siento, no puedo crear una tarea sin la hora y los minutos establecidos")

                return 

            tiempo = datetime.datetime.now()
            tiempo = tiempo.replace(hour=int(hor), minute=int(min_), second=0, microsecond=0)

            if not self.quitar_tarea_funcion(id_, ventana):
                self.notificacion('Lo siento, creo que ha habido un error al intentar eliminar esa tarea')
                self.cola.put('Lo siento, creo que ha habido un error al intentar eliminar esa tarea')

                return

            self.registrar_tarea_archivo(freq, tar, tiempo, "pendiente")

            ventana.destroy()


        if accion != "eliminar":
            root_modif = Toplevel(self.root)
            root_modif.iconbitmap(bitmap=os.path.join(self.ruta, 'icono.ico'))

            root_modif.title('Modificar')
            root_modif.resizable(False, False)
            Label(root_modif, text=f"Antes: {data_o_nombre[2]}, A las {data_o_nombre[3]}, {data_o_nombre[1]}", background="#1E1E2E", foreground="#FFFFFF", font=('cambria', 14, 'bold')).grid(row=0, column=0)
            frecuencia = ttk.Combobox(root_modif, font=('cambria', 14, 'bold'), values=('Solo esta vez', 'Todos los dias'), state="readonly")
            frecuencia.set('Solo esta vez')
            frecuencia.grid(row=1, column=0, padx=8, pady=8)

            tarea = Entry(root_modif, font=('cambria', 14, 'bold'))
            tarea.insert(END, '¿Cual es la tarea?')
            tarea.config(state="disable")
            tarea.grid(row=2, column=0, padx=8, pady=8)
            def pul(event):
                tarea.config(state="normal")
                tarea.delete(0, END)

            tarea.bind('<Button-1>', pul)

            hora = ttk.Combobox(root_modif, values=[i for i in range(0, 24)], width=10, font=('cambria', 12))
            hora.grid(row=3, column=0, sticky="w")
            hora.insert(0, 'Elija la hora')
            hora.config(state="readonly")

            minuto = ttk.Combobox(root_modif, values=[i for i in range(0, 60)], width=10, font=('cambria', 12))
            minuto.grid(row=3, column=0, sticky="e")
            minuto.insert(0, 'Elija minutos')
            minuto.config(state="readonly")

            mod = Button(root_modif, text="Modificar", relief="groove", font=('cambria', 14, 'bold'), fg="spring green", bg="#1E1E2E", command=lambda: mod_(frecuencia.get(), tarea.get(), hora.get(), minuto.get(), data_o_nombre[0], root_modif))
            mod.grid(row=4, column=0)

        else:
            if self.quitar_tarea_funcion(data_o_nombre[0], ventana=ventana):
                self.notificacion('La tarea ha sido eliminada', tipo="info")
                self.cola.put('La tarea ha sido eliminada')
    
    def quitar_tarea_funcion(self, id_, ventana):

        datos = []
        with open(self.archivo, "r", encoding="utf-8") as t:
            for linea in t.read().split('\n'):
                try:
                    if int(linea.split("|")[0]) == int(id_):
                        continue
                except:
                    continue
                    
                datos.append(linea.split('|'))
        with open(self.archivo, "w", encoding="utf-8") as t:
            for d in datos:
                t.write("|".join(d) + "\n")
        try:
            self.tareas_notificadas.remove(id_)
        except:
            pass
        
        ventana.destroy()
        return True
        

    
    def guardar_tarea(self, freq, tar, hor, min_):
        
        if tar.strip() == "¿Cual es la tarea?" or tar.strip() == "":
            self.notificacion("Lo siento, no puedo crear una tarea sin tarea")
            self.cola.put("Lo siento, no puedo crear una tarea sin tarea")

            return

        if hor.lower().strip() == "elija la hora" or hor.lower().strip() == "" or min_.lower().strip() == "elija minutos":
            self.notificacion("Lo siento, no puedo crear una tarea sin la hora y los minutos establecidos")
            self.cola.put("Lo siento, no puedo crear una tarea sin la hora y los minutos establecidos")

            return 

        tiempo = datetime.datetime.now()
        tiempo = tiempo.replace(hour=int(hor), minute=int(min_), second=0, microsecond=0)

        self.registrar_tarea_archivo(freq, tar, tiempo, "pendiente")
        return
        

    def registrar_tarea_archivo(self, *args):

        if not os.path.exists(self.archivo):
            with open(self.archivo, "w", encoding="utf-8") as t:
                pass

        with open(self.archivo, "a", encoding="utf-8") as t:
            t.write(f'{self.id}|{"|".join([c.strftime("%d-%m-%Y %H:%M") if isinstance(c, datetime.datetime) else c for c in args])}\n')

        self.id += 1
        self.notificacion('Nueva tarea registrada', tipo="info")
        self.cola.put(random.choice(self.mensajes['notificaciones']['nueva_tarea']))

        return

    def verificar_tareas(self):
        tareas = []
        

        self.p.delete(*self.p.get_children())
        if os.path.exists(self.archivo):

            with open(self.archivo, "r", encoding="utf-8") as t:
                for linea in t.read().split('\n'):
                    if linea.strip() == "":
                        continue
                    id, frecuencia, tarea, hora, estado = linea.split('|')
                    self.p.insert('', END, values=(hora, tarea.capitalize(), estado))
                    tareas.append((id, frecuencia, tarea, hora, estado))
                ids = [c[0] for c in tareas]
                try:
                    self.id = int(ids[-1]) + 1
                except:
                    pass
            
            for tarea in tareas:
                id_, _, t, h, e = tarea
                hora = datetime.datetime.strptime(h, '%d-%m-%Y %H:%M')
                ahora = datetime.datetime.now()
                # hora = ahora.replace(year=hora.year, month=hora.month, day=hora.day, hour=hora.hour, minute=hora.minute, second=0, microsecond=0)

                if datetime.datetime.now() >= hora and id_ not in self.tareas_notificadas:
                    self.tareas_notificadas.add(id_)
                    self.notificacion(f'¡Hola!, \nen este momento \ntienes una tarea:\n· {"hoy" if datetime.datetime.strptime(h.split()[0], "%d-%m-%Y").day == datetime.datetime.now().day else "mañana"} A las: {h.split()[-1]}\n·Tienes: {t}', tipo="ventana", id=id_)
                    self.audio.play()
                    self.root.after(4000)
                    self.cola.put(f'¡Hola!, \nen este momento \ntienes una tarea:\n· {"hoy" if datetime.datetime.strptime(h.split()[0], "%d-%m-%Y").day == datetime.datetime.now().day else "mañana"} A las: {h.split()[-1]}\n·Tienes: {t}')

            self.tareas = tareas
        self.root.after(2000, self.verificar_tareas)
            

        

    def notificacion(self, text, tipo="error", id=None):

        def cerrar(id_, ventana):
            self.notificando = False
            datos = []
            with open(self.archivo, "r", encoding="utf-8") as t:

                for linea in t.read().split('\n'):
                    if linea.strip() == "":
                        continue
                    try:
                        if int(linea.split("|")[0]) == int(id_):
                            if linea.split('|')[1].lower().strip() == "solo esta vez":
                                continue
                            else:
                                linea = linea.split('|')
                                manana = datetime.datetime.now() + datetime.timedelta(days=1)
                                nueva_fecha = datetime.datetime(manana.year, manana.month, manana.day, manana.hour, manana.minute, 0, 0).strftime('%d-%m-%Y %H:%M')
                                linea[3] = nueva_fecha
                                linea = "|".join([c for c in linea if c.strip() != ""])
                    except:
                        continue
                        
                    datos.append(linea.split('|'))
            with open(self.archivo, "w", encoding="utf-8") as t:
                for d in datos:
                    t.write("|".join(d) + "\n")

            self.cola.put(random.choice(self.mensajes['notificaciones']['tarea_completada']))
            self.tareas_notificadas.remove(id_)

            ventana.destroy()
        
        def posponer(id_, hor,min, ventana):
            self.notificando = False
            datos = []
            new_hora = hor
            new_minuto = min
            try:
                nueva_hora = datetime.datetime.now().replace(hour=int(new_hora), minute=int(new_minuto), second=0, microsecond=0).strftime('%d-%m-%Y %H:%M')
            except:
                self.notificacion('Porfavor, revise otra vez la informacion que introdujo e intentelo de nuevo')
                self.cola.put('Porfavor, revise otra vez la informacion que introdujo e intentelo de nuevo')

                return
            if os.path.exists(self.archivo):
                with open(self.archivo, "r", encoding="utf-8") as t:
                    for linea in t.read().split('\n'):
                        if linea.strip() == "":
                            continue
                        id, frecuencia, tarea, hora, estado = linea.split('|')
                        
                        if id == id_:
                            hora = nueva_hora

                        datos.append((id, frecuencia, tarea, hora, estado))

                with open(self.archivo, "w", encoding="utf-8") as t:
                    for dato in datos:
                        t.write("|".join(dato) + "\n")
                self.tareas_notificadas.remove(id_)
                self.cola.put('Acabas de posponer una tarea')

            else:
                self.notificacion('No detecto ningun archivo para modificar', tipo="error")
                self.cola.put('No detecto ningun archivo para modificar')
            
            ventana.destroy()

        if tipo == "error":
            messagebox.showerror(title="Error", message=text)
            return 

        elif tipo == "info":
            messagebox.showinfo(title="Info", message=text)
            return 

        if not self.notificando:
        
            self.notificando = True

            t = Toplevel(self.root)
            t.iconbitmap(bitmap=os.path.join(self.ruta, 'icono.ico'))

            t.resizable(False, False)
            t.geometry('250x250')
            t.title('Hora de hacer una tarea')
            t.attributes('-topmost', True)
            t.protocol('WM_DELETE_WINDOW', lambda: None)

            Label(t, text=text, font=('gelvetica', 14, 'bold'), fg="#3E3E3E").pack()
            Button(t, text="¡Cumplida!", command=lambda: cerrar(id, t), width=8, relief="flat", bg="spring green", fg="#1E1E1E").pack()

            new_hora = ttk.Combobox(t, values=[i for i in range(0, 24)], width=10, font=('cambria', 12))
            new_hora.pack()
            new_hora.insert(0, 'Elija la hora')
            new_hora.config(state="readonly")

            new_minuto = ttk.Combobox(t, values=[i for i in range(0, 60)], width=10, font=('cambria', 12))
            new_minuto.pack()
            new_minuto.insert(0, 'Elija minutos')
            new_minuto.config(state="readonly")
            Button(t, text="Posponer", command=lambda: posponer(id, new_hora.get(), new_minuto.get(), t), width=8, relief="flat", fg="maroon").pack()

            
        return


app()