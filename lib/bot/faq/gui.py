# bot modules
from bot.database.sqlite import Database
from bot.faq.base import FAQ
from bot.searcher.faq import FAQSearchEngine

# general python
import tkinter
from tkinter import ttk, messagebox
import abc
import webbrowser


class Menubar(ttk.Frame):
    """Builds a menu bar for the top of the main window"""

    def __init__(self, parent, *args, **kwargs):
        """ Constructor"""
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_menubar()

    def on_exit(self):
        """Exits program"""
        quit()

    # TODO add FAQ documentation link when available
    def display_help(self):
        """Displays help document"""
        webbrowser.open("https://github.com/rucio/donkeybot")
        return

    def init_menubar(self):
        self.menubar = tkinter.Menu(self.root)
        self.menu_file = tkinter.Menu(self.menubar)  # Creates a "File" menu
        self.menu_file.add_command(
            label="Exit", command=self.on_exit
        )  # Adds an option to the menu
        self.menubar.add_cascade(
            menu=self.menu_file, label="File"
        )  # Adds File menu to the bar. Can also be used to create submenus.

        self.menu_help = tkinter.Menu(self.menubar)  # Creates a "Help" menu
        self.menu_help.add_command(label="Help", command=self.display_help)
        self.menubar.add_cascade(menu=self.menu_help, label="Help")

        self.root.config(menu=self.menubar)


class Window(ttk.Frame):
    """Abstract base class for a popup window"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, parent):
        """ Constructor """
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.resizable(width=False, height=False)  # Disallows window resizing
        self.validate_notempty = (self.register(self.notEmpty), "%P")
        self.init_gui()

    @abc.abstractmethod  # Must be overwriten by subclasses
    def init_gui(self):
        """Initiates GUI of any popup window"""
        pass

    @abc.abstractmethod
    def on_click(self):
        """Does something that all popup windows need to do"""
        pass

    def notEmpty(self, P):
        """Validates Entry fields to ensure they aren't empty"""
        if P.strip():
            valid = True
        else:
            print("Error: Field must not be empty.")  # Prints to console
            valid = False
        return valid

    def close_win(self):
        """Closes window"""
        self.parent.destroy()


class IndexWindow(Window):
    """ Index FAQ window """

    def init_gui(self):
        self.large_font = ("Verdana", 30)
        self.small_font = ("Verdana", 10)

        self.parent.title("FAQ Indexing")
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(3, weight=1)

        # Create Widgets
        self.label_title = ttk.Label(
            self.parent, text="Use this to index FAQs for the Search Engine!"
        )
        self.contentframe = ttk.Frame(self.parent, relief="sunken")

        self.db_label = ttk.Label(self.contentframe, text="Database:")
        self.db_input = ttk.Entry(
            self.contentframe,
            width=50,
            font=self.small_font,
            validate="focusout",
            validatecommand=(self.validate_notempty),
        )
        self.db_input.insert(0, "data_storage")

        self.table_label = ttk.Label(self.contentframe, text="FAQ table:")
        self.table_input = ttk.Entry(
            self.contentframe,
            width=50,
            font=self.small_font,
            validate="focusout",
            validatecommand=(self.validate_notempty),
        )
        self.table_input.insert(0, "faq")

        self.btn_do = ttk.Button(
            self.parent, text="Create index", command=self.on_click
        )
        self.btn_cancel = ttk.Button(self.parent, text="Cancel", command=self.close_win)

        # Layout
        self.label_title.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.contentframe.grid(row=1, column=0, columnspan=4, sticky="nsew")

        self.db_label.grid(row=0, column=0)
        self.db_input.grid(row=0, column=1, sticky="w")

        self.table_label.grid(row=1, column=0)
        self.table_input.grid(row=1, column=1, sticky="w")

        self.btn_do.grid(row=2, column=0, sticky="e")
        self.btn_cancel.grid(row=2, column=1, sticky="e")

        # Padding
        for child in self.parent.winfo_children():
            child.grid_configure(padx=5, pady=5)
        for child in self.contentframe.winfo_children():
            child.grid_configure(padx=5, pady=2)

    def on_click(self):
        """Indexes FAQ values for the Search Engine"""
        db_name = self.db_input.get().strip()
        faq_table_name = self.table_input.get().strip()
        if db_name and faq_table_name:
            data_storage = Database(f"{db_name}.db")
            faq_df = data_storage.get_dataframe(table=f"{faq_table_name}")
            faq_se = FAQSearchEngine()
            faq_se.create_index(
                corpus=faq_df,
                db=data_storage,
                table_name=f"{faq_table_name}_doc_term_matrix",
            )
            data_storage.close_connection()
            self.close_win()
        else:
            print("Error: But for real though, fields must not be empty.")


