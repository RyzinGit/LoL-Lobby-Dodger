#Program must be enabled before entering the lobby

import willump
import asyncio
import tkinter as tk
from tkinter import ttk
from tkinter import *
import threading
import os

lock = asyncio.Lock()
lobbyStatus = "NONE"
enabledStatus = "DISABLED"
dodge = False

currentDir = os.getcwd()

countdownAdjustmentMs = 50

def terminate():
    os._exit(0)

def DodgeButtonHandler():
    global dodge
    dodge = not dodge
    
def GUI():
    GUI_root = tk.Tk()
    GUI_root.geometry('200x200')
    GUI_root.title('LoL-Lobby-Dodger')
    GUI_root.resizable(False,False)
    GUI_root.tk.call("source", "UI\\azure.tcl")
    GUI_root.tk.call("set_theme", "dark")
    GUI_root.update()
    GUI_root.protocol('WM_DELETE_WINDOW', terminate)

    lobbyStatusText = ttk.Label(GUI_root,text = "Lobby Status:",font = ('Ariel', 10, 'bold'))
    lobbyStatusText.pack( ipadx = 1, ipady = 1)

    lobbyStatusLabel = ttk.Label(GUI_root,text = lobbyStatus,font = ('Ariel', 15, 'bold'))
    lobbyStatusLabel.pack( ipadx = 3, ipady = 10)

    enabledStatusText = ttk.Label(GUI_root,text = "Dodger Status:",font = ('Ariel', 10, 'bold'))
    enabledStatusText.pack( ipadx = 1, ipady = 1)

    enabledStatusLabel = ttk.Label(GUI_root,text = lobbyStatus,font = ('Ariel', 15, 'bold'))
    enabledStatusLabel.pack( ipadx = 3, ipady = 10)

    st = ttk.Style()
    st.configure('TButton', font=('Ariel',10 ,'bold'))

    exitButton = ttk.Button(GUI_root, text ="Dodge", command = DodgeButtonHandler, style='TButton',padding="1 1 1 1")
    exitButton.pack(ipadx = 1, ipady = 1)
    
    styleRed = ttk.Style()
    styleRed.configure("Red.TLabel", foreground="red")

    styleGreen = ttk.Style()
    styleGreen.configure("Green.TLabel", foreground="green")
    
    def update_label():

        global enabledStatus
        global lobbyStatus

        enabledStatus = "ENABLED" if dodge else "DISABLED"

        enabledStatusLabel['text'] = enabledStatus
        lobbyStatusLabel['text'] = lobbyStatus

        if(enabledStatus == "DISABLED"):
            enabledStatusLabel.configure(style="Red.TLabel")
        else:
            enabledStatusLabel.configure(style= "Green.TLabel")

        GUI_root.after(100, update_label)

    update_label()
    GUI_root.mainloop()

async def countdown(milliseconds):

    async with lock: # Mutex lock
        seconds = int(milliseconds / 1000)
        for _ in range(seconds, 0, -1):
            await asyncio.sleep(1)
        await DodgeLobby()

async def DodgeLobby():
    global dodge
    if(dodge):
        await wllp.request("POST", "/process-control/v1/process/quit")
        os._exit(0)

async def default_message_handler(data):
    print(data['eventType'] + ' ' + data['uri'])

async def printing_listener(data):
    global lobbyStatus
    lobbyStatus = data['data']['timer']['phase']


    if(data['data']['timer']['phase'] == "FINALIZATION" and lock.locked() == False):
        
        adjustedTime = data['data']['timer']['totalTimeInPhase'] - countdownAdjustmentMs
        await countdown(adjustedTime)
        
async def main():
    threading.Thread(target=GUI,name="GUI_Thread").start()
    global wllp
    wllp = await willump.start()

    all_events_subscription = await wllp.subscribe('OnJsonApiEvent', default_handler=default_message_handler)
    wllp.subscription_filter_endpoint(all_events_subscription, '/lol-champ-select/v1/session', handler=printing_listener)
    
    while True:
        await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(wllp.close())
        print()
