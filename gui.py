import os
import json
import webbrowser
import customtkinter as ctk
from classes.moduleManager import ModuleManager
import tkinter as tk
from tkinter import ttk
from classes.module import Module
from classes.vote import Vote
from classes.member import Member
from PIL import Image, ImageTk
from functions.support import cwdpath


# Function to create the tree structure based on the JSON data
def load_data_into_treeview(tree, parent_node, module):
    global icon_doc
    # Create a row for the parent with status color.
    # if module.result:
    #     if module.result.lower() == 'aangenomen':
    #         status_color = 'green'
    #     elif module.result.lower() == 'afgerond':
    #         status_color = 'green'
    #     elif module.result.lower() == 'verworpen':
    #         status_color = 'red'
    #     elif module.result.lower() == 'ingetrokken na toezegging':
    #         status_color = 'yellow'
    #     else:
    #         status_color = 'white'
    # elif module.type:
    #     if module.type.lower() == 'toezegging':
    #         status_color = 'grey'
    #     else:
    #         status_color = 'white'
    # else:
    #     status_color = 'white'




    if module.title is not None:
        text = module.title.replace("Raadsvoorstel","")
    else:
        text = ''


    if module.module_id is None:
        print('wat?')

    label = ''
    if 194495 in module.member_id:
        label = f'{label} VJ'
    elif 194375 in module.member_id:
        label = f'{label} JR'

    context = module.text
    if context is None:
        context = ''

    # Insert the title of the instrument into the Treeview
    node_id = tree.insert(
        parent_node,
        'end',
        text=f'  {text}',
        image=determine_icon(module),
        tags=determine_tag(module),
        values=(module.date, label, wrapText(context), module.pdf_url, module.meeting_url, module.url)
    )
    all_items.append(node_id)
    all_items_parents[node_id]  = parent_node
    modules[node_id] = module.module_id
    if module.pdf_text is not None:
        pdf_texts[node_id] = module.pdf_text[0:5000].strip()
    else:
        pdf_texts[node_id] = ''

    # Add children nodes recursively (if they exist)
    for child_id in module.children:
        try:
            child = Module(child_id)
        except:
            print(f'could not load {child_id}')
            continue
        load_data_into_treeview(tree, node_id, child)
    return tree

def determine_tag(module):
    if module.parent is None:
        tag  = 'parent'
    else:
        tag = 'child'
    return (tag,)
def determine_icon(module):
    icon = icon_none
    # --- determine icons:
    if module.type == 'Raadsvoorstel':
        icon = icon_doc
        if module.result.lower() == 'verworpen':
            icon = icon_no
        elif module.children:
            try:
                modifications = [child for child in module.children if Module(child).result.lower()=='aangenomen' or Module(child).result.lower()=='ingetrokken na toezegging']
            except:
                modifications = False
            if modifications:
                icon = icon_notes
    elif module.type == 'Amendement':
        if module.result.lower() == 'aangenomen':
            icon = icon_modified
        elif module.result.lower() == 'verworpen':
            icon = icon_no
        else:
            icon = icon_none
    elif module.type == 'Toezegging':
        icon = icon_toezegging
    elif module.type == 'Agenda':
        icon = icon_agenda
    elif isinstance(module.module_id,str):
        if module.module_id.startswith('o'):
            icon = icon_orde
    elif module.type is None:
        icon = icon_none
    else:
        if module.result.lower() == 'verworpen':
            icon = icon_no
        elif module.result.lower() == 'ingetrokken na toezegging':
            icon = icon_gone
        elif module.result.lower() ==  'ingetrokken':
            icon = icon_trash
        elif module.result.lower() == 'aangenomen':
            icon = icon_yes
        elif 'vervallen' in module.title.lower():
            icon = icon_trash
        elif 'staken' in module.result.lower():
            icon = icon_error
        else:
            icon = icon_none
    return icon
def combine_icons(base,overlay):
    # Paste the tick (icon_ok) on top of the document (icon_doc)
    base.paste(overlay, (0, 0), overlay)  # (0, 0) is the top-left corner

    # Convert back to a format Tkinter can use
    combined_icon = ImageTk.PhotoImage(base)

    return combined_icon


# Open meeting or PDF link
def open_meeting_link(event):
    selected_item = tree.selection()[0]
    link = tree.item(selected_item, 'values')[-2]
    if link:
        webbrowser.open_new(link)

def open_module_link(event):
    selected_item = tree.selection()[0]
    link = tree.item(selected_item, 'values')[-1]
    if link:
        webbrowser.open_new(link)

def open_pdf_link(event):
    selected_item = tree.selection()[0]
    link = tree.item(selected_item, 'values')[-3]
    if link:
        webbrowser.open_new(link)


