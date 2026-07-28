import tkinter as tk
import time, math

root = tk.Tk()
canvas = tk.Canvas(root, width=600, height=600, bg="white")
canvas.pack()

cx, cy, r = 150, 150, 120 # Centro do raio

canvas.create_oval(cx-r, cy-r, cx+r, cy+r, width=3)

def ponteiro(cx, cy, comprimento, angulo_graus):
    rad = math.radians(angulo_graus - 90)
    x = cx + comprimento * math.cos(rad)
    y = cy + comprimento * math.sin(rad)

    return x, y

def atualizar():
    canvas.delete('ponteiros')
    agora = time.localtime()
    ang_seg = agora.tm_sec * 6
    ang_min = agora.tm_min * 6 + agora.tm_sec * 0.1
    ang_hora = agora.tm_hour * 6 + agora.tm_min * 0.5

    for angulo, comprimento, largura in [
        (ang_hora, 60, 6),
        (ang_min, 90, 4),
        (ang_seg, 100, 2),
    ]: 
        x, y = ponteiro(cx, cy, comprimento, angulo)
        canvas.create_line(cx, cy, x, y, width=largura, tags='ponteiros')

        root.after(1000, atualizar)


    atualizar()
    root.mainloop()