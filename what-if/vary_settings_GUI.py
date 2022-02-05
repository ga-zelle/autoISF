import  os, sys
import  glob
#from Lib import subprocess
import  contextlib
import  io
import  traceback
from datetime import datetime

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from vary_settings_core import parameters_known
from vary_settings_core import set_tty
from vary_settings_core import log_msg, sub_issue


#################################################################################
#   overall layout                                                              #
#                                                                               #
#   +----------------------------------------------------------------------+    #
#   |   ROW 0 / COL 0:  frame for WD definition                            |    #
#   +----------------------------------------------------------------------+    #
#   |   ROW 1 / COL 0:  Notebook tabs                                      |    #
#   |   +-----------------------------------------------------------+      |    #
#   |   |  Tab1: Inputs     | tab2: Graphics    | tab3: Results     |      |    #
#   |                                                                      |    #
#   |                                                                      |    #
#   |                                                                      |    #
#   +----------------------------------------------------------------------+    #
#################################################################################
root = Tk()
root.title('Manage Inputs and Outputs for Emulating AAPS Settings')
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)
ttk.Sizegrip(root).grid(column=999, row=999, sticky=(S,E))
#root['width']  = 600
#root['height'] = 500

book = ttk.Notebook(root)
book.columnconfigure(0, weight=1)
book.rowconfigure(0, weight=1)
tStyle = ttk.Style()
#tStyle.configure('TNotebook')
tStyle.configure('Bold.TNotebook.Tab', font='bold', padding=[20,0], background='#AAA')
book['style'] = 'Bold.TNotebook'
book.grid(column=0, row=2, columnspan=4, sticky='WN', padx=10, pady=20)
inpframe = ttk.Frame(book, relief='raised')
outframe = ttk.Frame(book, relief='raised')
resframe = ttk.Frame(book, relief='raised')
runframe = ttk.Frame(book, relief='raised')
book.add(inpframe, text='Select Inputs')
book.add(outframe, text='Select Graphics Options')
book.add(runframe, text='Execute the Analysis')
book.add(resframe, text='Inspect Results')



#################################################################################
#   wdframe:                                                                    #
#################################################################################
#   select the working directory    ---------------------------------------------
#wdframe = ttk.Frame(root, padding="3 3 12 12", borderwidth=10, relief='raised')
wdframe = ttk.Frame(root, padding="3 3 3 12", relief='raised')
wdframe.grid(column=0, row=0, columnspan=4, sticky='WENS')
wdframe.columnconfigure(0, weight=1)
wdframe.columnconfigure(1, weight=1)

def get_wdir():
    oldwd = wdir.get()
    newwd = filedialog.askdirectory(initialdir=oldwd)
    if newwd != "":
        wdir.set(newwd)

def reset_all():
    # input frame
    wdir.set('')
    vfil.set('')
    afil.set('')

    stmpStart.set('no')
    tstart_entry.state(['disabled'])                                                # initially OFF
    tstart.set(noStart)

    stmpStopp.set('no')
    tstopp.set(noStopp)
    tstopp_entry.state(['disabled'])                                                # initially OFF
    chkStopp.state(['disabled'])                                                    # initially OFF

    # variant frame
    radioMost()

    # run frame
    runState.set(notRunning)
    clear_msg()
    
    # result frame
    logfil.set('')
    tabfil.set('')
    deltafil.set('')
    txtorig.set('')
    txtemul.set('')
    pdffil.set('')
    
def gui_quit():
    really = messagebox.askyesno(
        message='Are you sure you want to quit this GUI?', icon='question', title='Quit ?', default='no')
    if really:
        root.destroy()
        exit()                                                                  # from tkinter
        sys.exit                                                                # from python

ttk.Label(wdframe, text="Your working directory").grid(column=0, columnspan=3, row=0, sticky=(W,E), padx=5)
wdir = StringVar()
wdir_entry = ttk.Entry(wdframe, width=100, textvariable=wdir)
wdir_entry.grid(column=0, columnspan=3, row=1, sticky=(W, E), padx=5)

ttk.Button(wdframe, text="Browse", command=get_wdir).grid(column=3, row=1, sticky=(W,E), padx=10)
ttk.Button(wdframe, text="Reset All", command=reset_all).grid(column=4, row=1, sticky=(W,E), padx=5)
tStyle.configure('Exit.TButton', foreground='red')
ttk.Button(wdframe, text="Quit",   command=gui_quit, style='Exit.TButton').grid(column=5, row=1, sticky=(W,E), padx=10)
# same as QUIT button so matplotlib is closed, too:
root.protocol("WM_DELETE_WINDOW", gui_quit)




#################################################################################
#   inpframe:                                                                   #
#################################################################################
#   select the variant definition file  -----------------------------------------
def get_vfil():
    oldvf = vfil.get()
    newvf = filedialog.askopenfilename(filetypes={'Variation {.vdf .dat}'}, initialdir=wdir.get())
    if newvf != "":
        vfil.set(newvf)