# Function to expand all treeview items
def expand_all(tree, parent_node):
    # Get all children of the current node
    children = tree.get_children(parent_node)

    for child in children:
        # Expand this child
        tree.item(child, open=True)
        # Recursively expand all its children
        expand_all(tree, child)

# Function to collapse all treeview items
def collapse_all(tree, parent_node):
    # Get all children of the current node
    children = tree.get_children(parent_node)

    for child in children:
        # Collapse this child
        tree.item(child, open=False)
        # Recursively collapse all its children
        collapse_all(tree, child)


# Event handler for when F1 is pressed, expand all items in the tree
def handle_f1_event(event):
    global expanded  # Use a global flag to track the current state of treeview

    if expanded:
        # If tree is currently expanded, then collapse all items
        collapse_all(tree, '')
    else:
        # If tree is currently collapsed, then expand all items
        expand_all(tree, '')

    # Toggle the expanded flag
    expanded = not expanded


def wrapText(text, line_length=80):

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
        return text[:space_index + 1] + wrapText(text[space_index + 1:], line_length)

    # If no space is found after the first line length, return the text as is
    return text

# Event handler for clicking on a row
def on_item_selected(event):
    selected_item = tree.focus()  # Get currently selected item
    link = tree.item(selected_item, 'values')[-3]

    if link=='None':
        btn_pdf.configure(state="disabled")
    else:
        btn_pdf.configure(state="normal")

    if tree.item(selected_item, 'values')[-2]=='None':
        btn_meeting.configure(state="disabled")
    else:
        btn_meeting.configure(state="normal")

    if tree.item(selected_item, 'values')[-1] == 'None':
        btn_module.configure(state="disabled")
    else:
        btn_module.configure(state="normal")

    #update votes:
    update_votes(modules[selected_item])

def update_votes(module_id):
    for widget in vote_frame.winfo_children():
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
        if vote=='voor':
            if member.party in voor:
                voor[member.party] += 1
            else:
                voor[member.party] =1
        else:
            if member.party in tegen:
                tegen[member.party] += 1
            else:
                tegen[member.party] =1
    x_offset =0
    margin_fraction = 0.001
    for partij in voor:
        proportion = voor[partij]/total_votes
        if partij=='Partij voor de Dieren':
            partij = 'PvdD'
        if 'ouderen' in partij.lower():
            partij = 'OA'
        label_text =partij
        label = ctk.CTkLabel(
            vote_frame,
            text = label_text,
            fg_color="green")
        label.place(relx = x_offset+margin_fraction, relwidth=proportion-2*margin_fraction,relheight = 1.0)
        x_offset += proportion

    for partij in tegen:
        proportion = tegen[partij] / total_votes
        if partij=='Partij voor de Dieren':
            partij = 'PvdD'
        if 'ouderen' in partij.lower():
            partij = 'OA'
        label_text =partij
        label = ctk.CTkLabel(
            vote_frame,
            text=label_text,
            fg_color="red")
        label.place(relx=x_offset+margin_fraction, relwidth=proportion-2*margin_fraction, relheight=1.0)
        x_offset += proportion




def reset():
    global should_be_shown_based_on_keyword
    for item in all_items:
        tree.reattach(item, all_items_parents[item],'end')
        tree.item(item, tags=())
        should_be_shown_based_on_keyword[item] = True


def match(typed,item_text,description_text,pdf_text):
    global value_b
    if typed in item_text:
        return True
    if typed in description_text:
        return True
    if value_b.get():
        if pdf_text:
            if typed in pdf_text.lower():
                return True
    return False

def show(item):
    global types
    global value_m, value_a, value_r, value_i, value_o

    type = types[item]
    if 'motie' in type:
        return value_m.get()
    elif 'amendement' in type:
        return value_a.get()
    elif 'raadsvoorstel' in type:
        return value_r.get()
    elif 'initiatief' in type:
        return value_i.get()
    elif 'orde' in type:
        return value_o.get()
    #no match
    return True

def filterTypes(event):
    global should_be_shown_based_on_keyword
    global value_m, value_a, value_r, value_i, value_o
    return #function is not really working as it should. So it's disabled.
    for item in all_items:
        if should_be_shown_based_on_keyword[item]:
            if 'motie' in types[item]:
                if not value_m.get():
                    tree.detach(item)
            elif 'amendement' in types[item]:
                if not value_a.get():
                    tree.detach(item)
            elif 'raadsvoorstel' in types[item]:
                if not value_r.get():
                    tree.detach(item)
            elif 'initiatief' in types[item]:
                if not value_i.get():
                    tree.detach(item)
            elif 'orde' in types[item]:
                if not value_o.get():
                    tree.detach(item)




