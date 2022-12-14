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
import scipy
from scipy.stats import norm

mpl.use('Agg')
plt.rcParams["font.family"] = "Times New Roman"

class Game(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry("1680x720")
        self.resizable(False, False)
        self.configure(bg='black')
        self.title('Find the Highest')

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

    def check_result(self):
        self.create_frame(ResultPage)

    def defineFunction(self):
        x = np.expand_dims(np.linspace(0,20,1000),1)
        cov = 3.5*self.kernel_RBF(x,x) # Exponential Gaussian Kernel
        y = np.random.multivariate_normal(mean=np.zeros(1000), cov=cov, size=1).flatten()
        y += 0.5*np.cos(3*x.flatten())
        return y

    def kernel_RBF(self, xa, xb):
        sqnorm = -0.5*scipy.spatial.distance.cdist(xa, xb, 'sqeuclidean')
        return np.exp(sqnorm)



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

        self.title = self.ax.text(5, 3, "Find the Highest", fontsize=150, color='white') # include text in graph : coordinates [0,10]x[-2,2]
        self.title.set_horizontalalignment('center')
        self.title.set_verticalalignment('center')

        self.subtitle = self.ax.text(5, 2, "Click Anywhere to Play", fontsize=30, color='white')
        self.subtitle.set_horizontalalignment('center')
        self.subtitle.set_verticalalignment('center')

        self.setAlpha()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root) # connect tkinter canvas with pyplot figure
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init, frames=1000, interval=20, blit=True)

    def setAlpha(self):
        self.line.set_alpha(self.alpha)
        self.title.set_alpha(self.alpha)
        self.subtitle.set_alpha(self.alpha)

    def init(self):
        return self.line, self.title, self.subtitle

    def animate(self, i):
        x = np.linspace(0, 20, 1000)
        y = (2.3*np.sin(12*(x+0.001*i))+1.4*np.cos(5*(x+0.004*i))+0.7*np.sin(16*(x+0.003*i)))/3
        self.line.set_data(x, y)
        return self.line, self.title, self.subtitle

    def fadein(self):
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        if self.alpha < 1:
            self.alpha = min(self.alpha+0.1, 1)
            self.setAlpha()
            self.after(50, self.fadein)
        else:
            self.canvas.mpl_connect("button_press_event", lambda e : self.fadeout()) # listener of canvas

    def fadeout(self):
        self.canvas.mpl_disconnect("button_press_event")
        if self.alpha > 0:
            self.alpha = max(self.alpha-0.1, 0)
            self.setAlpha()
            self.after(50, self.fadeout)
        else:
            self.root.start_game()
            self.canvas.get_tk_widget().pack_forget()
            self.destroy()
            self.line = None # causes error



class Player(Frame):
    def __init__(self, parent, root):
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
        self.guide.set_color('gold')
        self.candidates = self.ax.scatter([], [], s=150, marker='+', lw=3) # chosen candidates in graph

        self.counter = self.ax.text(0.5, 4.5, "", fontsize=30, color='white')
        self.counter.set_horizontalalignment('center')
        self.counter.set_verticalalignment('center')

        self.setAlpha()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init, frames=1000, interval=20, blit=True)

    def setAlpha(self):
        self.guide.set_alpha(self.alpha)
        self.candidates.set_alpha(self.alpha)

    def track(self, event):
        self.x = event.x
        self.x = int(self.x*1000.0/1680.0)

    def onclick(self):
        self.entries.append(self.x)
        if len(self.entries) == 20:
            self.fadeout()

    def init(self):
        return self.guide, self.candidates, self.counter

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
        self.counter.set_text(str(20-len(self.entries)))
        return self.guide, self.candidates, self.counter

    def fadein(self):
        if self.alpha < 1:
            self.alpha = min(self.alpha+0.1, 1)
            self.setAlpha()
            self.after(50, self.fadein)
        else:
            self.func = self.root.function
            self.entries = []
            self.canvas.mpl_connect("button_press_event", lambda e : self.onclick())

    def fadeout(self):
        self.canvas.mpl_disconnect("button_press_event")
        if self.alpha > 0:
            self.alpha = max(self.alpha-0.1, 0)
            self.setAlpha()
            self.after(50, self.fadeout)
        else:
            self.root.playerRecords = self.entries.copy()
            self.root.create_frame(Machine)
            self.canvas.get_tk_widget().pack_forget()
            self.destroy()
            self.guide = None



