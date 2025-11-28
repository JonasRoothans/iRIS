from classes.SearchThread import *
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from functions.support import cwdpath
import os
from classes.module import Module
from classes.moduleManager import ModuleManager
from classes.vote import Vote
from classes.member import Member
import webbrowser
import time
import json
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from functions.download import download_brieven, download_subtitles, download_votes, download_members, download_moties, download_raadsvoorstellen, download_amendementen,download_pdf,download_vragen,download_updates, download_meetings, web
import keywordAnalysis
from tkinter import simpledialog
import downloadPopup


class Iris:
    def __init__(self):
        #-- Presets
        self.MAX_PDF_LENGTH = 50000
        self.LINE_LENGTH = 80
        self.SEARCH_DELAY = int(300)

        #-- data
        self.all_items = []
        self.all_parents = {}
        self.pdf_texts = {}
        self.modules = {}
        self.types = {}


        #--ui
        self.root = None
        self.icons = {}
        self.tree = None
        self.search_pdf_toggle = None
        self.visible = {}
        self.expanded = False
        self.buttons = {}
        self.frames = {}

        #-- search engine
        self.searcher = SearchThread()
        self.last_search_time = time.time()
        self.search_after_id = None

        #-- download
        self.popup = None


        self.root = self.construct_UI()
        self.loadModules()
        self.root.mainloop()


    def loadModules(self):
        # Load data into Treeview (hierarchical structure)
        module_manager = ModuleManager()
        module_manager.addall()
        module_manager.sort_chronological()

        for module in module_manager.modules:
            if module.parent is None:
                self.addModuleToTree(module,'')  # use '' to insert into the root level

    def addModuleToTree(self,module,parent):
        node_id = self.tree.insert(
            parent,
            'end',
            text= self.getTitle(module),
            image=self.getIcon(module),
            tags=self.getTag(module),
            values=(module.date,
                    self.getTag(module),
                    self.getContext(module),
                    module.pdf_url,
                    module.meeting_url,
                    module.url)
        )

        self.all_items.append(node_id)
        self.all_parents[node_id] = parent
        self.modules[node_id] = module.module_id
        self.visible[node_id] = True
        self.pdf_texts[node_id] = self.getPDFText(module)
        self.types[node_id] = module.type

        if module.type and 'brief' in module.type and not self.buttons['rib'].get():
            self.tree.detach(node_id)


        for child_id in module.children:
            try:
                child = Module(child_id)
            except:
                print(f'could not load {child_id}')
                continue
            self.addModuleToTree(child,node_id)


    def getPDFText(self,module):
        if module.pdf_text is not None:
            return module.pdf_text[0:self.MAX_PDF_LENGTH].strip()
        else:
            return ''

    def getContext(self,module)->str:
        context = module.text
        if context is None:
            context = ''
        return self.wrapText(context,self.LINE_LENGTH)


    def wrapText(self,text,line_length):
        if text is None:
            return None
        # Base case: If text is shorter than or equal to the line length, return as-is
        if len(text) <= line_length:
            return text

        # Find the first space after the line_length characters
        space_index = text.find(' ', line_length)

        if space_index != -1:
            # Insert a newline at the first space after the line_length
            text = text[:space_index] + '\n' + text[space_index + 1:]

            # Recursively process the rest of the text
            return text[:space_index + 1] + self.wrapText(text[space_index + 1:], line_length)

        # If no space is found after the first line length, return the text as is
        return text

    def getTitle(self,module) -> str:
        if module.title is not None:
            return f'  {module.module_id} : {module.title.replace("Raadsvoorstel","")}'
        else:
            return ''

    def getIcon(self, module):
        #default:
        icon = self.icons['none']

        if module.type == 'Raadsvoorstel':
            icon = self.icons['doc']
            if module.result.lower() == 'verworpen':
                icon = self.icons['no']
            elif module.children:
                try:
                    modifications = [child for child in module.children if
                                     Module(child).result.lower() == 'aangenomen' or
                                     Module(child).result.lower() == 'ingetrokken na toezegging']
                except:
                    modifications = False
                if modifications:
                    icon = self.icons['notes']
                elif module.result.lower() == '':
                    icon = self.icons['doc']
                else:
                    icon = self.icons['afgerond']
            elif module.vote_id is None and module.result != '':
                icon = self.icons['hamer']
            elif module.result.lower() == 'afgerond':
                icon = self.icons['afgerond']
            elif module.result.lower() == 'aangenomen':
                icon = self.icons['afgerond']

        elif module.type == 'Amendement':
            if module.result.lower() == 'aangenomen':
                icon = self.icons['modified']
            elif module.result.lower() == 'verworpen':
                icon = self.icons['no']
            else:
                icon = self.icons['none']
        elif module.type == 'Toezegging':
            icon = self.icons['toezegging']
        elif module.type == 'Agenda':
            icon = self.icons['agenda']
        elif module.type == 'Raadsinformatiebrief' or module.type == 'Collegebrief' or module.type == 'Nieuwsbrief' or module.type == 'Burgemeesterbrief':
            icon = self.icons['brief']
        elif isinstance(module.module_id, str):
            if module.module_id.startswith('o'):
                icon = self.icons['orde']
        elif module.type is None:
            icon = self.icons['none']
        else:
            if module.result.lower() == 'verworpen':
                icon = self.icons['no']
            elif module.result.lower() == 'ingetrokken na toezegging':
                icon = self.icons['gone']
            elif module.result.lower() == 'ingetrokken':
                icon = self.icons['trash']
            elif module.result.lower() == 'aangenomen':
                icon = self.icons['yes']
            elif 'vervallen' in module.title.lower():
                icon = self.icons['trash']
            elif 'staken' in module.result.lower():
                icon = self.icons['error']
        return icon


    def getTag(self,module)->str:
        tag = ''
        if 194495 in module.member_id:
            label = f'{tag} VJ'
        elif 194375 in module.member_id:
            label = f'{tag} JR'
        return tag


    def expand_all(self, parent_node):
        children = self.tree.get_children(parent_node)
        for child in children:
            self.tree.item(child, open=True)
            self.expand_all(child)


    def collapse_all(self, parent_node):
        children = self.tree.get_children(parent_node)

        for child in children:
            self.tree.item(child, open=False)
            # Recursively collapse all its children
            self.collapse_all(child)

    def resetTree(self):
        for item in self.all_items:
            if not self.buttons['rib'].get() and self.types[item] and 'brief' in self.types[item]:
                self.tree.detach(item)
            else:
                self.tree.reattach(item,self.all_parents[item],'end')
                self.tree.item(item,tags=())