def edit_vfil():
    oldvf = vfil.get()
    os.startfile(oldvf)                                                         # requires DOS knows to edit ".dat" files

inpframe.columnconfigure(0, weight=1)
inpframe.columnconfigure(1, weight=1)
vfilRow = 3
ttk.Label(inpframe, text="\nYour variant definition file").grid(column=0, columnspan=2, row=vfilRow-1, sticky=(W), padx=5)
vfil = StringVar()
vfil_entry = ttk.Entry(inpframe, width=100, textvariable=vfil)
vfil_entry.grid(column=0, columnspan=2, row=vfilRow, sticky=(W,E), padx=5)

ttk.Button(inpframe, text="Browse", command=get_vfil).grid( column=2, row=vfilRow, sticky=(W, E), padx=10)
ttk.Button(inpframe, text="Edit",   command=edit_vfil).grid(column=3, row=vfilRow, sticky=(W, E), padx=10)

#   select the AAPS logfile(s)  -------------------------------------------------
def get_afil():
    oldaf = afil.get()
    loglist = {'logs {.zip .0 .1 .2 .3 .4 .5 .6 .7 .8 .9 .10 .11 .12 .13 .14 .15 .16}'}  # my own max was 11 !!
    newaf = filedialog.askopenfilename(filetypes=loglist, initialdir=wdir.get())
    if newaf != "":
        afil.set(newaf)

def show_afil():
    newaf = afil.get()
    if newaf.find("*")<0 and newaf.find("?")<0:    
        msg = "No wild card match specified.\nInsert '*' or '?' at the appropriate position"
    else:
        msg = ""
        logListe = glob.glob(newaf, recursive=False)                            # the wild card match
        filecount = 0
        for fn in logListe:
            ftype = fn[len(fn)-3:]
            if ftype=='zip' or ftype.find(".")>=0:
                msg += os.path.basename(fn) + "\n"
                filecount += 1
        msg +="\nTotal match count: " + str(filecount)
    messagebox.showinfo(message=msg, title="List matching logfiles", icon="info")

afilRow = 5
ttk.Label(inpframe, text="\nYour AAPS logfile(s)").grid(column=0, columnspan=2, row=afilRow-1, sticky=(E), padx=5)
afil = StringVar()
afil_entry = ttk.Entry(inpframe, width=100, textvariable=afil, justify='right')
afil_entry.grid(column=0, columnspan=2, row=afilRow, sticky=(W,E), padx=5)

ttk.Button(inpframe, text="Browse", command=get_afil).grid( column=2, row=afilRow, sticky=(W, E), padx=10)
ttk.Button(inpframe, text="Show matches", command=show_afil).grid( column=3, row=afilRow, sticky=(W, E), padx=10)

#   select the optional start and end date/time     -----------------------------
def stmpStartChanged():
    if stmpStart.get() == 'yes':
        tstart_entry.state(['!disabled'])
        chkStopp.state(['!disabled'])
    else:
        tstart_entry.state(['disabled'])
        tstopp_entry.state(['disabled'])
        chkStopp.state(['disabled'])

def stmpStoppChanged():
    if stmpStopp.get() == 'yes':
        tstopp_entry.state(['!disabled'])
    else:
        tstopp_entry.state(['disabled'])
    
tstartRow = 10
noStart = '2000-01-01T00:00:00Z'
noStopp = '2099-12-31T23:59:59Z'
ttk.Label(inpframe, text="\nexample date/time format ...   2019-11-06T12:30:00Z   ").grid(column=1, row=tstartRow-1, sticky=(E), padx=5)

stmpStart = StringVar()
stmpStart.set('no')                                                             #was in tri-state
chkStart  = ttk.Checkbutton(inpframe, text='  Use start time by entering UTC date/time', \
            command=stmpStartChanged, variable=stmpStart, onvalue='yes', offvalue='no')
chkStart.grid(column=0, row=tstartRow, sticky=(W), padx=5)
tstart = StringVar()
tstart_entry = ttk.Entry(inpframe, width=20, textvariable=tstart)
tstart_entry.grid(column=1, row=tstartRow, sticky=(E), padx=5, pady=0)
tstart_entry.state(['disabled'])                                                # initially OFF
tstart.set(noStart)

stmpStopp = StringVar()
stmpStopp.set('no')                                                             #was in tri-state
chkStopp  = ttk.Checkbutton(inpframe, text='  Use final time by entering UTC date/time', \
            command=stmpStoppChanged, variable=stmpStopp, onvalue='yes', offvalue='no')
chkStopp.grid(column=0, row=tstartRow+1, sticky=(W), padx=5)
tstopp = StringVar()
tstopp_entry = ttk.Entry(inpframe, width=20, textvariable=tstopp)
tstopp_entry.grid(column=1, row=tstartRow+1, sticky=(E), padx=5, pady=5)
tstopp_entry.state(['disabled'])                                                # initially OFF
chkStopp.state(['disabled'])                                                    # initially OFF
tstopp.set(noStopp)


