#!/usr/bin/python

import os
import random
import tempfile
import subprocess
import time
import json

import core
import chatter

## system globals
SOURCE = os.path.join("/home", "endorphant", "projects", "ttbp", "bin")
LIVE = "http://tilde.town/~"
FEEDBACK = os.path.join("/home", "endorphant", "ttbp-mail")
USERFILE = os.path.join("/home", "endorphant", "projects", "ttbp", "users.txt")

## user globals
USER = os.path.basename(os.path.expanduser("~"))
PATH = os.path.join("/home", USER, ".ttbp")
PUBLIC = os.path.join("/home", USER, "public_html")
WWW = os.path.join(PATH, "www")
CONFIG = os.path.join(PATH, "config")
TTBPRC = os.path.join(CONFIG, "ttbprc")
DATA = os.path.join(PATH, "entries")
SETTINGS = {
        "editor": "none",
        "publish dir": False
    }

## ui globals
BANNER = open(os.path.join(SOURCE, "config", "banner.txt")).read()
SPACER = "\n\n\n"
INVALID = "please pick a number from the list of options!\n\n"
DUST = "sorry about the dust, but this part is still under construction. check back later!\n\n"

## ref

EDITORS = ["vim", "vi", "emacs", "pico", "nano"]
SUBJECTS = ["bug report", "feature suggestion", "general comment"]

##

def redraw(leftover=""):
    os.system("clear")
    print(BANNER)
    print(SPACER)
    if leftover:
        print("> "+leftover+"\n")

def start():
  redraw()
  #print(chatter.say("greet")+", "+chatter.say("friend"))
  #print("(remember, you can always press ctrl-c to come home)\n")
  print("if you don't want to be here at any point, press <ctrl-d> and it'll all go away.\njust keep in mind that you might lose anything you've started here.\n")
  print(check_init())

  try:
    redraw()
    print(main_menu())
  except ValueError or SyntaxError:
    redraw("oh no i didn't understand that. let's go home and start over.")
    print(main_menu())
  except KeyboardInterrupt:
    redraw("eject button fired! going home now.")
    print(main_menu())

def stop():
  return "\n\t"+chatter.say("bye")

def check_init():
  global SETTINGS
  print("\n\n")
  if os.path.exists(os.path.join(os.path.expanduser("~"),".ttbp")):
      print(chatter.say("greet")+", "+USER+".")
      while not os.path.isfile(TTBPRC):
        setup_handler()
      try:
        SETTINGS = json.load(open(TTBPRC))
      except ValueError:
        setup_handler()

      raw_input("\n\npress <enter> to explore your feelings.\n\n")
      core.load()
      return ""
  else:
    return init()

def init():
    try:
        raw_input("i don't recognize you, stranger. let's make friends.\n\npress <enter> to begin, or <ctrl-c> to get out of here. \n\n")
    except KeyboardInterrupt:
        print("\n\nthanks for checking in! i'll always be here.\n\n")
        quit() 

    users = open(USERFILE, 'a')
    users.write(USER+"\n")
    users.close()
    subprocess.call(["mkdir", PATH])
    subprocess.call(["mkdir", CONFIG])
    subprocess.call(["mkdir", DATA])
    #subprocess.call(["cp", os.path.join(SOURCE, "config", "defaults", "header.txt"), CONFIG])
    header = gen_header()
    headerfile = open(os.path.join(CONFIG, "header.txt"), 'w')
    for line in header:
        headerfile.write(line)
    headerfile.close()
    subprocess.call(["cp", os.path.join(SOURCE, "config", "defaults", "footer.txt"), CONFIG])
    subprocess.call(["cp", os.path.join(SOURCE, "config", "defaults", "style.css"), WWW])

    setup()
    core.load()

    raw_input("\nyou're all good to go, "+chatter.say("friend")+"! hit <enter> to continue.\n\n")
    return ""

def gen_header():
    header = []

    header.append("<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 3.2//EN\">")
    header.append("\n<html>")
    header.append("\n\t<head>")
    header.append("\n\t\t<title>~"+USER+" on TTBP</title>")
    header.append("\n\t\t<link rel=\"stylesheet\" href=\"style.css\" />")
    header.append("\n\t</head>")
    header.append("\n\t<body>")
    header.append("\n\t\t<div id=\"meta\">")
    header.append("\n\t\t\t<h1><a href=\"#\">~"+USER+"</a>@<a href=\"/~endorphant/ttbp\">TTBP</a></h1>")
    header.append("\n\t\t</div>\n")
    header.append("\n\t\t<div id=\"tlogs\">")
    return header

def setup_handler():
    print("\nyour ttbp configuration doesn't look right. let's make you a fresh copy.\n\n")
    try:
        setup()
    except KeyboardInterrupt:
        print("\n\nsorry, trying again.\n\n")
        setup()