#---- buttons
    def open_meeting_link(self,event):
        selected_item = self.tree.selection()[0]
        link = self.tree.item(selected_item, 'values')[-2]
        if link:
            webbrowser.open_new(link)

    def open_module_link(self,event):
        selected_item = self.tree.selection()[0]
        link = self.tree.item(selected_item, 'values')[-1]
        if link:
            webbrowser.open_new(link)

    def open_pdf_link(self,event):
        selected_item = self.tree.selection()[0]
        link = self.tree.item(selected_item, 'values')[-3]
        if link:
            webbrowser.open_new(link)

    def update_votes(self,module_id):
        for widget in self.frames['vote'].winfo_children():
            widget.destroy()

        m = Module(module_id)
        if not m.vote_id:
            return

        v = Vote(m.vote_id)
        total_votes = len(v.member_votes)
        voor = {}
        tegen = {}
        for person, vote in v.member_votes.items():
            member = Member(person)
            if vote == 'voor':
                if member.party in voor:
                    voor[member.party] += 1
                else:
                    voor[member.party] = 1
            else:
                if member.party in tegen:
                    tegen[member.party] += 1
                else:
                    tegen[member.party] = 1
        x_offset = 0
        margin_fraction = 0.001
        for partij in voor:
            proportion = voor[partij] / total_votes
            if partij == 'Partij voor de Dieren':
                partij = 'PvdD'
            if 'ouderen' in partij.lower():
                partij = 'OA'
            label_text = partij
            label = ctk.CTkLabel(
                self.frames['vote'],
                text=label_text,
                fg_color="green")
            label.place(relx=x_offset + margin_fraction, relwidth=proportion - 2 * margin_fraction, relheight=1.0)
            x_offset += proportion

        for partij in tegen:
            proportion = tegen[partij] / total_votes
            if partij == 'Partij voor de Dieren':
                partij = 'PvdD'
            if 'ouderen' in partij.lower():
                partij = 'OA'
            label_text = partij
            label = ctk.CTkLabel(
                self.frames['vote'],
                text=label_text,
                fg_color="red")
            label.place(relx=x_offset + margin_fraction, relwidth=proportion - 2 * margin_fraction, relheight=1.0)
            x_offset += proportion

    def apply_search_result(self, result):
        """Apply the search result:
        - Show/hide nodes based on result['show']
        - Tag nodes with `match` for highlighting"""

        counter =0
        for node_id, node_info in result.items():
            # Detach if 'show' is False
            if node_info['show']:
                # Check if it's hidden, then reattach otherwise ignore
                self.tree.reattach(node_id, self.all_parents[node_id], 'end')
            else:
                # Detach the node if not to be shown
                self.tree.detach(node_id)

            # Highlight if 'match' is True
            if node_info['match']:
                counter += 1
                self.tree.item(node_id, tags='match')  # Apply highlight tag
            else:
                self.tree.item(node_id, tags='')  # Remove any highlight

        self.update_activity(f'{self.search_entry.get()} is {counter}x gevonden.')
    def update_activity(self,text):
        self.activity.configure(text=text)

    #---- binds
    def bind_f1_event(self,event):
        if self.expanded:
            self.collapse_all('')
        else:
            self.expand_all('')
        self.expanded = not self.expanded

    def bind_search_query_change(self,event):
        typed = self.search_entry.get().lower()
        if len(typed) < 3:
            self.resetTree()
            return

        if self.search_after_id:
            self.root.after_cancel(self.search_after_id)

        # Schedule a new search after 300ms (0.3 seconds)
        self.search_after_id = self.root.after(self.SEARCH_DELAY, lambda: self.searcher.start_search(self,typed))




    def bind_item_selected(self,event):
        selected_item = self.tree.focus()  # Get currently selected item
        link = self.tree.item(selected_item, 'values')[-3]

        if link == 'None':
            self.buttons['pdf'].configure(state="disabled")
        else:
            self.buttons['pdf'].configure(state="normal")

        if self.tree.item(selected_item, 'values')[-2] == 'None':
            self.buttons['meeting'].configure(state="disabled")
        else:
            self.buttons['meeting'].configure(state="normal")

        if self.tree.item(selected_item, 'values')[-1] == 'None':
            self.buttons['module'].configure(state="disabled")
        else:
            self.buttons['module'].configure(state="normal")

        # update votes:
        self.update_votes(self.modules[selected_item])



    def menu_datum_aanpassen(self):
        settings = self.menu_get_settings()
        settings['last_update'] = simpledialog.askstring(title="iRIS", prompt="Datum laatste update? [dd-mm-yyyy]:")
        self.menu_save_settings(settings)

        new_label=f"Update vanaf {settings['last_update']} met {settings['buffer_months']} maanden buffer"
        self.download_menu.entryconfig(2, label=new_label)
        
    def menu_buffer_aanpassen(self):
       settings = self.menu_get_settings()
       settings['buffer'] = simpledialog.askinteger(title="iRIS", prompt="Hoeveel maanden buffer?")
       self.menu_save_settings(settings)

       new_label=f"Update vanaf {settings['last_update']} met {settings['buffer_months']} maanden buffer"
       self.download_menu.entryconfig(2, label=new_label)

    def menu_update(self):
        self.popup = downloadPopup.downloadPopup()
        self.start_threaded_downloads()

    def start_threaded_downloads(self):
        task_thread = threading.Thread(target=self.run_sequential_downloads)
        task_thread.start()

    def run_sequential_downloads(self):
        settings = self.menu_get_settings()
        date = datetime.strptime(settings['last_update'],'%d-%m-%Y')
        start_date = date - relativedelta(months=settings['buffer_months'])
        driver = web.setup_driver()
        for tag in self.popup.tags:
            self.root.after(0, self.popup.start_task,tag)
            if tag=='Stemmen':
                print('Stemmen')  # todo: weghalen
                #download_votes.download_votes(driver, start_date)

            if tag =='Meetings':
                print('Meetings')
                download_meetings.download_meetings(start_date)

            if tag=='Moties':
                print('Moties')
                download_moties.download_moties(driver, start_date)

            if tag=='Raadsvoorstellen':
                print('Raadsvoorstellen')  # todo: weghalen
                web.teardown_driver(driver)
                driver = web.setup_driver()
                download_raadsvoorstellen.download_raadsvoorstellen(driver, start_date)

            if tag=='Amendementen':
                print('Amendementen')  # todo: weghalen
                web.teardown_driver(driver)
                driver = web.setup_driver()
                download_amendementen.download_amendementen(driver, start_date)

            if tag=='Brieven':
                print('DEBUG')  # todo: weghalen
                download_brieven.download_brieven(driver, start_date)

            if tag=='Bijlages':
                print('DEBUG')  # todo: weghalen
                download_pdf.download_pdf(start_date)

            if tag=='Vragen':
                print('Vragen')  # todo: weghalen
                web.teardown_driver(driver)
                driver = web.setup_driver()
                download_vragen.download_vragen(driver, start_date)
            if tag=="Keywords":
                keywordAnalysis.keywordAnalysis()

            if tag=="Updates":
                print('updates')
                web.teardown_driver(driver)
                driver = web.setup_driver()
                download_updates.download_updates(driver, start_date)


            self.root.after(0,self.popup.finish_task,tag)
        settings['last_update'] = date.today().strftime('%d-%m-%Y')
        self.menu_save_settings(settings)

    def menu_get_settings(self):
        settings_path = cwdpath(os.path.join('json', 'settings.json'))
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as file:
                return json.load(file)

        else:
            settings = {}
            settings['last_update'] = '01-04-2022'
            settings['buffer_months'] = 3
            self.menu_save_settings(settings)
            return settings

    def menu_save_settings(self,settings):
        settings_path = cwdpath(os.path.join('json', 'settings.json'))
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

    def construct_UI(self):
        self.root = ctk.CTk()
        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode("light")
        self.root.title("iRIS / powered by Partij voor de Dieren")
        self.root.geometry("1500x800")


        #UI elements
        # --- Menu
        menubar = tk.Menu(self.root)
        settings = self.menu_get_settings()


        download_menu = tk.Menu(self.root, tearoff=0)
        menubar.add_cascade(label="Download",menu=download_menu)
        # Add options to the "Download" menu
        download_menu.add_command(label="Datum aanpassen", command=self.menu_datum_aanpassen)
        download_menu.add_command(label="Buffer aanpassen", command=self.menu_buffer_aanpassen)

        download_menu.add_command(label=f"Update vanaf {settings['last_update']} met {settings['buffer_months']} maanden buffer", command=self.menu_update)

        self.root.config(menu=menubar)
        self.download_menu = download_menu









        # ---Search frame
        search_frame = ctk.CTkFrame(self.root)
        search_frame.pack(pady=0, padx=0, fill="y", side="left")
        titel = ctk.CTkLabel(master=search_frame,
                             text='iRIS',
                             font=(None, 30))
        subtitel = ctk.CTkLabel(master=search_frame,
                                text='Powered By PvdD - v24.10',
                                font=(None, 15))
        titel.pack(pady=(20, 0))
        subtitel.pack()

        search_entry = ctk.CTkEntry(master=search_frame,
                                    placeholder_text="Zoeken..",
                                    font=("Roboto", 20),
                                    justify="center",
                                    width=200)
        search_entry.pack(pady=(20,0), padx=10)
        activity = ctk.CTkLabel(master=search_frame,
                                text='',
                                font=(None, 10))
        activity.pack(pady=0,padx=0)

        switch_frame = ctk.CTkFrame(search_frame)
        switch_frame.pack(pady=10, padx=30, fill="y")

        search_pdf_toggle = ctk.CTkSwitch(master=switch_frame, text="Doorzoek bijlage", command = lambda: self.bind_search_query_change('pdf_toggle'))
        search_pdf_toggle.grid(row=1, column=1, sticky="w", pady=5, padx=10)

        search_show_rib = ctk.CTkSwitch(master=switch_frame, text="Doorzoek brieven",command=lambda: self.bind_search_query_change('brieven'))
        search_show_rib.grid(row=2, column=1, sticky="w", pady=5, padx=10)

        # Create two buttons: One for each type of action
        btn_frame = ctk.CTkFrame(search_frame)
        btn_frame.pack(pady=10, padx=20, fill="x", side='bottom')

        btn_meeting = ctk.CTkButton(btn_frame, text="Ga naar de vergadering", command=lambda: self.open_meeting_link(None))
        btn_meeting.pack(side="bottom", padx=10, pady=10, fill='x')

        btn_module = ctk.CTkButton(btn_frame, text="Ga naar de module", command=lambda: self.open_module_link(None))
        btn_module.pack(side="bottom", padx=10, pady=10, fill='x')

        btn_pdf = ctk.CTkButton(btn_frame, text="Open PDF",command=lambda: self.open_pdf_link(None))
        btn_pdf.pack(side="bottom", padx=10, pady=10, fill='x')


        #-- Tree frame
        tree_frame = ctk.CTkFrame(self.root)
        tree_frame.pack(pady=20, padx=20, fill="both", expand=True)
        tree = ttk.Treeview(tree_frame, columns=('Dag', 'Label', 'Info'))

        tree.heading('#0', text='Title')
        tree.heading('Dag', text="Dag")
        tree.heading('Label', text="Label")
        tree.heading('Info', text="Info")

        tree.column('#0', width=350)
        tree.column('Dag', width=5)
        tree.column('Label', width=5)
        tree.column('Info', width=400)

        scrollbar = ctk.CTkScrollbar(tree_frame, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(fill="both", expand=True)

        #-- Vote frame
        vote_frame = ctk.CTkFrame(self.root, height=30)
        vote_frame.pack(pady=10, padx=10, fill='x')


        #Load images
        self.icons['doc'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Text.png")))
        self.icons['script'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Script.png")))
        self.icons['none'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Question.png")))
        self.icons['yes'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Yes.png")))
        self.icons['no'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "No.png")))
        self.icons['toezegging'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Comment.png")))
        self.icons['agenda'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Calendar.png")))
        self.icons['gone'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Smile.png")))
        self.icons['trash'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Trash.png")))
        self.icons['error'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Warning.png")))
        self.icons['notes'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Notes.png")))
        self.icons['modified'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Modify.png")))
        self.icons['orde'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Wrench.png")))
        self.icons['brief'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Mail.png")))
        self.icons['hamer'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Volume.png")))
        self.icons['afgerond'] = tk.PhotoImage(
            file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Good mark.png")))



        #Design and style
        # Apply statuses as row background colors
        style = ttk.Style()
        style.configure("Treeview", rowheight=60, font=(None, 12))

        tree.tag_configure("parent", background='#ffffff')
        tree.tag_configure("child", background='#dddddd')
        tree.tag_configure("match", background='#a8c7aa')
        tree.tag_configure("highlightchild", background='#a8c7aa')

        style.map('Treeview', background=[('selected', '#7f8cab')])


        #Binds
        self.root.bind('<F1>', self.bind_f1_event)
        search_entry.bind('<KeyRelease>', self.bind_search_query_change)
        tree.bind('<<TreeviewSelect>>', self.bind_item_selected)

        #collect handles
        self.tree = tree
        self.search_entry = search_entry
        self.search_pdf_toggle = search_pdf_toggle
        self.search_show_rib = search_show_rib
        self.activity = activity
        self.buttons['meeting'] = btn_meeting
        self.buttons['module'] = btn_module
        self.buttons['pdf'] = btn_pdf
        self.buttons['rib'] = search_show_rib
        self.frames['tree'] = tree_frame
        self.frames['btn'] = btn_frame
        self.frames['switch'] = switch_frame
        self.frames['vote'] = vote_frame


        return self.root



if __name__=='__main__':
    Iris()


