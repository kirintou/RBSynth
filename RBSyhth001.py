import numpy as np
import pyaudio
import struct
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk

#window表示
root = Tk()
root.title('Synth')
root.geometry('1500x200')
frame1 = Frame(root,width=2000, height=1000,)
frame2 =Frame(root,width=2000, height=100,)
frame1.grid(row=0,column=0)
frame2.grid(row=1,column=0)

fs = 44100  # sampling rate, Hz, must be integer
f = 440.0  # sine frequency, Hz, may be float

# Volume 
def vol(self):
       global volume
       volume = Vscale.get()
Vscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Volume",command=vol)
Vscale.set(50)
Vscale.grid(row=0,column=0)

# type 
def typ(self):
       global type
       type = Tscale.get()
Tscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Type",command=typ,resolution=25)
Tscale.set(100)
Tscale.grid(row=0,column=1)

# duration
def dur(self):
       global duration
       duration = Dscale.get()
Dscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Duration",command=dur)
Dscale.set(20)
Dscale.grid(row=0,column=2)

# lowpass
def low(self):
       global lowpass
       lowpass = Lscale.get()
Lscale = Scale(frame1,orient=HORIZONTAL,length=100,label="lowpass",command=low,from_=0,to=255)
Lscale.set(20)
Lscale.grid(row=0,column=3)



#鍵盤
for i in range(88):


    #ローパスフィルター
    lpfbuf=np.zeros(4)
    outwave=np.zeros(32)
    def lowpassf(self,wave):
        global lpfbuf,outwave
        w0 = 2.0*np.pi*(200+(lowpass/255.0)**2*20000)/fs
        Q = 1.0
        alpha = np.sin(w0)/(2.0*Q)
        a0 =   (1 + alpha)
        a1 =  -2*np.cos(w0)/a0
        a2 =   (1 - alpha)/a0
        b0 =  (1 - np.cos(w0))/2/a0
        b1 =   (1 - np.cos(w0))/a0
        b2 =  (1 - np.cos(w0))/2/a0
        for i in range(32):
            outwave[i] = b0*wave[i]+b1*lpfbuf[1]+b2*lpfbuf[0]-a1*lpfbuf[3]-a2*lpfbuf[2]
            lpfbuf[0] = lpfbuf[1]
            lpfbuf[1] = wave[i]
            lpfbuf[2] = lpfbuf[3]
            lpfbuf[3] = outwave[i]
        return outwave

    def synth(t):
        print(2*t)
        note = t #from 0 to 48 + 39=87
        ph = f*(np.power(2,(note-48)/12))/fs
        if 25<=type<50:#のこぎり波
            wave = ph*2.0-1.0
        elif type<25 :#矩形波
            wave = np.zeros(32);wave[ph<=0.5]=-1;wave[ph>0.5]=1
        elif 50<=type<75:#三角波
            wave = np.abs(ph*2.0-1.0)*2.0-1.0
        else:#サイン波
            wave = np.sin(2.0*np.pi*ph)

        #wave = lowpassf(wave)
        wave = wave *np.arange(fs*duration/10)
        wave = wave.astype(np.float32)
        return wave

    def StartStream(x):
        print(x)
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output=True)
        stream.write(volume/100*synth(x))
        stream.stop_stream()
        stream.close()
        p.terminate()
        
    def button_def(s):# ボタン設定
                keyi = Button(frame2, text=s,width =1,height = 4,command=lambda:StartStream(s))
                keyi.grid(row=0,column=i)# ボタンを配置
    button_def(i)

root.mainloop()