def search(event):
    global just_added_item_after_search, pdf_texts
    global should_be_shown_based_on_keyword
    typed = search_entry.get().lower()
    if len(typed)<3:
        reset()
        just_added_item_after_search = []
        return
    else:


        for item in all_items:
            item_text = tree.item(item,'text').lower()
            description_text = tree.item(item,'values')[2].lower()
            pdf = pdf_texts[item]
            if match(typed,item_text,description_text,pdf):
                parent = all_items_parents[item]
                tree.reattach(item, parent,'end')
                tree.item(item,tags=('highlight',))
                should_be_shown_based_on_keyword[item] = True
                if parent != '':
                    tree.reattach(parent, all_items_parents[parent], 'end')
                    tree.item(item, tags=('highlightchild',))
                    should_be_shown_based_on_keyword[parent] = True

                    siblings = tree.get_children(parent)
                    for sibling in siblings:
                        tree.reattach(sibling,parent,'end')
                        if 'highlightchild' not in tree.item(sibling)['tags']:
                            tree.item(sibling, tags=('child',))
                        just_added_item_after_search.append(sibling)
                        should_be_shown_based_on_keyword[sibling] = True

            elif item not in just_added_item_after_search:
                tree.detach(item)
                tree.item(item, tags=())
                should_be_shown_based_on_keyword[item] = False

        #filterTypes()
        print(typed)



