import tkinter
import gc
from tkinter import *
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)
from matplotlib.backend_bases import button_press_handler
from matplotlib import pyplot as plt, figure, animation
import numpy as np
import matplotlib as mpl
from numpy.random import randint

mpl.use('Agg')
plt.rcParams["font.family"] = "Times New Roman"

class Game(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry("1680x720")
        self.resizable(False, False)
        self.configure(bg='black')

        self.container = Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.phases = {}
        self.create_frame(StartPage)

        self.function = []
        self.playerRecords = []
        self.machineRecords = []

    def create_frame(self, F):
        name = F.__name__
        frame = F(parent=self.container, root=self)
        self.phases[name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.fadein()
        frame.tkraise()

    def start_game(self):
        self.function = self.defineFunction()
        self.create_frame(Player)

    def defineFunction(self):
        x = np.linspace(0,20,1000)
        y = -0.05*((x-10)**2)+2.5
        return y

    def check_result(self):
        self.create_frame(ResultPage)


class StartPage(Frame):
    def __init__(self, parent, root):
        Frame.__init__(self, parent)
        self.root = root
        self.alpha = 0.0
        self.run = True

        self.fig = plt.Figure(figsize=(16.8,7.2), dpi=100) # figure = screen
        self.fig.patch.set_facecolor('black')

        self.ax = self.fig.add_subplot(xlim=(0,10),ylim=(-2,4.5)) # ax = full graph. graph is inside screen
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.ax.set_facecolor('black')
        self.ax.set_position([0, 0, 1, 1]) # position and size of graph inside screen : coordinates [0,1]x[0,1], so fullscreen

        self.line, = self.ax.plot([], [], lw=2) # include line in graph
        self.line.set_color('turquoise')
        self.line.set_alpha(self.alpha)

        self.title = self.ax.text(5, 3, "Find the Highest", fontsize=150, color='white') # include text in graph : coordinates [0,10]x[-2,2]
        self.title.set_horizontalalignment('center')
        self.title.set_verticalalignment('center')
        self.title.set_alpha(self.alpha)

        self.subtitle = self.ax.text(5, 2, "Click Anywhere to Play", fontsize=30, color='white')
        self.subtitle.set_horizontalalignment('center')
        self.subtitle.set_verticalalignment('center')
        self.subtitle.set_alpha(self.alpha)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root) # connect tkinter canvas with pyplot figure
        self.canvas.mpl_connect("button_press_event", lambda e : self.fadeout()) # listener of canvas
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init, frames=1000, interval=20, blit=True)

    def fadein(self):
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        if self.alpha < 1:
            self.alpha = min(self.alpha+0.1, 1)
            self.line.set_alpha(self.alpha)
            self.title.set_alpha(self.alpha)
            self.subtitle.set_alpha(self.alpha)
            self.after(50, self.fadein)

    def fadeout(self):
        self.canvas.mpl_disconnect("button_press_event")
        if self.alpha > 0:
            self.alpha = max(self.alpha-0.1, 0)
            self.line.set_alpha(self.alpha)
            self.title.set_alpha(self.alpha)
            self.subtitle.set_alpha(self.alpha)
            self.after(50, self.fadeout)
        else:
            self.root.start_game()
            self.canvas.get_tk_widget().pack_forget()
            self.line = None

    def init(self):
        return self.line, self.title, self.subtitle

    def animate(self, i):
        x = np.linspace(0, 10, 1000)
        y = (2.3*np.sin(12*(x+0.001*i))+1.4*np.cos(5*(x+0.004*i))+0.7*np.sin(16*(x+0.003*i)))/3
        self.line.set_data(x, y)
        return self.line, self.title, self.subtitle



