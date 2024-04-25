import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from tkinter import *
import webbrowser
from tkinter import ttk, font
from tkinter import filedialog
from tkinter import messagebox
from ttkthemes import ThemedTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Funciones de codificación de señales
def nrz_l(data, start_level):
    encoded = [start_level, start_level]
    for bit in data:
        encoded.extend([1 if bit == '0' else -1]*2)
    return encoded

def nrz_i(data, start_level):
    level = start_level
    encoded = [level, level]
    for bit in data:
        if bit == '1':
            level = -level
        encoded.extend([level]*2)
    return encoded

def manchester(data, start_level):
    encoded = []
    for bit in data:
        if bit == '1':
            encoded.extend([1, -1])
        else:
            encoded.extend([-1, 1])
    return encoded

def diff_manchester(data, start_level):
    level = start_level
    encoded = []
    for bit in data:
        if bit == '1':
            level = -level
        encoded.extend([level, -level])
    return encoded

# Función para trazar la señal
def plot_signal(signal, data, title, folder, manchester=False):
    plt.style.use(var_style.get())
    signal.append(signal[-1])
    fig = plt.figure(figsize=(len(signal)/4, 5))
    plt.step(np.arange(1, len(signal)/2 + 1, 0.5), signal, where='post')
    for i, bit in enumerate(data):
        plt.text(i + 2.5 if not manchester else i+1.5,-2, bit, ha='center')
    plt.title(title)
    plt.ylim(-2.5, 2.5)
    plt.yticks(range(-2, 3))
    plt.xticks(np.arange(0, len(signal)/2 + 2, 1))
    plt.grid(True)
    fig.tight_layout()
    return fig

# Función para guardar la imagen
def save_image():
    global fig
    if fig is None:
        messagebox.showerror("Error", "No hay gráfico para guardar.")
        return
    data = e1.get("1.0", END).strip()
    method = var.get()
    default_filename = f"{method}-{data}"
    filepath = filedialog.asksaveasfilename(defaultextension=".png", initialfile=default_filename, filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg"), ("EPS files", "*.eps")])
    if not filepath:
        return
    fig.savefig(filepath)

# Función para dibujar la señal
def draw():
    global canvas, fig
    data = e1.get("1.0", END).strip()
    if not set(data).issubset({'0', '1'}):
        messagebox.showerror("Error", "Los datos deben ser una secuencia de ceros y unos.")
        return
    method = var.get()
    if method not in ['NRZ-L', 'NRZ-I', 'Manchester', 'Manchester Diferencial']:
        messagebox.showerror("Error", "El método seleccionado no es válido.")
        return
    start_level = 1 if var_start.get() == "Arriba" else -1
    if start_level not in [1, -1]:
        messagebox.showerror("Error", "El nivel de inicio seleccionado no es válido.")
        return
    if method == 'NRZ-L':
        fig = plot_signal(nrz_l(data, start_level), data, f'NRZ-L {data}', 'NRZ-L')
    elif method == 'NRZ-I':
        fig = plot_signal(nrz_i(data, start_level), data, f'NRZ-I {data}', 'NRZ-I')
    elif method == 'Manchester':
        fig = plot_signal(manchester(data, start_level), data, f'Manchester {data}', 'Manchester', manchester=True)
    elif method == 'Manchester Diferencial':
        fig = plot_signal(diff_manchester(data, start_level), data, f'Manchester Diferencial {data}', 'Manchester Diferencial', manchester=True)
    canvas.get_tk_widget().pack_forget()
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    option_style.pack(side=TOP, anchor=E)

# Función para cerrar la aplicación
def on_closing():
    root.destroy()
    os._exit(0)

# Inicialización de variables globales
fig = None

# Configuración de la ventana principal
root = ThemedTk(theme="arc")
root.title("Generador de señales")
root.geometry("1000x350")
root.minsize(800, 350)

# Configuración del icono de la aplicación
try:
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            icon_path = os.path.join(sys._MEIPASS, 'icono.ico')
        elif sys.platform == 'darwin':
            icon_path = os.path.join(sys._MEIPASS, 'icono.icns')
        else:
            icon_path = os.path.join(sys._MEIPASS, 'icono.xpm')
    else:
        if sys.platform == 'win32':
            icon_path = 'icono.ico'
        elif sys.platform == 'darwin':
            icon_path = 'icono.icns'
        else:
            icon_path = 'icono.xpm'
    root.iconbitmap(icon_path)
except Exception:
    pass  # Si no se puede establecer el icono, simplemente lo ignoramos y continuamos

# Configuración del estilo de la aplicación
style = ttk.Style()
style.theme_use('clam')

# Configuración del marco principal
frame = Frame(root)
frame.grid(row=0, column=0, sticky=N+S, padx=20, pady=20)

# Configuración de los widgets de entrada
Label(frame, text="Tipo de onda:").grid(row=0, column=0, padx=10, sticky=W)
var = StringVar(root)
var.set("NRZ-L")
option = ttk.Combobox(frame, textvariable=var, values=["NRZ-L", "NRZ-I", "Manchester", "Manchester Diferencial"], state='readonly')
option.grid(row=1, column=0, padx=10, sticky=W)

Label(frame, text="Nivel de inicio:").grid(row=2, column=0, padx=10, sticky=W)
var_start = StringVar(root)
var_start.set("Arriba")
option_start = ttk.Combobox(frame, textvariable=var_start, values=["Arriba", "Abajo"], state='readonly')
option_start.grid(row=3, column=0, padx=10, sticky=W)

bigfont = font.Font(size=12)

Label(frame, text="Datos:").grid(row=4, column=0, padx=10, sticky=W)
e1 = Text(frame, height=1, width=20, font=bigfont)
e1.grid(row=5, column=0, padx=10, pady=(10, 0), sticky=N+S)

# Configuración de los botones
b = Button(frame, text="Dibujar", command=draw, font=bigfont, width=20)
b.grid(row=6, column=0, padx=10, pady=10)

b2 = Button(frame, text="Exportar imagen", command=save_image, font=bigfont, width=20)
b2.grid(row=7, column=0, padx=10, pady=10)

# Configuración del canvas
canvas = FigureCanvasTkAgg(plt.figure(), master=root)
canvas.get_tk_widget().grid(row=0, column=1, sticky=N+S+E+W)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

canvas_frame = Frame(root)
canvas_frame.grid(row=0, column=1, sticky=N+S+E+W)

var_style = StringVar(root)
var_style.set("default")
option_style = ttk.Combobox(canvas_frame, textvariable=var_style, values=plt.style.available, state='readonly')
option_style.pack(side=TOP, anchor=E)

canvas = FigureCanvasTkAgg(plt.figure(), master=canvas_frame)
canvas.get_tk_widget().pack(fill=BOTH, expand=True)

root.protocol("WM_DELETE_WINDOW", on_closing)

mainloop()