def setup():
    global SETTINGS

    # editor selection
    print_menu(EDITORS)
    choice = raw_input("\npick your favorite text editor: ")
    while choice  not in ['0', '1', '2', '3', '4']:
        choice = raw_input("\nplease pick a number from the list: ")

    SETTINGS["editor"] = EDITORS[int(choice)]
    redraw("text editor set to: "+SETTINGS["editor"])

    # publish directory selection
    if SETTINGS["publish dir"]:
        print("\tcurrent publish dir:\t"+os.path.join(PUBLIC, SETTINGS["publish dir"])+"\n\n")
    choice = raw_input("\nwhere do you want your blog published? (leave blank to use default \"blog\") ")
    if not choice:
        choice = "blog"

    publishing = os.path.join(PUBLIC, choice)
    while os.path.exists(publishing):
        second = raw_input("\n"+publishing+" already exists!\nif you're sure you want to use it, hit <enter> to confirm. otherwise, pick another location: ")
        if second == "":
            break
        choice = second
        publishing = os.path.join(PUBLIC, choice)

    SETTINGS["publish dir"] = choice

    # set up publish directory
    if not os.path.exists(publishing):
        subprocess.call(["mkdir", publishing])
        subprocess.call(["touch", os.path.join(publishing, "index.html")])
        index = open(os.path.join(publishing, "index.html"), "w")
        index.write("<h1>ttbp blog placeholder</h1>")
        index.close()
    if os.path.exists(WWW):
        subprocess.call(["rm", WWW])
    subprocess.call(["ln", "-s", publishing, WWW])
    print("\n\tpublishing to "+LIVE+USER+"/"+SETTINGS["publish dir"]+"/\n\n")

    # save settings
    ttbprc = open(TTBPRC, "w")
    ttbprc.write(json.dumps(SETTINGS, sort_keys=True, indent=2, separators=(',',':')))
    ttbprc.close()

    return SETTINGS

## menus

def print_menu(menu):
    i = 0
    for x in menu:
        line = []
        line.append("\t[ ")
        if i < 10:
            line.append(" ")
        line.append(str(i)+" ] "+x)
        print("".join(line))
        i += 1

def main_menu():
    #os.system("clear")
    #print(BANNER)
    #redraw()
    menuOptions = [
            "record feelings",
            "(wip) check out neighbors",
            "change settings",
            "send feedback",
            "(wip) see credits"]
    #print(SPACER)
    print("you're at ttbp home. remember, you can always press <ctrl-c> to come back here.\n\n")
    print_menu(menuOptions)
    #print("how are you feeling today? ")

    try:
        choice = raw_input("\ntell me about your feels (enter 'none' to quit): ")
    except KeyboardInterrupt:
        redraw("eject button fired! going home now.")
        return main_menu()

    if choice == '0':
        redraw()
        today = time.strftime("%Y%m%d")
        write_entry(os.path.join(DATA, today+".txt"))
    elif choice == '1':
        redraw(DUST)
    elif choice == '2':
        pretty_settings = "\n\ttext editor:\t" +SETTINGS["editor"]
        pretty_settings += "\n\tpublish dir:\t" +os.path.join(PUBLIC, SETTINGS["publish dir"])

        redraw("now changing your settings. press <ctrl-c> if you didn't mean to do this.\n\ncurrent settings "+pretty_settings+"\n")
        setup()
        raw_input("\nyou're all good to go, "+chatter.say("friend")+"! hit <enter> to continue.\n\n")
        redraw()
    elif choice == '3':
        redraw()
        feedback_menu()
    elif choice == '4':
        redraw(DUST)
    elif choice == "none":
        return stop()
    else:
        redraw(INVALID)

    return main_menu()

def feedback_menu():
    print("you're about to send mail to ~endorphant about ttbp\n\n")

    print_menu(SUBJECTS)
    choice = raw_input("\npick a category for your feedback: ")

    cat = ""
    if choice in ['0', '1', '2']:
        cat = SUBJECTS[int(choice)]
        raw_input("\ncomposing a "+cat+" to ~endorphant.\n\npress enter to open an external text editor. mail will be sent once you save and quit.\n")
        redraw(send_feedback(cat))
        return
    else:
        redraw(INVALID)

    return feedback_menu()

## handlers

def write_entry(entry=os.path.join(DATA, "test.txt")):

    raw_input("\nfeelings will be recorded for today, "+time.strftime("%d %B %Y")+".\n\nif you've already started recording feelings for this day, you \ncan pick up where you left off.\n\npress <enter> to begin recording your feelings.\n\n")
    subprocess.call([SETTINGS["editor"], entry])
    core.load_files()
    core.write("index.html")
    redraw("new entry posted to "+LIVE+USER+"/"+SETTINGS["publish dir"]+"/index.html\n\nthanks for sharing your feelings!")
    return

def send_feedback(subject="none", mailbox=os.path.join(FEEDBACK, USER+"-"+str(int(time.time()))+".msg")):

    mail = ""

    temp = tempfile.NamedTemporaryFile()
    subprocess.call([SETTINGS["editor"], temp.name])
    mail = open(temp.name, 'r').read()

    outfile = open(mailbox, 'w')
    outfile.write("from:\t\t~"+USER+"\n")
    outfile.write("subject:\t"+subject+"\n")
    outfile.write("date:\t"+time.stfrtime("%d %B %y")+"\n")
    outfile.write(mail)
    outfile.close()

    return "mail sent. thanks for writing! i'll try to respond to you soon."

#####

start()