# Define the GUI and layout for CustomTkinter
def create_gui():
    global tree
    global search_entry
    global icon_doc
    global icon_script
    global icon_none
    global icon_yes
    global icon_no
    global icon_toezegging
    global icon_gone
    global icon_agenda
    global icon_trash
    global icon_error
    global icon_notes
    global icon_modified
    global icon_orde

    global all_items
    global all_items_parents
    global pdf_texts
    global types
    global just_added_item_after_search
    global should_be_shown_based_on_keyword
    global modules
    global expanded
    global btn_pdf
    global btn_module
    global btn_meeting
    global vote_frame
    global value_b
    global value_m
    global value_a
    global value_r
    global value_i
    global value_o

    modules = {}
    all_items = []
    all_items_parents = {}
    pdf_texts = {}
    types = {}
    just_added_item_after_search = []
    should_be_shown_based_on_keyword = {}
    expanded = False




    # Initialize CustomTkinter window
    root = ctk.CTk()
    ctk.set_default_color_theme("dark-blue")
    ctk.set_appearance_mode("light")

    root.title("iRIS / powered by Partij voor de Dieren")
    root.geometry("1500x800")

    # make search box
    # Create two buttons: One for each type of action
    search_frame = ctk.CTkFrame(root)
    search_frame.pack(pady=0, padx=0, fill="y", side="left")

    titel = ctk.CTkLabel(master=search_frame,text='iRIS',font=(None,30))
    subtitel = ctk.CTkLabel(master=search_frame,text='Powered By PvdD - v24.10',font=(None,15))
    titel.pack(pady=(20,0))
    subtitel.pack()

    # Button to open the meeting link from the selected item
    search_entry= ctk.CTkEntry(master=search_frame, placeholder_text="Zoeken..",font = ("Roboto",20),justify="center",width=400)
    search_entry.pack(pady=20, padx=10)

    switch_frame = ctk.CTkFrame(search_frame)
    switch_frame.pack(pady=10, padx=30, fill="y")

    value_b = tk.BooleanVar(value=True)
    value_m = tk.BooleanVar(value=True)
    value_a = tk.BooleanVar(value=True)
    value_r = tk.BooleanVar(value=True)
    value_i = tk.BooleanVar(value=True)
    value_o = tk.BooleanVar(value=True)
    value_darkmode = tk.BooleanVar(value=True)

    switch_b = ctk.CTkSwitch(master=switch_frame,text="Doorzoek bijlage", command= lambda: search('bijlage'), variable=value_b)
    switch_b.grid(row=1, column = 1, sticky="w", pady=5,padx = 10)
    # switch_m = ctk.CTkSwitch(master=switch_frame,text="Toon moties", command= lambda: filterTypes('m'), variable=value_m)
    # switch_m.grid(row=2, column = 1, sticky="w", pady=5,padx = 10)
    # switch_a = ctk.CTkSwitch(master=switch_frame, text="Toon amendementen", command=lambda: filterTypes('a'), variable=value_a)
    # switch_a.grid(row=3, column = 1, sticky="w", pady=5,padx = 10)
    # switch_r = ctk.CTkSwitch(master=switch_frame, text="Toon raadsvoorstellen", command=lambda: filterTypes('r'), variable=value_r)
    # switch_r.grid(row=4, column = 1, sticky="w", pady=5,padx = 10)
    # switch_i = ctk.CTkSwitch(master=switch_frame, text="Toon initiatiefvoorstellen", command=lambda: filterTypes('i'), variable=value_i)
    # switch_i.grid(row=5, column = 1, sticky="w", pady=5,padx = 10)
    # switch_o = ctk.CTkSwitch(master=switch_frame, text="Toon ordevoorstellen", command=lambda: filterTypes('o'), variable=value_o)
    # switch_o.grid(row=6, column = 1, sticky="w", pady=5,padx = 10)

    # Create a frame to hold the Treeview
    frame = ctk.CTkFrame(root)
    frame.pack(pady=20, padx=20, fill="both", expand=True)



    # Define the Treeview widget

    tree = ttk.Treeview(frame, columns=('Dag','Label','Info'))
    # Set the heading and format the columns
    tree.heading('#0', text='Title')
    tree.column('#0', width=350)

    tree.heading('Dag', text="Dag")
    tree.column('Dag', width=5)

    tree.heading('Label', text="Label")
    tree.column('Label', width=5)

    tree.heading('Info', text="Info")
    tree.column('Info', width=400)


    # Scrollbar for the Treeview
    scrollbar = ctk.CTkScrollbar(frame, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    tree.pack(fill="both", expand=True)

    # Load images (small colored dots) beforehand
    # Load images
    icon_doc = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Text.png")))  # 16x16 image of green dot
    icon_script = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Script.png")))  # 16x16 image of green dot
    icon_none = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Question.png")))  # 16x16 image of green dot
    icon_yes = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Yes.png")))  # 16x16 image of green dot
    icon_no = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "No.png")))  # 16x16 image of green dot
    icon_toezegging = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Comment.png")))  # 16x16 image of green dot
    icon_agenda = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Calendar.png")))  # 16x16 image of green dot
    icon_gone = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Smile.png")))  # 16x16 image of green dot
    icon_trash = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Trash.png")))  # 16x16 image of green dot
    icon_error = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Warning.png")))  # 16x16 image of green dot
    icon_notes = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Notes.png")))  # 16x16 image of green dot
    icon_modified = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Modify.png")))  # 16x16 image of green dot
    icon_orde = tk.PhotoImage(
        file=cwdpath(os.path.join('Presentation', 'icon', '16x16', "Wrench.png")))  # 16x16 image of green dot



    # Load data into Treeview (hierarchical structure)
    module_manager = ModuleManager()
    module_manager.addall()
    module_manager.sort_chronological()

    for module in module_manager.modules:
        if module.parent is None:
            load_data_into_treeview(tree, '', module)  # use '' to insert into the root level

    # Apply statuses as row background colors
    style = ttk.Style()
    style.configure("Treeview", rowheight=60, font=(None,12))

    tree.tag_configure("green", background="#90ee90")
    tree.tag_configure("red", background="#ff7f7f")
    tree.tag_configure("yellow", background="#ffee90")
    tree.tag_configure("grey", background="#aaaaaa")
    tree.tag_configure("white", background='#ffffff')

    tree.tag_configure("parent", background='#ffffff')
    tree.tag_configure("child", background='#dddddd')
    tree.tag_configure("highlight", background='#a8c7aa')
    tree.tag_configure("highlightchild", background='#889e89')

    style.map('Treeview', background=[('selected', '#7f8cab')])

    vote_frame = ctk.CTkFrame(root, height = 30)
    vote_frame.pack(pady = 10, padx=10, fill='x')







    # Create two buttons: One for each type of action
    btn_frame = ctk.CTkFrame(search_frame)
    btn_frame.pack(pady=10, padx=20, fill="x", side='bottom')

    # Button to open the meeting link from the selected item
    btn_meeting = ctk.CTkButton(
        btn_frame, text="Ga naar de vergadering",
        command=lambda: open_meeting_link(None)
    )
    btn_meeting.pack(side="bottom", padx=10, pady= 10, fill='x')

    # Button to open the PDF link from the selected item
    btn_module = ctk.CTkButton(
        btn_frame, text="Ga naar de module",
        command=lambda: open_module_link(None)
    )
    btn_module.pack(side="bottom", padx=10,pady= 10, fill='x')

    btn_pdf = ctk.CTkButton(
        btn_frame, text="Open PDF",
        command=lambda: open_pdf_link(None)
    )
    btn_pdf.pack(side="bottom", padx=10, pady= 10, fill='x')

    #Binds
    root.bind('<F1>', handle_f1_event)
    search_entry.bind('<KeyRelease>',search)
    tree.bind('<<TreeviewSelect>>', on_item_selected)

    # Run the application loop
    root.mainloop()


if __name__ == "__main__":
    create_gui()