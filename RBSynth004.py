import numpy as np
import pyaudio
import threading
from tkinter import *
import struct

fs = 44100  # sampling rate
f = 440.0  # frequency
bs = 32 #buffsize
playing=0
vel=0
decaying=0
attack=0
decay=0
sustain=0
release=0
volume=0
sample=0
type=0
lowp=0
x = np.arange(bs)

lp=np.zeros(4)#[0,0,0,0]
outwave=np.zeros(bs)#[0,0,///,,,0,0]
def lowpass(wave):
    global lp,outwave
    w0 = 2.0*np.pi*(200+(lowp)**2*20000)/fs
    Q = 1.0
    alpha = np.sin(w0)/(2.0*Q)
    a0 =   (1 + alpha)
    a1 =  -2*np.cos(w0)/a0
    a2 =   (1 - alpha)/a0
    b0 =  (1 - np.cos(w0))/2/a0
    b1 =   (1 - np.cos(w0))/a0
    b2 =  (1 - np.cos(w0))/2/a0
    for i in range(bs):
        outwave[i] = b0*wave[i]+b1*lp[1]+b2*lp[0]-a1*lp[3]-a2*lp[2]
        lp[0] = lp[1]
        lp[1] = wave[i]
        lp[2] = lp[3]
        lp[3] = outwave[i]
    return outwave

def Envelope():
              global vel,decaying
              if playing ==1:
                     if decaying ==1:
                            vel-=decay**3/10000
                            if vel<=sustain:
                                   vel = sustain
                     elif decaying ==0:
                            vel+=attack**3/1000
                     if vel>=10000:
                             vel = 10000
                             decaying=1 
              elif playing ==0:
                      vel-=release**3/1000
                      decaying=0
                      if vel<0:vel = 0
              return vel/10000

def sin():
       global sample
       print(f*(np.power(2,(note-48)/12)))
       t=(x+sample)*f*(np.power(2,(note-48)/12))/fs#buff/fs の分だけの、波形を取り込む
       sample +=bs #次のループで、次のbuff/fs の分取り込む
       t=t-np.trunc(t)#波形一個分に達したとき、初期化
       if type==0:wave=np.sin(2.0*np.pi*t)
       if type==1:wave=x;wave[t<=0.5]=-1;wave[t>=0.5]=1
       if type==2:wave=t*2-1
       else:wave=np.abs(t*2-1)*2-1
       print(type)
       wave = wave*Envelope()
       #wave = lowpass(wave)
       wave = volume/100*wave
       return wave 

def player():
              p = pyaudio.PyAudio()
              stream = p.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=fs,
                     frames_per_buffer = bs,
                     output=True)
              while stream.is_active: 
                     w=sin()
                     w = (w*32768.0).astype(np.int16)#16bit変換、
                     #w=w.tobytes()#機械語化
                     w = struct.pack("h" * len(w), *w)
                     stream.write(w)
              stream.stop_stream()
              stream.close()
              p.terminate()

#window表示
root = Tk()
root.title('RBSynth')
root.geometry('1500x280')
frame1 = Frame(root,width=2000, height=1000,)
frame2 =Frame(root,width=2000, height=100,)
frame1.grid(row=0,column=0)
frame2.grid(row=1,column=0)

def vol(self):
       global volume
       volume = Vscale.get()
Vscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Volume",command=vol,to=100)
Vscale.set(50)
Vscale.grid(row=1,column=0)
def typ(self):
       global type
       type = Tscale.get()
Tscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Type",command=typ,resolution=1,to=4)
Tscale.set(0)
Tscale.grid(row=1,column=1)
def low(self):
       global lowp
       lowp = Lscale.get()
Lscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Lowpass",command=low,to=255)
Lscale.set(50)
Lscale.grid(row=1,column=2)
def atk(self):
       global attack
       attack = Ascale.get()
Ascale = Scale(frame1,orient=HORIZONTAL,length=100,label="Attack",command=atk,from_=5,to =100)
Ascale.set(50)
Ascale.grid(row=2,column=0)
def dec(self):
       global decay
       decay = Dscale.get()
Dscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Decay",command=dec,to =100)
Dscale.set(50)
Dscale.grid(row=2,column=1)
def sus(self):
       global sustain
       sustain = Sscale.get()
Sscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Sustain",command=sus,to =10000)
Sscale.set(8000)
Sscale.grid(row=2,column=2)
def rel(self):
       global release
       release = Rscale.get()
Rscale = Scale(frame1,orient=HORIZONTAL,length=100,label="Release",command=rel,to =100)
Rscale.set(20)
Rscale.grid(row=2,column=3)

#鍵盤
for i in range(88):
       playing =0
       note =0
       def press_button(pit):
             global playing,note
             note = pit #from 0 to 48 + 39=87
             playing = 1
       def release_button(event):
             global playing
             playing = 0
       def button_def(s):# ボタン設定
                     if s%12==1 or s%12==4 or s%12==6 or s%12==9 or s%12==11 or s%12==13:
                            keyi = Button(frame2, text=s,width =1,height = 4,bg='black', fg='white')
                            keyi.grid(row=0,column=i)# ボタンを配置
                            keyi.bind('<ButtonPress-1>',lambda event:press_button(s))
                            keyi.bind('<ButtonRelease-1>',release_button,'+')
                     else:
                            keyi = Button(frame2, text=s,width =1,height = 4)
                            keyi.grid(row=1,column=i)# ボタンを配置
                            keyi.bind('<ButtonPress-1>',lambda event:press_button(s))
                            keyi.bind('<ButtonRelease-1>',release_button,'+')
       button_def(i)
if __name__ == "__main__": 
        thread = threading.Thread(target=player)
        thread.start()
        
root.mainloop()