class Machine(Frame):
    def __init__(self, parent, root):
        Frame.__init__(self, parent)
        self.root = root
        self.func = []
        self.predict, self.uncertain = [], []
        self.entries = []
        self.alpha = 0.0
        self.x, self.i = 500, 0

        self.fig = plt.Figure(figsize=(16.8,7.2), dpi=100)
        self.fig.patch.set_facecolor('black')

        self.ax = self.fig.add_subplot(xlim=(0,20),ylim=(-5,5))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.ax.set_facecolor('black')
        self.ax.set_position([0, 0, 1, 1])

        self.prdLine, = self.ax.plot([], [], color='white', ls='--')
        self.prdHigh, = self.ax.plot([], [], color='white')
        self.prdLow, = self.ax.plot([], [], color='white')

        self.guide, = self.ax.plot([], [], lw=2, ls='--') # include line in graph
        self.guide.set_color('gold')
        self.candidates = self.ax.scatter([], [], s=150, marker='o', lw=0) # chosen candidates in graph

        self.counter = self.ax.text(0.5, 4.5, "", fontsize=30, color='white')
        self.counter.set_horizontalalignment('center')
        self.counter.set_verticalalignment('center')

        self.setAlpha()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init, frames=1000, interval=20, blit=True)

    def setAlpha(self):
        self.guide.set_alpha(self.alpha)
        self.candidates.set_alpha(self.alpha)

    def GaussianProcess(self, x, y, X, kernel): # given x and y(x), predict all y(X)
        cov11 = kernel(x,x)
        cov12 = kernel(x,X)
        cov22 = kernel(X,X)
        solved = scipy.linalg.solve(cov11, cov12, assume_a='pos').T # inv(cov11)*(cov12)
        mean, cov = solved @ y, cov22 - (solved @ cov12)
        return mean, cov

    def bayesOptim(self): # add entries
        x = np.array([0.02*i for i in self.entries]).reshape(-1,1)
        y = np.array([self.func[i] for i in self.entries]).reshape(-1,1)
        X = np.linspace(0,20,1000).reshape(-1,1)
        mean, cov = self.GaussianProcess(x, y, X, self.root.kernel_RBF)
        std = np.sqrt(np.diag(cov)).reshape(-1,1)
        eps = 0.01
        max_curr = np.max(y)
        imp = mean-max_curr-eps
        Z = imp / (std+0.001)
        EI = imp * norm.cdf(Z) + std * norm.pdf(Z) # Acquisition : Expected Improvement
        EI[std==0.0] = 0.0
        self.entries.append(np.argmax(EI))
        self.predict = mean.flatten()
        self.uncertain = std.flatten()

    def move(self, dir):
        if self.x > dir+150: self.x -= 10
        elif self.x > dir+50: self.x -= 6
        elif self.x > dir+1: self.x -= 3
        elif self.x < dir-150: self.x += 10
        elif self.x < dir-50: self.x += 6
        elif self.x < dir-1: self.x += 3
        else: self.i += 1
        if self.i == 12: self.fadeout()

    def init(self):
        return self.guide, self.candidates, self.prdLine, self.prdHigh, self.prdLow, self.counter

    def animate(self, i):
        guidex = [self.x/50, self.x/50]
        guidey = [-5, 5]
        self.guide.set_data(guidex, guidey)
        if self.i == len(self.entries): # when moving is finished
            if self.i < 12: self.bayesOptim() # add next entry
            X = np.array([0.02*i for i in self.entries[:self.i]])
            Y = np.array([self.func[i] for i in self.entries[:self.i]])
            scale = (Y+4.0)/8.0
            self.candidates.set_offsets(np.vstack((X,Y)).T)
            self.candidates.set_facecolors(plt.cm.coolwarm(scale))
            x = np.linspace(0, 20, 1000)
            self.prdHigh.set_data(x, self.predict-self.uncertain)
            self.prdLow.set_data(x, self.predict+self.uncertain)
            self.prdLine.set_data(x, self.predict)
        elif len(self.entries) != 0: self.move(self.entries[-1]) # needs to move
        self.counter.set_text(str(13-len(self.entries)))
        return self.guide, self.candidates, self.prdLine, self.prdHigh, self.prdLow, self.counter

    def fadein(self):
        self.anim.event_source.start()
        if self.alpha < 1:
            self.alpha = min(self.alpha+0.1, 1)
            self.setAlpha()
            self.after(50, self.fadein)
        else:
            self.func = self.root.function
            self.entries = [500]
            self.x, self.i = 200, 0

    def fadeout(self):
        if self.alpha > 0:
            self.alpha = max(self.alpha-0.1, 0)
            self.setAlpha()
            self.after(50, self.fadeout)
        else:
            self.root.machineRecords = self.entries.copy()
            self.root.check_result()
            self.canvas.get_tk_widget().pack_forget()
            self.destroy()
            self.guide = None



class ResultPage(Frame):
    def __init__(self, parent, root):
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

        self.title = self.ax.text(10, 7, "The Winner Is..   ", fontsize=130, color='white') # include text in graph : coordinates [0,20]x[-5,5]
        self.title.set_horizontalalignment('center')
        self.title.set_verticalalignment('center')

        self.subtitle = self.ax.text(10, 5, "Click Anywhere to Retry", fontsize=30, color='white')
        self.subtitle.set_horizontalalignment('center')
        self.subtitle.set_verticalalignment('center')

        self.player = self.ax.scatter([], [], s=150, marker='+', lw=3) # chosen candidates in graph
        self.machine = self.ax.scatter([], [], s=150, marker='o', lw=0) # chosen candidates in graph

        self.setAlpha()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root) # connect tkinter canvas with pyplot figure
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init, frames=2000, interval=20, blit=True)

    def setAlpha(self):
        self.line.set_alpha(self.alpha)
        self.title.set_alpha(self.alpha)
        self.subtitle.set_alpha(self.alpha)
        self.player.set_alpha(self.alpha)
        self.machine.set_alpha(self.alpha)

    def init(self):
        return self.line, self.title, self.subtitle, self.player, self.machine

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

    def fadein(self):
        if self.alpha < 1:
            self.alpha = min(self.alpha+0.1, 1)
            self.setAlpha()
            self.after(50, self.fadein)
        else:
            self.func = self.root.function
            self.pEntries = self.root.playerRecords
            self.mEntries = self.root.machineRecords
            self.canvas.mpl_connect("button_press_event", lambda e : self.fadeout())

    def fadeout(self):
        if self.alpha > 0:
            self.alpha = max(self.alpha-0.1, 0)
            self.setAlpha()
            self.after(50, self.fadeout)
        else:
            self.root.start_game()
            self.canvas.get_tk_widget().pack_forget()
            self.destroy()
            self.line = None



if __name__ == "__main__":
    app = Game()
    app.mainloop()