#################################################################################
#   outframe:   select the graphics options                                     #
#################################################################################
def clearchecks():
    global useinsReq
    
    useinsReq.set('off')
    usemaxBolus.set('off')
    useSMB.set('off')
    usebasal.set('off')
    useinsReq.set('off')
    usebg.set('off')
    usetarget.set('off')
    usecob.set('off')
    useiob.set('off')
    useactivity.set('off')
    useas_ratio.set('off')
    useai_ratio.set('off')
    userange.set('off')
    usebestslope.set('off')
    usefitsslope.set('off')
    usebestparabola.set('off')
    usefitsparabola.set('off')
    useISF.set('off')
    if raw.get() == 'most':
        usepred.set('on')
        useflow.set('on')
    else:
        usepred.set('off')
        useflow.set('off')
    
def optionLabels(show):
    chkinsReq['text']   = show + ' insulin required'
    chkmaxBolus['text'] = show + ' max bolus limit'
    chkSMB['text']      = show + ' SMB'
    chkbasal['text']    = show + ' basal rate'
    
    chkbg['text']       = show + ' glucose'
    chktarget['text']   = show + ' targets'
    chkcob['text']      = show + ' COB'
    chkiob['text']      = show + ' IOB'
    chkactivity['text'] = show + ' insulin activity'
    chkas_ratio['text'] = show + ' autosense ratio'
    chkai_ratio['text'] = show + ' autoISF ratio'
    chkrange['text']    = show + ' range parameters'
    chkbestslope['text']    = show + ' best slope'
    chkfitsslope['text']    = show + ' other slopes'
    chkbestparabola['text'] = show + ' best parabola'
    chkfitsparabola['text'] = show + ' other parabolas'
    chkISF['text']      = show + ' ISF'
    chkpred['text']     = show + ' predictions'
    
    chkflow['text']     = show + ' flowchart'

def act(using, thisOpt):
    global doit
    txt = doit.get('1.0', 'end')[:-1]
    addornot = raw.get()
    if addornot == 'most':
        what = '-' + thisOpt                                                    # suppress option flag
    else:
        what = thisOpt                                                          # use option flag
    wo = txt.find(what)
    if wo>=0:
        if using == 'off':
            txt = txt[:wo] + txt[wo+len(what):]                                 # deleted the option from list
        # final clean ups
        txt = txt.replace('//', '/')
        if len(txt)>0:
            if '/' == txt[0]:             txt = txt[1:]
            if '/' == txt[len(txt)-1]:    txt = txt[:-1]
    elif using == 'on':
        if len(txt) > 0:    txt += '/'
        txt += what
    doit.delete('1.0', 'end')
    doit.insert('end', txt)                                                     # update displayed content
    pass
    
def radioAll():
    optHeader.set("\n")                
    raw.set('All')
    doit.delete('1.0', 'end')
    doit.insert('end', 'All')
    flowframe.grid_remove()
    glucframe.grid_remove()
    isf_frame.grid_remove()
    insuframe.grid_remove()
    clearchecks()
    
def radioMost():
    optHeader.set("\nFine grained selection of items to be excluded")                
    raw.set('most')
    doit.delete('1.0', 'end')
    clearchecks()
    insuframe.grid()
    glucframe.grid()
    isf_frame.grid()
    flowframe.grid()
    doit.insert('end', 'All/-pred/-flowchart')
    optionLabels('Hide')

def radioSome():
    optHeader.set("\nFine grained selection of items to be included")                
    raw.set('some')
    doit.delete('1.0', 'end')
    clearchecks()
    insuframe.grid()
    glucframe.grid()
    isf_frame.grid()
    flowframe.grid()
    optionLabels('Show')

outframe.columnconfigure(1, weight=1)
outframe.columnconfigure(2, weight=1)
outframe.columnconfigure(3, weight=1)
ttk.Label(outframe, text="\nThe resulting graphics request string").grid(column=1, row=0, columnspan=3, padx=5, sticky=(W))
doit = Text(outframe, state='normal', width=76, height=1)                       # w=77 equals w=80 for Entry
doit.grid(column=1, row=1, columnspan=3, padx=5, sticky='w')

optHeader = StringVar()
ttk.Label(outframe, textvariable=optHeader).grid(column=1, row=19, columnspan=3, padx=5, sticky=(W))
insuframe = ttk.Labelframe(outframe, width=250, height=400, text='Insulin chart content')
insuframe.grid(row= 20, column=1, padx=20, pady=5, sticky=(W,N))
glucframe = ttk.Labelframe(outframe, width=250, height=400, text='Glucose chart content          ') # same width as autoISF frame
glucframe.grid(row= 20, column=2, padx=20, pady=5, sticky=(W,N))
isf_frame = ttk.Labelframe(outframe, width=250, height=400, text='specials, e.g. autoISF')
isf_frame.grid(row= 30, column=2, padx=20, pady=5, sticky=(W,N))
flowframe = ttk.Labelframe(outframe, width=250, height=400, text='Flowchart ON/OFF')
flowframe.grid(row= 20, column=3, padx=20, pady=5, sticky=(W,N))

