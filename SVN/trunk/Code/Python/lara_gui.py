import os
import pathlib
import re
import subprocess
import sys
import time

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

import lara_utils
import lara_edit

class LaraShellWindowApp:

    def __init__(self):

        self.root = tk.Tk()

        self.proc = None

        cFont = 'sans-serif 12'
        cFontMono = 'courier 11'
        cFontBold = f'{cFont} bold'
        cFontMonoBold = f'{cFontMono} bold'
        cButtonWidth = 14
        cColumn0Width = 400
        cPadding = 6

        style = ttk.Style()
        style.configure( "TButton", font=cFont, width=cButtonWidth, borderwidth=2, padx=cPadding , pady=cPadding )
        self.root.option_add("*TCombobox*Listbox*Font", cFont)

        self.title = 'LARA Commands'
        self.root.title( self.title )

        contentButtons = [
            { 
                "text": "Treetagger", 
                "tooltip" : "Run the treetagger command for the selected content",
                "command": self.on_click_treetagger
            },
            { 
                "text": "Resources", 
                "tooltip" : "Run the resources command for the selected content",
                "command": self.on_click_resources
            },
            { 
                "text": "Word Pages", 
                "tooltip" : "Run the word_pages command for the selected content",
                "command": self.on_click_word_pages
            },
            { 
                "text": "Open in Browser", 
                "tooltip" : "Open the hyperlinked text file in your browser",
                "command": self.on_click_open_in_browser
            },
            { 
                "text": "Refresh List", 
                "tooltip" : "Refresh the list of contents",
                "command": self.on_click_refresh_contents
            },
        ]

        row = 0
        aLabel = tk.Label(self.root, text='Select one of the contents below and click the appropriate button', font=cFontBold)
        aLabel.grid( column=0, row=row, columnspan=2, sticky='w', padx=cPadding)
        row += 1

        aFrame = self.create_frame(cColumn0Width, 200, 0, row, 1, len(contentButtons), cPadding )
        self.contents_list = tk.Listbox(aFrame, font=cFontMono, width=4*cButtonWidth )
        self.contents_list.bind('<<ListboxSelect>>', self.on_contents_selected_index_changed)
        self.lastSelectedIndex = -1
        self.contents_list.grid( sticky='news' )
        self.add_scrollbar_to_frame( aFrame, self.contents_list, tk.VERTICAL)

        for buttonDescriptor in contentButtons:
            aButton = ttk.Button(self.root, text=buttonDescriptor['text'], command=buttonDescriptor['command'])
            aButton.grid( column=1, row=row, sticky='w', padx=cPadding )
            CreateToolTip( aButton, buttonDescriptor['tooltip'])
            row += 1

        # TODO: Batch recording only on Windows so far
        if sys.platform.startswith("win32"):
            self.batchButtonText = tk.StringVar()
            self.batchButton = ttk.Button(self.root, textvariable=self.batchButtonText, command=self.on_click_batch)
            self.batchButton.grid( column=1, row=row, sticky='w', padx=cPadding, pady=cPadding )
            self.batchButtonText.set( "Record Batch")
            CreateToolTip( self.batchButton, "Record commands in batch file")
            self.batch_recording = False
            self.batch_commands = []
            self.batch_directory = os.path.abspath(os.environ['LARA'])
            row += 1

        aLabel = tk.Label(self.root, text='Choose a file to edit and click the button', font=cFontBold)
        aLabel.grid( column=0, row=row, columnspan=2, sticky='w', padx=cPadding )
        row += 1

        allFileOptions = list(lara_edit.EditFileIds.keys())
        self.fileOptions = ttk.Combobox( self.root, font=cFont, state="readonly", values=allFileOptions) 
        self.fileOptions.set( allFileOptions[0] )
        self.fileOptions.grid( column=0, row=row, sticky='we', padx=cPadding )
        
        aButton = ttk.Button(self.root, text='Edit', command=self.on_click_edit)
        aButton.grid( column=1, row=row, sticky='w', padx=cPadding)
        CreateToolTip( aButton, "Edit the file")
        row += 1

        aLabel = tk.Label(self.root, text='Enter the ID of a new content and click the button', font=cFontBold)
        aLabel.grid( column=0, row=row, columnspan=2, sticky='w', padx=cPadding )
        row += 1

        self.newcontent_entry = tk.Entry(self.root, font=cFont)
        self.newcontent_entry.grid( column=0, row=row, sticky='we', padx=cPadding)
        aButton = ttk.Button(self.root, text='Create', command=self.on_click_new_content)
        aButton.grid( column=1, row=row, sticky='w', padx=cPadding)
        CreateToolTip( aButton, "Create the new content")
        row += 1

        aLabel = tk.Label(self.root, text='Convert audio directory to MP3. Enter a directory name or choose one, then click the button', font=cFontBold)
        aLabel.grid( column=0, row=row, columnspan=2, sticky='w', padx=cPadding )
        row += 1

        self.audiodir_entry = tk.Entry(self.root, font=cFont)
        self.audiodir_entry.grid( column=0, row=row, sticky='we', padx=cPadding)
        aButton = ttk.Button(self.root, text='Choose ...', command=self.on_click_choosefolder)
        aButton.grid( column=1, row=row, sticky='w', padx=cPadding)
        CreateToolTip( aButton, "Choose a directory for audio conversion")
        row += 1
        
        aButton = ttk.Button(self.root, text='Convert', command=self.on_click_convert_audiodir)
        aButton.grid( column=1, row=row, sticky='w', padx=cPadding)
        CreateToolTip( aButton, "Convert the files in the audio directory")
        row += 1

        aLabel = tk.Label(self.root, text='Output:', font=cFontBold)
        aLabel.grid( column=0, row=row, sticky='w', padx=cPadding )
        row += 1

        # NOT YET! (If at all)
        # aButton = tk.Button(self.root, text='Kill Process', font=cFont, width=cButtonWidth, command=self.kill_proc)
        # aButton.grid( column=1, row=8, sticky='w', padx=cPadding )

        aFrame = self.create_frame(600, 200, 0, row, 2, 1, cPadding)
        self.output_text = LaraOutputText(aFrame, font=cFontMono, undo=True, wrap='none')
        self.output_text.config(state=tk.DISABLED)
        self.output_text.grid(sticky='news')
        self.output_text.tag_config('warning', foreground="black", background="orange" )
        self.output_text.tag_config('error', foreground="white", background="red" )
        self.output_text.tag_config('gui', foreground="blue", background="white" )
        self.add_scrollbar_to_frame( aFrame, self.output_text, tk.VERTICAL)
        self.add_scrollbar_to_frame( aFrame, self.output_text, tk.HORIZONTAL)
        row += 1
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(row-1, weight=2)
        
        aLabel = tk.Label(self.root, text='')
        aLabel.grid( column=0, row=row, columnspan=2, sticky='w', padx=cPadding)
        row += 1

        self.refresh_contents()

        self.center()


    def add_scrollbar_to_frame( self, frame, widget, orient=tk.VERTICAL ):
        if orient == tk.VERTICAL:
            scrollbar = tk.Scrollbar(frame, command=widget.yview, orient=orient)
            scrollbar.grid(row=0, column=1, sticky='ns')
            widget['yscrollcommand'] = scrollbar.set
        if orient == tk.HORIZONTAL:
            scrollbar = tk.Scrollbar(frame, command=widget.xview, orient=orient)
            scrollbar.grid(row=1, column=0, sticky='nsew')
            widget['xscrollcommand'] = scrollbar.set

    def refresh_contents(self):
        currentConfig = self.get_current_config(False) # keep the current selection
        laraContentDir = lara_utils.absolute_file_name('$LARA/Content')
        allConfigFiles = [ str(path) for path in pathlib.Path(laraContentDir).glob('*/corpus/*.json') ]
        self.contentRepository = []
        self.contents_list.delete(0, tk.END) 
        for configFile in allConfigFiles:
            fileAdded = False
            try:
                configData = lara_utils.read_json_file(configFile)
                if configData and 'id' in configData and 'corpus' in configData:
                    if lara_utils.is_valid_contentid( configData['id'] ):
                        self.contentRepository.append( ( configFile, configData ) )
                        fileAdded = True
            except:
                pass   
            if not fileAdded:
                pass
                # self.add_gui_output( f'skipping {configFile} (no valid config file)' )
        maxidlen = 0                
        for entry in self.contentRepository:
            configFile, configData = entry
            idlen = len(configData["id"])
            if idlen > maxidlen: maxidlen = idlen
        for entry in self.contentRepository:
            configFile, configData = entry
            item = f'{configData["id"].ljust(maxidlen)} | file: ' + configFile[len(laraContentDir)+1:]
            self.contents_list.insert(tk.END, item )
        # restore selection
        self.set_current_config( currentConfig )

    def create_frame(self,width,height,column,row,columnspan,rowspan, padx):
        frm = tk.Frame(self.root, width=width, height=height)
        frm.grid(column=column, row=row, columnspan=columnspan, rowspan=rowspan, sticky='news', padx=padx)
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(0, weight=1)
        return frm

    def get_current_config(self, alert = True):
        try:
            index = int(self.contents_list.curselection()[0])
            return self.contentRepository[index]
        except:
            pass
        if alert:
            tk.messagebox.showerror( self.title, "Select a content from the list first")
        return None

    def set_current_config(self, config):
        if not config:
            return
        for index in range(0, len(self.contentRepository)):
            if self.contentRepository[index][0] == config[0]:
                self.contents_list.selection_set( index )
                break

    def try_run_command( self, mode ):
        configEntry = self.get_current_config()
        if configEntry is None:
            return
        configFile = configEntry[0]
        self.run_lara( [ mode, configFile ] )

    def run_lara( self, parameters ):
        if self.proc is not None and self.proc.poll() is None:
            tk.messagebox.showerror(self.title, 'Process already on progress. Wait for it to finish!')
            return
        self.output_text.clear()
        self.root.update()
        # Quick and Dirty switch to see if we're running under Python or "lara_run.exe"
        # Surely there must be more clever/cleaner ways to do this!
        if sys.executable.lower().find( 'lara_run' ) >= 0:
            popen_args = [ sys.executable ] + parameters
        else:
            # Executable is "python" (or maybe "python3", or even "py"?)
            lararun_file = lara_utils.absolute_filename_in_python_directory('lara_run.py')
            popen_args = [ sys.executable, '-u', lararun_file ] + parameters
        if self.batch_recording:
            self.batch_commands.append( popen_args )            
        self.add_gui_output( f'Start Process')
        self.add_gui_output( f'Process args: {popen_args}')
        self.proc = subprocess.Popen( popen_args,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.root.after_idle(self.poll_proc)
    
    def poll_proc(self):
        if self.proc == None:
            self.proc_finished()
            return
        line = self.proc.stdout.readline().decode( 'iso-8859-1' ) # TODO: LARA output ancoding encoding always ANSI? 
        if line != '':
            line = line.strip().rstrip()
            self.output_text.append( f'{line}\n' )
            lara_utils.print_and_flush( line )
            self.root.update()
        elif self.proc.poll() is not None:
            self.proc = None
        self.root.after(0, self.poll_proc) # poll again in any case until proc is None, so we have a single point at which the proc has ended

    def proc_finished(self):
        # work after the proc has ended
        self.refresh_contents()
        ( errors, warnings ) = self.output_text.tally();
        self.add_gui_output( f'End Process: {errors} error(s), {warnings} warning(s)')
        self.output_text.highlight_output_from_lara()
        if errors > 0:
            tk.messagebox.showerror(self.title, 'Process completed with error(s).\nCheck the output!' )

    def add_gui_output(self, text):
        lara_utils.print_and_flush( f'=== GUI: {text}')
        self.output_text.append( f'=== {text}\n')

    def kill_proc(self):
        if self.proc is not None and self.proc.poll() is None:
            add_gui_output( f'***** KILLING PROCESS... *****')
            self.proc.kill()

    def center(self):
        win = self.root
        win.update_idletasks()
        width = 2 * win.winfo_screenwidth() // 3
        height = 2 * win.winfo_screenheight() // 3
        x = win.winfo_screenwidth() // 2 - width // 2
        y = win.winfo_screenheight() // 2 - height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()

    def confirm( self, question ):
        return tk.messagebox.askyesno( self.title, question )

    def save_batch_commands( self, batchfile ):
        batchlines = self.get_batch_prolog() + [ self.get_batch_line( params ) for params in self.batch_commands ] + self.get_batch_epilog()
        batchfile.write( "\n".join( batchlines ) )

    def get_batch_line( self, params ):
        batchparams = [ self.get_batch_parameter( param ) for param in params ]
        return " ".join( batchparams )

    def get_batch_parameter( self, param ):
        laradir = os.path.abspath(os.environ['LARA'])
        if param == sys.executable:
            param = "%PYEXE%"
        elif param[:len(laradir)].replace( "\\", "/" ) == laradir.replace( "\\", "/" ):
            param = "%LARA%" + param[len(laradir):]
        return param if param.find( " " ) < 0 else f'\"{param}\"' 

    def get_batch_prolog( self ):
        return [
            "@echo off",
            "",
            "if %LARA%.==. (",
            "\techo LARA environment variable not set",
            "\tgoto end",
            ")",
            "",
            "if %TREETAGGER%.==. (",
            "\techo TREETAGGER environment variable not set",
            "\tgoto end",
            ")",
            "",
            f"set PYEXE={sys.executable}",
            "",
        ]

    def get_batch_epilog( self ):
        return [ 
            "",
            ":end" 
        ]

    # ----- events -----

    def on_click_refresh_contents(self):
        self.refresh_contents()

    def on_click_treetagger(self):
        if not self.confirm( 'This will override your current tagged corpus file. Are you sure you want to continue?'):
            return
        self.try_run_command('treetagger' )

    def on_click_resources(self):
        self.try_run_command('resources' )

    def on_click_word_pages(self):
        self.try_run_command('word_pages' )

    def on_click_open_in_browser(self):
        self.try_run_command('open_in_browser' )

    def on_click_new_content(self):
        self.run_lara( [ 'newcontent', self.newcontent_entry.get() ])
        return

    def on_click_edit(self):
        configEntry = self.get_current_config()
        if configEntry != None:
            fileOption = self.fileOptions.get()
            configFile = configEntry[0]
            self.run_lara( [ 'edit', fileOption, configFile ])
        return

    def on_click_choosefolder(self):
        folder_selected = tk.filedialog.askdirectory()
        if folder_selected and folder_selected != '':
            self.audiodir_entry.delete(0, tk.END)
            self.audiodir_entry.insert(0, folder_selected)

    def on_click_convert_audiodir(self):
        self.run_lara( [ 'audio_dir_to_mp3', self.audiodir_entry.get() ])
        return

    def on_click_batch(self):
        if self.batch_recording:
            CreateToolTip( self.batchButton, "Record commands in batch file")
            self.batchButtonText.set( "Record Batch")
            if len(self.batch_commands) > 0:
                options = {
                    'defaultextension' : '.bat',
                    'filetypes' : [ ('batch files', '.bat'), ('all files', '.*') ],
                    'title' : 'Save Batch File...',
                    'initialdir': self.batch_directory,
                    'mode' : 'w'
                }
                batchfile = tk.filedialog.asksaveasfile( **options )
                if batchfile is not None: # dialog closed with "OK".
                    self.batch_directory = os.path.dirname( batchfile.name )
                    self.save_batch_commands( batchfile )
                    batchfile.close()
            self.batch_recording = False
        else:
            CreateToolTip( self.batchButton, "Stop recording and save batch file")
            self.batchButtonText.set( "Stop Recording")
            self.batch_commands.clear()
            self.batch_recording = True

    def on_contents_selected_index_changed(self, evt):
        # changing the index in the combobox below will deselect the item in the listbox above!
        # make sure the last item in the list box gets re-selected here
        if len(self.contents_list.curselection()) == 0:
            if self.lastSelectedIndex >= 0:
                self.contents_list.selection_set( self.lastSelectedIndex )
        else:                
            self.lastSelectedIndex = self.contents_list.curselection()[0]

class LaraOutputText(tk.Text):
    
    def __init__(self, *args, **kwargs):
        self.info_re = re.compile( '^---.*$' )
        self.warning_re = re.compile( '^\*\*\* Warning:.*$', re.MULTILINE )
        self.error_re1 = re.compile( '^\*\*\* Error:.*$', re.MULTILINE )
        self.error_re2 = re.compile( '^Traceback.*', re.DOTALL )
        self.gui_re = re.compile( '^===.*$', re.MULTILINE )
        tk.Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=False):
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)
        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit", count=count, regexp=regexp)
            if index == "": break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")

    def highlight_output_from_lara(self):
        self.highlight_pattern(self.warning_re.pattern,'warning', regexp=True)
        self.highlight_pattern(self.error_re1.pattern,'error', regexp=True)
        self.highlight_pattern(self.error_re2.pattern,'error', regexp=True)
        self.highlight_pattern(self.gui_re.pattern,'gui', regexp=True)

    def clear(self):
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.config(state=tk.DISABLED)
    
    def tally(self):
        text = self.get(1.0,tk.END)
        errors = len(self.error_re1.findall(text)) + len(self.error_re2.findall(text))
        warnings = len(self.warning_re.findall(text))
        return ( errors, warnings )

    def append(self, line ):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, line)
        self.see(tk.END)
        self.config(state=tk.DISABLED)
        # Performace issue when called too often  
        # (e.g. "word_pages" for Alice which gives man "*** Warning: unable to add audio for ...")
        # if len(line) > 3 and line[0:4] == '*** ':
        #     self.highlight_output()

# =============================================================================================
""" tk_ToolTip_class101.py
gives a Tkinter widget a tooltip as the mouse is above the widget
tested with Python27 and Python34  by  vegaseat  09sep2014
www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

Modified to include a delay time by Victor Zaccardo, 25mar16
"""

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 32
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#fffff8", relief='solid', borderwidth=1,
                       wraplength = self.wraplength,
                       font = 'sans-serif 10')
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

# =============================================================================================

def check_environment():
    Var = 'LARA'
    if not lara_utils.check_environment_variable_directory(Var):
        message = f'The environment variable {Var} is not set\nor does not contain a valid directory.'
        tk.messagebox.showerror('Error', message)
        return False
    return True

def main( Args ):
    if check_environment():
        app = LaraShellWindowApp()
        # Maximize Window at startup: app.root.wm_state('zoomed')
        app.root.mainloop()

if __name__=='__main__':
    from sys import argv
    main( argv[1:] )