class Player(Frame):
    def __init__(self, parent, root):
        print("I am new Player")
        Frame.__init__(self, parent)
        self.root = root
        self.root.bind('<Motion>', self.track) # mouse motion listener
        self.func = []
        self.entries = []
        self.alpha = 0.0
        self.x = 0          # 0~999

        self.fig = plt.Figure(figsize=(16.8,7.2), dpi=100)
        self.fig.patch.set_facecolor('black')

        self.ax = self.fig.add_subplot(xlim=(0,20),ylim=(-5,5))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.ax.set_facecolor('black')
        self.ax.set_position([0, 0, 1, 1])

        self.guide, = self.ax.plot([], [], lw=3, ls='--') # include line in graph
        self.guide.set_color('yellow')
        self.candidates = self.ax.scatter([], [], s=150, marker='+', lw=3) # chosen candidates in graph

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init, frames=1000, interval=20, blit=True)

    def __del__(self):
        print("I am dying")

    def track(self, event):
        self.x = event.x
        self.x = int(self.x*1000.0/1680.0)

    def fadein(self):
        if self.alpha < 1:
            self.alpha = min(self.alpha+0.1, 1)
            self.guide.set_alpha(self.alpha)
            self.candidates.set_alpha(self.alpha)
            self.after(50, self.fadein)
        else:
            self.func = self.root.function
            self.entries = []
            self.canvas.mpl_connect("button_press_event", lambda e : self.onclick())

    def onclick(self):
        self.entries.append(self.x)
        if len(self.entries) == 20:
            self.fadeout()

    def fadeout(self):
        self.canvas.mpl_disconnect("button_press_event")
        if self.alpha > 0:
            self.alpha = max(self.alpha-0.1, 0)
            self.guide.set_alpha(self.alpha)
            self.candidates.set_alpha(self.alpha)
            self.after(50, self.fadeout)
        else:
            self.root.playerRecords = self.entries.copy()
            self.root.create_frame(Machine)
            self.canvas.get_tk_widget().pack_forget()
            self.guide = None

    def init(self):
        return self.guide, self.candidates,

    def animate(self, i):
        x = [self.x/50, self.x/50]
        y = [-5, 5]
        self.guide.set_data(x, y)
        if len(self.entries) != 0:
            X = np.array([0.02*i for i in self.entries])
            Y = np.array([self.func[i] for i in self.entries])
            scale = (Y+4.0)/8.0
            self.candidates.set_offsets(np.vstack((X,Y)).T)
            self.candidates.set_edgecolors(plt.cm.coolwarm(scale))
        return self.guide, self.candidates,



class Machine(Frame):
    def __init__(self, parent, root):
        print("I am new Machine")
        Frame.__init__(self, parent)
        self.root = root
        self.func = []
        self.predict = []
        self.entries = []
        self.alpha = 0.0
        self.x = 500
        self.i = 0

        self.fig = plt.Figure(figsize=(16.8,7.2), dpi=100)
        self.fig.patch.set_facecolor('black')

        self.ax = self.fig.add_subplot(xlim=(0,20),ylim=(-5,5))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.ax.set_facecolor('black')
        self.ax.set_position([0, 0, 1, 1])

        self.guide, = self.ax.plot([], [], lw=2, ls='--') # include line in graph
        self.guide.set_color('yellow')
        self.candidates = self.ax.scatter([], [], s=150, marker='o', lw=0) # chosen candidates in graph

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init, frames=1000, interval=20, blit=True)


    def fadein(self):
        self.anim.event_source.start()
        if self.alpha < 1:
            self.alpha = min(self.alpha+0.1, 1)
            self.guide.set_alpha(self.alpha)
            self.candidates.set_alpha(self.alpha)
            self.after(50, self.fadein)
        else:
            self.func = self.root.function
            self.entries = self.bayesOptim()
            self.x, self.i = 500, 0

    def bayesOptim(self):
        results = [50+i for i in range(20)]
        return results

    def fadeout(self):
        if self.alpha > 0:
            self.alpha = max(self.alpha-0.1, 0)
            self.guide.set_alpha(self.alpha)
            self.candidates.set_alpha(self.alpha)
            self.after(50, self.fadeout)
        else:
            self.root.machineRecords = self.entries.copy()
            self.root.check_result()
            self.canvas.get_tk_widget().pack_forget()
            self.guide  = None
            self.grid_forget()
            self.destroy()

    def init(self):
        return self.guide, self.candidates,

    def animate(self, i):
        x = [self.x/50, self.x/50]
        y = [-5, 5]
        self.guide.set_data(x, y)
        if len(self.entries) != 0: self.move()
        if self.i != 0:
            X = np.array([0.02*i for i in self.entries[:self.i]])
            Y = np.array([self.func[i] for i in self.entries[:self.i]])
            scale = (Y+4.0)/8.0
            self.candidates.set_offsets(np.vstack((X,Y)).T)
            self.candidates.set_edgecolors(plt.cm.coolwarm(scale))
        return self.guide, self.candidates,

    def move(self):
        if self.i == 20: return
        if self.x > self.entries[self.i]+150: self.x -= 10
        elif self.x > self.entries[self.i]+50: self.x -= 6
        elif self.x > self.entries[self.i]+1: self.x -= 3
        elif self.x < self.entries[self.i]-150: self.x += 10
        elif self.x < self.entries[self.i]-50: self.x += 6
        elif self.x < self.entries[self.i]-1: self.x += 3
        else: self.i += 1
        if self.i == 20: self.fadeout()