#   insulin chart options     --------------------------------------------------
def useinsReqChanged():     act(useinsReq.get(), "insReq")
useinsReq = StringVar()
chkinsReq = ttk.Checkbutton(insuframe, text='Show insulin required', \
            command=useinsReqChanged, variable=useinsReq, onvalue='on', offvalue='off')
chkinsReq.grid(column=0, row=1, columnspan=2, sticky=(W), padx=5)

def usemaxBolusChanged():   act(usemaxBolus.get(), "maxBolus")
usemaxBolus = StringVar()
chkmaxBolus = ttk.Checkbutton(insuframe, text='Show max bolus limit', \
            command=usemaxBolusChanged, variable=usemaxBolus, onvalue='on', offvalue='off')
chkmaxBolus.grid(column=0, row=2, columnspan=2, sticky=(W), padx=5)

def useSMBChanged():        act(useSMB.get(), "SMB")
useSMB = StringVar()
chkSMB = ttk.Checkbutton(insuframe, text='Show SMB', \
            command=useSMBChanged, variable=useSMB, onvalue='on', offvalue='off')
chkSMB.grid(column=0, row=3, columnspan=2, sticky=(W), padx=5)

def usebasalChanged():      act(usebasal.get(), "basal")
usebasal = StringVar()
chkbasal = ttk.Checkbutton(insuframe, text='Show basal rate', \
            command=usebasalChanged, variable=usebasal, onvalue='on', offvalue='off')
chkbasal.grid(column=0, row=4, columnspan=2, sticky=(W), padx=5)

#   glucose chart options   --------------------------------------------------
def usepredChanged():       act(usepred.get(), "pred")
usepred = StringVar()
chkpred = ttk.Checkbutton(glucframe, text='Show predictions', \
            command=usepredChanged, variable=usepred, onvalue='on', offvalue='off')
chkpred.grid(column=0, row=1, columnspan=2, sticky=(W), padx=5)

def usebgChanged():         act(usebg.get(), "bg")
usebg = StringVar()
chkbg = ttk.Checkbutton(glucframe, text='Show glucose', \
            command=usebgChanged, variable=usebg, onvalue='on', offvalue='off')
chkbg.grid(column=0, row=2, columnspan=2, sticky=(W), padx=5)

def usetargetChanged():     act(usetarget.get(), "target")
usetarget = StringVar()
chktarget = ttk.Checkbutton(glucframe, text='Show targets', \
            command=usetargetChanged, variable=usetarget, onvalue='on', offvalue='off')
chktarget.grid(column=0, row=3, columnspan=2, sticky=(W), padx=5)

def usecobChanged():        act(usecob.get(), "cob")
usecob = StringVar()
chkcob = ttk.Checkbutton(glucframe, text='Show COB', \
            command=usecobChanged, variable=usecob, onvalue='on', offvalue='off')
chkcob.grid(column=0, row=4, columnspan=2, sticky=(W), padx=5)

def useiobChanged():        act(useiob.get(), "iob")
useiob = StringVar()
chkiob = ttk.Checkbutton(glucframe, text='Show IOB', \
            command=useiobChanged, variable=useiob, onvalue='on', offvalue='off')
chkiob.grid(column=0, row=5, columnspan=2, sticky=(W), padx=5)

def useactivityChanged():   act(useactivity.get(), "activity")
useactivity = StringVar()
chkactivity = ttk.Checkbutton(glucframe, text='Show insulin activity', \
            command=useactivityChanged, variable=useactivity, onvalue='on', offvalue='off')
chkactivity.grid(column=0, row=6, columnspan=2, sticky=(W), padx=5)

def useas_ratioChanged():   act(useas_ratio.get(), "as_ratio")
useas_ratio = StringVar()
chkas_ratio = ttk.Checkbutton(glucframe, text='Show autosense ratio', \
            command=useas_ratioChanged, variable=useas_ratio, onvalue='on', offvalue='off')
chkas_ratio.grid(column=0, row=7, columnspan=2, sticky=(W), padx=5)

#   glucose chart, subchart autoISF options   --------------------------------------------------
def useai_ratioChanged():   act(useai_ratio.get(), "autoISF")
useai_ratio = StringVar()
chkai_ratio = ttk.Checkbutton(isf_frame, text='Show autoISF ratio', \
            command=useai_ratioChanged, variable=useai_ratio, onvalue='on', offvalue='off')
chkai_ratio.grid(column=0, row=7, columnspan=2, sticky=(W), padx=5)

def userangeChanged():   act(userange.get(), "range")
userange = StringVar()
chkrange = ttk.Checkbutton(isf_frame, text='Show range', \
            command=userangeChanged, variable=userange, onvalue='on', offvalue='off')