class QAPairWindow(Window):
    """ QA Pair window """

    def init_gui(self):

        self.large_font = ("Verdana", 30)
        self.small_font = ("Verdana", 10)

        self.parent.title("Question-Answer Pair")
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(3, weight=1)

        # Create Widgets
        self.label_title = ttk.Label(
            self.parent, text="Use this to insert QA pairs to FAQ!"
        )
        self.contentframe = ttk.Frame(self.parent, relief="sunken")

        self.db_label = ttk.Label(self.contentframe, text="Database:")
        self.db_input = ttk.Entry(
            self.contentframe,
            width=50,
            font=self.small_font,
            validate="focusout",
            validatecommand=(self.validate_notempty),
        )
        self.db_input.insert(0, "data_storage")

        self.table_label = ttk.Label(self.contentframe, text="FAQ table:")
        self.table_input = ttk.Entry(
            self.contentframe,
            width=50,
            font=self.small_font,
            validate="focusout",
            validatecommand=(self.validate_notempty),
        )
        self.table_input.insert(0, "faq")

        self.que_label = ttk.Label(self.contentframe, text="Question:")
        self.que_input = ttk.Entry(
            self.contentframe,
            width=50,
            font=self.small_font,
            validate="focusout",
            validatecommand=(self.validate_notempty),
        )

        self.ans_label = ttk.Label(self.contentframe, text="Answer:")
        self.ans_input = tkinter.Text(
            self.contentframe, width=50, height=5
        )  # Text so that I have height (I loose validate but its ok)

        self.auth_label = ttk.Label(self.contentframe, text="Author:")
        self.auth_input = ttk.Entry(
            self.contentframe,
            width=50,
            font=self.small_font,
            validate="focusout",
            validatecommand=(self.validate_notempty),
        )

        self.kw_label = ttk.Label(
            self.contentframe, text='Keywords (format: "kw1,kw2,kw3"):'
        )
        self.kw_input = ttk.Entry(
            self.contentframe,
            width=50,
            font=self.small_font,
            validate="focusout",
            validatecommand=(self.validate_notempty),
        )

        self.btn_do = ttk.Button(self.parent, text="Insert FAQ", command=self.on_click)
        self.btn_cancel = ttk.Button(self.parent, text="Cancel", command=self.close_win)

        # Layout
        self.label_title.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.contentframe.grid(row=2, column=0, columnspan=4, sticky="nsew")

        self.db_label.grid(row=0, column=0)
        self.db_input.grid(row=0, column=1, sticky="w")

        self.table_label.grid(row=1, column=0)
        self.table_input.grid(row=1, column=1, sticky="w")

        self.que_label.grid(row=2, column=0)
        self.que_input.grid(row=2, column=1, sticky="w")

        self.ans_label.grid(row=3, column=0)
        self.ans_input.grid(row=3, column=1, sticky="w")

        self.auth_label.grid(row=4, column=0)
        self.auth_input.grid(row=4, column=1, sticky="w")

        self.kw_label.grid(row=5, column=0)
        self.kw_input.grid(row=5, column=1, sticky="w")

        self.btn_do.grid(row=6, column=0, sticky="e")
        self.btn_cancel.grid(row=6, column=1, sticky="e")

        # Padding
        for child in self.parent.winfo_children():
            child.grid_configure(padx=5, pady=5)
        for child in self.contentframe.winfo_children():
            child.grid_configure(padx=5, pady=2)

    def on_click(self):
        """Inserts FAQ values to db"""
        db_name = self.db_input.get().strip()
        faq_table_name = self.table_input.get().strip()
        question = self.que_input.get().strip()
        answer = self.ans_input.get("1.0", tkinter.END).strip()
        print(answer)
        author = self.auth_input.get().strip()
        keywords = self.kw_input.get().strip()
        if db_name and faq_table_name and question and answer and author and keywords:
            self.insert_faq_to_db(
                db_name, faq_table_name, question, answer, author, keywords
            )
            self.close_win()
        else:
            print("Error: But for real though, field must not be empty.")

    def insert_faq_to_db(
        self, db_name, faq_table_name, question, answer, author, keywords
    ):
        """Inserts FAQ values to db"""
        # prepare data_storage
        data_storage = Database(f"{db_name}.db")
        # create table if not exists
        tables_in_db = list([table[0] for table in data_storage.get_tables()])
        if faq_table_name not in tables_in_db:
            print(f"Creating '{faq_table_name}' table in {db_name}.db")
            data_storage.create_faq_table(table_name=f"{faq_table_name}")
        # insert row
        faq_obj = FAQ(
            question=question, answer=answer, author=author, keywords=keywords
        )
        data_storage.insert_faq(faq_obj, table_name=faq_table_name)
        print(f"FAQ object inserted in '{faq_table_name}' table on {db_name}.db!")
        data_storage.close_connection()


class GUI(ttk.Frame):
    """Main GUI class"""

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()
        self.large_font = ("Verdana", 30)

    def openwindow(self):
        self.new_win = tkinter.Toplevel(self.root)  # Set parent
        QAPairWindow(self.new_win)

    def open_index_window(self):
        self.new_win = tkinter.Toplevel(self.root)  # Set parent
        IndexWindow(self.new_win)

    def init_gui(self):
        self.root.title("FAQ GUI")
        self.root.geometry("600x200")
        self.grid(column=0, row=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)  # Allows column to stretch upon resizing
        self.grid_rowconfigure(0, weight=1)  # Same with row
        self.grid_rowconfigure(1, weight=1)  # Same with second row
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.option_add(
            "*tearOff", "FALSE"
        )  # Disables ability to tear menu bar into own window

        # Menu Bar
        self.menubar = Menubar(self.root)

        # Insert new FAQ Widget
        self.faq_btn = ttk.Button(self, text="Insert new FAQ", command=self.openwindow)
        # Index FAQs Widget
        self.idx_btn = ttk.Button(
            self,
            text="Index FAQ table for the Search Engine",
            command=self.open_index_window,
        )

        # Layout using grid
        self.faq_btn.grid(row=0, column=0, sticky="ew")
        self.idx_btn.grid(row=1, column=0, sticky="ew")

        # Padding
        for child in self.winfo_children():
            child.grid_configure(padx=1, pady=1)


def on_closing():
    if messagebox.askokcancel(
        "Quit", "Did you remember to index the new FAQs for the Search Engine?"
    ):
        root.destroy()


if __name__ == "__main__":
    root = tkinter.Tk()
    GUI(root)
    # make sure to re-index FAQs for the Search Engine before closing the window
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
