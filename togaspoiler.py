import ctypes
import msvcrt
import os
import psutil
import pythoncom, pyHook
import re
import struct
import sys
import time
import threading
import win32api
import win32con

from Tkinter import Label, Tk
from win32gui import *

buffer = ''
pid = None
PROCESS_TERMINATE = 1
hm = pyHook.HookManager()

# Popup Notification class
class WindowsBalloonTip:
    def __init__(self, title, msg1, msg2):
        message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
        }
        # Register the Window class.
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow( classAtom, "Taskbar", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, hinst, None)

        UpdateWindow(self.hwnd)
        iconPathName = os.path.abspath(os.path.join( sys.path[0], "balloontip.ico" ))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
           hicon = LoadImage(hinst, iconPathName, \
                    win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
          hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, \
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER+20,\
                          hicon, "Balloon  tooltip",msg1,200,title))
        # self.show_balloon(title, msg)
        time.sleep(5)
        Shell_NotifyIcon(NIM_MODIFY, \
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER+20,\
                          hicon, "Balloon  tooltip",msg2,200,title))
        time.sleep(5)
        DestroyWindow(self.hwnd)
    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)

#Popup Notification caller method
def balloon_tip(title, msg1, msg2):
    w=WindowsBalloonTip(title, msg1, msg2)

# Catch Keyboard Inputs
def OnKeyboardEvent(event):
    if event.Ascii == 5:
        sys.exit()

    if event.Ascii != 0 and event.Ascii != 8 and event.Ascii != 13:
        keylogs = chr(event.Ascii)
        if event.Ascii == 84 or event.Ascii == 116:
            global buffer
            buffer = ''
            buffer = buffer + chr(event.Ascii)
        elif event.Ascii == 79 or event.Ascii == 111:
            if buffer == 't' or buffer == 'T':
            #if re.match('[tT]', buffer):
                buffer = buffer + chr(event.Ascii)
            else:
                buffer = ''
        elif event.Ascii == 71 or event.Ascii == 103:
            if buffer == 'to' or buffer == 'tO' or buffer == 'To' or buffer == 'TO':
            #if re.match('[tT][oO]', buffer):
                buffer = buffer + chr(event.Ascii)
            else:
                buffer = ''
        elif event.Ascii == 65 or event.Ascii == 97:
            if buffer == 'tog' or buffer == 'Tog' or buffer == 'tOg' or buffer == 'toG' or buffer == 'TOg' or buffer == 'ToG' or buffer == 'tOG' or buffer == 'TOG':
            #if re.match('[tT][oO][gG]', buffer):
                #ctypes.windll.user32.MessageBoxA(0, "Trying to Toga me?\nBetter luck next time!", "TogaSpoiler", 1)
                #win32api.MessageBox(0, "Trying to Toga me?\nBetter luck next time!", "TogaSpoiler", 0x00001000)

                #Freeze the mouse
                hm.MouseAll = input_freeze
                hm.HookMouse()
                #print "PID: ", pid
                #Kill the Spark Process
                handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
                ctypes.windll.kernel32.TerminateProcess(handle, -1)
                ctypes.windll.kernel32.CloseHandle(handle)
                #Display Popup Notification
                balloon_tip("TogaSpoiler", "You have 10 seconds before this computer locks itself!", "Better luck next time! :)")
                #Cleanup buffer
                buffer = ''
                # Lock the computer
                ctypes.windll.user32.LockWorkStation()
                sys.exit()
            else:
                buffer = ''
        else:
            buffer = ''

# Freeze mouse and/or keyboard
def input_freeze(event):
    return False

# Obtian PID of Spark process
def get_spark_pid():
    for proc in psutil.process_iter():
        if proc.name() == 'SparkWindows.exe':
            print proc
            return proc.pid

if __name__ == '__main__':
    while True:
        print "TogaSpoiler Daemon is Running..."
        pid = get_spark_pid()
        #print pid
        try:
            hm.KeyDown = OnKeyboardEvent
            hm.HookKeyboard()
            pythoncom.PumpMessages()
        except Exceptios as e:
            print e