chkrange.grid(column=0, row=8, columnspan=2, sticky=(W), padx=5)

def usebestslopeChanged():   act(usebestslope.get(), "bestslope")
usebestslope = StringVar()
chkbestslope = ttk.Checkbutton(isf_frame, text='Show best slope', \
            command=usebestslopeChanged, variable=usebestslope, onvalue='on', offvalue='off')
chkbestslope.grid(column=0, row=9, columnspan=2, sticky=(W), padx=5)

def usefitsslopeChanged():   act(usefitsslope.get(), "fitsslope")
usefitsslope = StringVar()
chkfitsslope = ttk.Checkbutton(isf_frame, text='Show other slopes', \
            command=usefitsslopeChanged, variable=usefitsslope, onvalue='on', offvalue='off')
chkfitsslope.grid(column=0, row=10, columnspan=2, sticky=(W), padx=5)

def usebestparabolaChanged():   act(usebestparabola.get(), "bestParabola")
usebestparabola = StringVar()
chkbestparabola = ttk.Checkbutton(isf_frame, text='Show best parabola', \
            command=usebestparabolaChanged, variable=usebestparabola, onvalue='on', offvalue='off')
chkbestparabola.grid(column=0, row=11, columnspan=2, sticky=(W), padx=5)

def usefitsparabolaChanged():   act(usefitsparabola.get(), "fitsParabola")
usefitsparabola = StringVar()
chkfitsparabola = ttk.Checkbutton(isf_frame, text='Show other parabolas', \
            command=usefitsparabolaChanged, variable=usefitsparabola, onvalue='on', offvalue='off')
chkfitsparabola.grid(column=0, row=12, columnspan=2, sticky=(W), padx=5)

def useISFChanged():   act(useISF.get(), "ISF")
useISF = StringVar()
chkISF = ttk.Checkbutton(isf_frame, text='Show ISF', \
            command=useISFChanged, variable=useISF, onvalue='on', offvalue='off')
chkISF.grid(column=0, row=13, columnspan=2, sticky=(W), padx=5)

#   flowchart options     ------------------------------------------------------
def useflowChanged():       act(useflow.get(), "flowchart")
useflow = StringVar()
chkflow = ttk.Checkbutton(flowframe, text='Create flowchart', \
            command=useflowChanged, variable=useflow, onvalue='on', offvalue='off')
chkflow.grid(column=0, row=1, columnspan=2, sticky=(W), padx=5)

#   this is placed last because their commands refer to above defs
ttk.Label(outframe, text="\nCoarse grained selection of graphics output").grid(column=1, row=2, columnspan=3, padx=5, sticky=(W))
raw  = StringVar()
some = ttk.Radiobutton(outframe, variable=raw, value='some', command=radioSome, text='just a few')
most = ttk.Radiobutton(outframe, variable=raw, value='most', command=radioMost, text='most (i.e.  All but a few)')
all  = ttk.Radiobutton(outframe, variable=raw, value='All',  command=radioAll,  text='All')
radioMost()                                                                     # initial default
some.grid(column=1, row=11, padx=20, sticky=W)
most.grid(column=1, row=12, padx=20, sticky=W)
all.grid( column=1, row=13, padx=20, sticky=W)



#################################################################################
#   resframe                                                                    #
#################################################################################
#   inspect the results     -----------------------------------------------------

def get_logfil():
    oldaf = logfil.get()
    loglist = {'logfile {.log}'}  
    newaf = filedialog.askopenfilename(filetypes=loglist, initialdir=wdir.get(), initialfile=oldaf)
    if newaf != "":
        logfil.set(newaf)

def get_deltafil():
    oldaf = deltafil.get()
    loglist = {'deltafile {.delta}'}  
    newaf = filedialog.askopenfilename(filetypes=loglist, initialdir=wdir.get(), initialfile=oldaf)
    if newaf != "":
        deltafil.set(newaf)

def get_tabfil():
    oldaf = tabfil.get()
    loglist = {'logfile {.tab}'}  
    newaf = filedialog.askopenfilename(filetypes=loglist, initialdir=wdir.get(), initialfile=oldaf)
    if newaf != "":
        tabfil.set(newaf)

def get_txtorig():
    oldaf = txtorig.get()
    loglist = {'orig_log {.orig.txt}'}  
    newaf = filedialog.askopenfilename(filetypes=loglist, initialdir=wdir.get(), initialfile=oldaf)
    if newaf != "":
        txtorig.set(newaf)

def get_txtemul():
    oldaf = txtemul.get()
    loglist = {'emul_log {.txt}'}  
    newaf = filedialog.askopenfilename(filetypes=loglist, initialdir=wdir.get(), initialfile=oldaf)
    if newaf != "":
        txtemul.set(newaf)

def get_pdffil():
    oldaf = pdffil.get()
    loglist = {'graphics {.pdf .jpg}'}  
    newaf = filedialog.askopenfilename(filetypes=loglist, initialdir=wdir.get(), initialfile=oldaf)
    if newaf != "":
        pdffil.set(newaf)