class ResultPage(Frame):
    def __init__(self, parent, root):
        print("I am new Result")
        Frame.__init__(self, parent)
        self.root = root
        self.alpha = 0.0
        self.iteration = 0
        self.func = []
        self.pEntries = []
        self.mEntries = []

        self.fig = plt.Figure(figsize=(16.8,7.2), dpi=100) # figure = screen
        self.fig.patch.set_facecolor('black')

        self.ax = self.fig.add_subplot(xlim=(0,20),ylim=(-5,10)) # ax = full graph. graph is inside screen
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.ax.set_facecolor('black')
        self.ax.set_position([0, 0, 1, 1]) # position and size of graph inside screen : coordinates [0,1]x[0,1], so fullscreen

        self.line, = self.ax.plot([], [], lw=2) # include line in graph
        self.line.set_color('turquoise')
        self.line.set_alpha(self.alpha)

        self.title = self.ax.text(10, 7, "The Winner Is..   ", fontsize=130, color='white') # include text in graph : coordinates [0,20]x[-5,5]
        self.title.set_horizontalalignment('center')
        self.title.set_verticalalignment('center')
        self.title.set_alpha(self.alpha)

        self.subtitle = self.ax.text(10, 5.5, "Click Anywhere to Retry", fontsize=30, color='white')
        self.subtitle.set_horizontalalignment('center')
        self.subtitle.set_verticalalignment('center')
        self.subtitle.set_alpha(self.alpha)

        self.player = self.ax.scatter([], [], s=150, marker='+', lw=3) # chosen candidates in graph
        self.machine = self.ax.scatter([], [], s=150, marker='o', lw=0) # chosen candidates in graph

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root) # connect tkinter canvas with pyplot figure
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init, frames=2000, interval=20, blit=True)

    def fadein(self):
        if self.alpha < 1:
            self.alpha = min(self.alpha+0.1, 1)
            self.line.set_alpha(self.alpha)
            self.title.set_alpha(self.alpha)
            self.subtitle.set_alpha(self.alpha)
            self.player.set_alpha(self.alpha)
            self.machine.set_alpha(self.alpha)
            self.after(50, self.fadein)
        else:
            self.func = self.root.function
            self.pEntries = self.root.playerRecords
            self.mEntries = self.root.machineRecords
            self.canvas.mpl_connect("button_press_event", lambda e : self.fadeout())

    def init(self):
        return self.line, self.title, self.subtitle, self.player, self.machine

    def fadeout(self):
        if self.alpha > 0:
            self.alpha = max(self.alpha-0.1, 0)
            self.line.set_alpha(self.alpha)
            self.title.set_alpha(self.alpha)
            self.subtitle.set_alpha(self.alpha)
            self.player.set_alpha(self.alpha)
            self.machine.set_alpha(self.alpha)
            self.after(50, self.fadeout)
        else:
            self.pause = True
            self.root.start_game()
            self.canvas.get_tk_widget().pack_forget()
            self.line = None
            self.grid_forget()
            self.destroy()

    def animate(self, i):
        self.iteration += 1
        x = np.linspace(0, 20, 1000)
        y = self.func
        if len(y) == 0: x, y = [], []
        elif self.iteration <= 200:
            x, y = x[0:5*self.iteration], y[0:5*self.iteration]
        self.line.set_data(x,y)

        playerMax, machineMax = 0, 0
        if len(self.pEntries) != 0:
            X = np.array([0.02*i for i in self.pEntries])
            Y = np.array([self.func[i] for i in self.pEntries])
            scale = (Y+4.0)/8.0
            self.player.set_offsets(np.vstack((X,Y)).T)
            self.player.set_edgecolors(plt.cm.coolwarm(scale))
            playerMax = max(Y)

        if len(self.mEntries) != 0:
            X = np.array([0.02*i for i in self.mEntries])
            Y = np.array([self.func[i] for i in self.mEntries])
            scale = (Y+4.0)/8.0
            self.machine.set_offsets(np.vstack((X,Y)).T)
            self.machine.set_facecolors(plt.cm.coolwarm(scale))
            machineMax = max(Y)

        str = "AI" if machineMax > playerMax else "Player"
        self.title.set_text("The Winner is " + str)
        return self.line, self.title, self.subtitle, self.player, self.machine


if __name__ == "__main__":
    app = Game()
    app.mainloop()