def edit_logfil():
    oldvf = logfil.get()
    try:
        os.startfile(oldvf)                                                     # requires DOS knows to edit ".log" files
    except:                                                                     # catch *all* exceptions
        book.select(4)                                                          # activate result tab
        tb = sys.exc_info()[2]
        sub_issue("Problem in vary_GUI.py")
        for ele in traceback.format_tb(tb):
            sub_issue(ele[:-1])                                                 # sub appends <CR>
        sub_issue(str(sys.exc_info()[1]))

def edit_deltafil():
    oldvf = deltafil.get()
    try:
        os.startfile(oldvf)                                                     # requires DOS knows to edit ".delta" files
    except:                                                                     # catch *all* exceptions
        book.select(4)                                                          # activate result tab
        tb = sys.exc_info()[2]
        sub_issue("Problem in vary_GUI.py")
        for ele in traceback.format_tb(tb):
            sub_issue(ele[:-1])                                                 # sub appends <CR>
        sub_issue(str(sys.exc_info()[1]))

def edit_tabfil():
    oldvf = tabfil.get()
    try:
        os.startfile(oldvf)                                                     # requires DOS knows to edit ".log" files
    except:                                                                     # catch *all* exceptions
        book.select(4)                                                          # activate result tab
        tb = sys.exc_info()[2]
        sub_issue("Problem in vary_GUI.py")
        for ele in traceback.format_tb(tb):
            sub_issue(ele[:-1])                                                 # sub appends <CR>
        sub_issue(str(sys.exc_info()[1]))

def edit_txtorig():
    oldvf = txtorig.get()
    try:
        os.startfile(oldvf)                                                     # requires DOS knows to edit ".log" files
    except:                                                                     # catch *all* exceptions
        book.select(4)                                                          # activate result tab
        tb = sys.exc_info()[2]
        sub_issue("Problem in vary_GUI.py")
        for ele in traceback.format_tb(tb):
            sub_issue(ele[:-1])                                                 # sub appends <CR>
        sub_issue(str(sys.exc_info()[1]))

def edit_txtemul():
    oldvf = txtemul.get()
    try:
        os.startfile(oldvf)                                                     # requires DOS knows to edit ".log" files
    except:                                                                     # catch *all* exceptions
        book.select(4)                                                          # activate result tab
        tb = sys.exc_info()[2]
        sub_issue("Problem in vary_GUI.py")
        for ele in traceback.format_tb(tb):
            sub_issue(ele[:-1])                                                 # sub appends <CR>
        sub_issue(str(sys.exc_info()[1]))

def edit_pdffil():
    oldvf = pdffil.get()
    try:
        os.startfile(oldvf)                                                     # requires DOS knows to open ".pdf" files
    except:                                                                     # catch *all* exceptions
        book.select(4)                                                          # activate result tab
        tb = sys.exc_info()[2]
        sub_issue("Problem in vary_GUI.py")
        for ele in traceback.format_tb(tb):
            sub_issue(ele[:-1])                                                 # sub appends <CR>
        sub_issue(str(sys.exc_info()[1]))

resframe.columnconfigure(0, weight=1)
resframe.columnconfigure(1, weight=1)
resframe.columnconfigure(2, weight=1)
rfilRow = 1

ttk.Label(resframe, text="\n*.log - Your file showing edits from the variant assignments").grid(column=0, columnspan=2, row=rfilRow-1, sticky=(W), padx=5)
logfil = StringVar()
logfil_entry = ttk.Entry(resframe, width=130, textvariable=logfil)              #, justify='right')
logfil_entry.grid(column=0, columnspan=3, row=rfilRow, sticky=(W,E), padx=5)
ttk.Button(resframe, text="Browse", command=get_logfil).grid( column=3, row=rfilRow, sticky=(W, E), padx=10)
ttk.Button(resframe, text="Show",   command=edit_logfil).grid(column=4, row=rfilRow, sticky=(W, E), padx=10)

ttk.Label(resframe, text="\n*.tab - Your table comparing key values of original vs emulation").grid(column=0, columnspan=2, row=rfilRow+1, sticky=(W), padx=5)
tabfil = StringVar()
tabfil_entry = ttk.Entry(resframe, width=130, textvariable=tabfil)              #, justify='right')
tabfil_entry.grid(column=0, columnspan=3, row=rfilRow+2, sticky=(W,E), padx=5)
ttk.Button(resframe, text="Browse", command=get_tabfil).grid( column=3, row=rfilRow+2, sticky=(W, E), padx=10)
ttk.Button(resframe, text="Show",   command=edit_tabfil).grid(column=4, row=rfilRow+2, sticky=(W, E), padx=10)

ttk.Label(resframe, text="\n*.delta - Your table comparing bg deltas of original vs emulation").grid(column=0, columnspan=2, row=rfilRow+3, sticky=(W), padx=5)
deltafil = StringVar()
deltafil_entry = ttk.Entry(resframe, width=130, textvariable=deltafil)            #, justify='right')
deltafil_entry.grid(column=0, columnspan=3, row=rfilRow+4, sticky=(W,E), padx=5)
ttk.Button(resframe, text="Browse", command=get_deltafil).grid( column=3, row=rfilRow+4, sticky=(W, E), padx=10)
ttk.Button(resframe, text="Show",   command=edit_deltafil).grid(column=4, row=rfilRow+4, sticky=(W, E), padx=10)

ttk.Label(resframe, text="\n*.orig.txt - Your short log of original analysis").grid(column=0, columnspan=2, row=rfilRow+5, sticky=(W), padx=5)
txtorig = StringVar()
txtorig_entry = ttk.Entry(resframe, width=130, textvariable=txtorig)              #, justify='right')
txtorig_entry.grid(column=0, columnspan=3, row=rfilRow+6, sticky=(W,E), padx=5)
ttk.Button(resframe, text="Browse", command=get_txtorig).grid( column=3, row=rfilRow+6, sticky=(W, E), padx=10)
ttk.Button(resframe, text="Show",   command=edit_txtorig).grid(column=4, row=rfilRow+6, sticky=(W, E), padx=10)

ttk.Label(resframe, text="\n*.txt - Your short log of emulated analysis").grid(column=0, columnspan=2, row=rfilRow+7, sticky=(W), padx=5)
txtemul = StringVar()
txtemul_entry = ttk.Entry(resframe, width=130, textvariable=txtemul)              #, justify='right')
txtemul_entry.grid(column=0, columnspan=3, row=rfilRow+8, sticky=(W,E), padx=5)
ttk.Button(resframe, text="Browse", command=get_txtemul).grid( column=3, row=rfilRow+8, sticky=(W, E), padx=10)
ttk.Button(resframe, text="Show",   command=edit_txtemul).grid(column=4, row=rfilRow+8, sticky=(W, E), padx=10)

ttk.Label(resframe, text="\n*.pdf etc. - Your graphic file comparing key values of original vs emulation").grid(column=0, columnspan=2, row=rfilRow+9, sticky=(W), padx=5)
pdffil = StringVar()
pdffil_entry = ttk.Entry(resframe, width=130, textvariable=pdffil)              #, justify='right')
pdffil_entry.grid(column=0, columnspan=3, row=rfilRow+10, sticky=(W,E), padx=5)
ttk.Button(resframe, text="Browse", command=get_pdffil).grid( column=3, row=rfilRow+10, sticky=(W, E), padx=10)
ttk.Button(resframe, text="Show",   command=edit_pdffil).grid(column=4, row=rfilRow+10, sticky=(W, E), padx=10)



#################################################################################
#   runframe: execute the emulation                                             #
#################################################################################

def clear_msg():
    lfd['state'] = 'normal'
    lfd.delete(1.0, 'end')
    lfd['state'] = 'disabled'
    
def sub_emul():
    global runState 
    runState.set('Checking inputs ...   ')
    ttk.Label(runframe, textvariable=runState, style='TLabel').grid(column=2, row=runRow, sticky=(W), padx=20, pady=10)
    incomplete = False                                                          # update frame display
    variant = os.path.basename(vfil.get())
    if variant == '':
        sub_issue('variant definition file is missing')
        incomplete = True
    gopt = doit.get('1.0', 'end')[:-1]
    if gopt == '':
        sub_issue('graphics output options are missing')
        incomplete = True
    gopt = 'Windows/' + gopt                                                    # i.e. not in Android
    if afil.get() == '':
        sub_issue('AndroidAPS logfile is missing')
        incomplete = True
    if stmpStart.get() == 'no':
        useStart = noStart
    else:
        useStart = tstart.get()
        if useStart == '':
            sub_issue('start time ticked but missing')
            incomplete = True
    if stmpStopp.get() == 'no':
        useStopp = noStopp
    else:
        useStopp = tstopp.get()
        if useStopp == '':
            sub_issue('stop time ticked but missing')
            incomplete = True
    if incomplete:
        runState.set(notRunning)
        lfd['state'] = 'disabled'
        return                                                                  # no execution

    try:
        runState.set('Emulation started ...')
        runframe.update()                                                       # update frame display
        #kick_off(afil.get(), gopt, variant, useStart, useStopp)
        entries = {}
        thisTime, extraSMB, CarbReqGram, CarbReqTime, lastCOB = parameters_known(afil.get(), gopt, vfil.get(), useStart, useStopp, entries, m)
        if thisTime == 'SYNTAX':
            runState.set('Emulation halted ... ')
            ttk.Label(runframe, textvariable=runState, style='Error.TLabel').grid(column=2, row=runRow, sticky=(W), padx=20, pady=10)
            #sub_issue('Problem in VDF file. For details, see file "*.'+variant[:-4]+'.log"')
        else:   
            runState.set('Emulation finished ..')
            ttk.Label(runframe, textvariable=runState, style='Done.TLabel').grid(column=2, row=runRow, sticky=(W), padx=20, pady=10)
        runframe.update()                                                       # update frame display

        # load result filenames into resframe
        newaf = afil.get()
        logListe = glob.glob(newaf, recursive=False)                            # the wild card match
        filecount = 0
        for fn in logListe:
            #log_msg("checking result file "+fn)
            ftype = fn[len(fn)-3:]
            fn_first = wdir.get() + '/' + os.path.basename(fn)
            varLabel = variant[:-4]
            if ftype=='zip' or ftype.find(".")>=0:
                logfil.set(fn_first+'.'+variant[:-4]+'.log')
                tabfil.set(fn_first+'.'+variant[:-4]+'.tab')
                deltafil.set(fn_first+'.'+variant[:-4]+'.delta')
                txtorig.set(fn_first+'.' + 'orig' +  '.txt')
                txtemul.set(fn_first+'.'+variant[:-4]+'.txt')
                pdffil.set(fn_first+'.'+variant[:-4]+'.pdf')
                resframe.focus()
                book.select(3)                                                  # activate result tab
                logfil_entry.focus()                                            # activate as initial input box
                break                                                           # use name from 1st match
                
    except:                                                                     # catch *all* exceptions
        #e = sys.exc_info()[0]
        tb = sys.exc_info()[2]
        sub_issue("Problem in vary_settings_core.py")
        for ele in traceback.format_tb(tb):
            sub_issue(ele[:-1])                                                 # sub appends <CR>
        sub_issue(str(sys.exc_info()[1]))
        runState.set('Emulation broken ...  ')
        ttk.Label(runframe, textvariable=runState, style='Error.TLabel').grid(column=2, row=runRow, sticky=(W), padx=20, pady=10)
    runframe.update()                                                           # update frame display
    #log_msg("End of sub_emul reached")
    pass

def echo_version(mdl):
    global echo_msg
    #mdl= 'vary_settings_batch.py'
    stamp = os.stat(varyHome + mdl)
    stposx= datetime.fromtimestamp(stamp.st_mtime)
    ststr = datetime.strftime(stposx, "%Y-%m-%d %H:%M:%S")
    echo_msg[ststr] = mdl
    return 

varyHome= sys.argv[0]                           # command used to start this script
whereColon = varyHome.find(':')
if whereColon < 0:
    varyHome = os.getcwd()
varyHome = os.path.dirname(varyHome) + '\\'
m  = '='*66+'\nEcho of software versions used\n'+'-'*66
m +='\n vary_settings home directory  ' + varyHome
global echo_msg
echo_msg = {}
echo_version('vary_settings_GUI.py')
echo_version('vary_settings_core.py')
echo_version('determine_basal.py')
for ele in echo_msg:
    m += '\n dated: '+ele + ',   module name: '+echo_msg[ele]
m += '\n' + '='*66 + '\n'


runRow = 1
runframe.columnconfigure(0, weight=1)
runframe.rowconfigure(runRow+1, weight=1)

ttk.Label(runframe, text="Messages from Emulation").grid(column=0, row=runRow, sticky=(W), padx=5, pady=10)
ttk.Button(runframe, text="Run Emulation", command=sub_emul).grid( column=1, row=runRow, sticky=(E), padx=20, pady=5)
runState = StringVar()
notRunning ='                                   '                               # in prop. font as long as running
runState.set(notRunning)
tStyle.configure('Done.TLabel', foreground='green')
tStyle.configure('Error.TLabel', foreground='red')
ttk.Label(runframe, textvariable=runState).grid(column=2, row=runRow, sticky=(W), padx=20, pady=10)
lfd = Text(runframe, state='disabled', width=146, height=30)                    # w/h in characters
lfd.grid(column=0, row=runRow+1, columnspan=3)
lfd['wrap'] = 'none'
lfd.tag_configure('issue', foreground='red')
scrly = ttk.Scrollbar(runframe, orient=VERTICAL, command=lfd.yview)
scrly.grid(column=3, row=runRow+1, sticky=(W,N,S))
lfd['yscrollcommand'] = scrly.set
scrlx = ttk.Scrollbar(runframe, orient=HORIZONTAL, command=lfd.xview)
scrlx.grid(column=0, columnspan=5, row=runRow+2, sticky=(W,E,N))
lfd['xscrollcommand'] = scrlx.set
ttk.Button(runframe, text="Clear Messages", command=clear_msg).grid( column=0, row=runRow+0, sticky=(E), padx=20, pady=5)


how_to_print = 'GUI'
#how_to_print = 'print'                                                         # goes to DOS window; for debugging
set_tty(runframe, lfd, how_to_print)                                            # export print settings to main routine

wdir_entry.focus()                                                              # activate as initial input box
while True:
    root.mainloop()                                                             # was sometimes broken on return from parmeters_known or matplotlib, respectively
