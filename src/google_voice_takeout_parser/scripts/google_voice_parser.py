import argparse
import sys

import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.font
import tkinter.messagebox

import google_voice_takeout_parser


def cli_main():
    parser = argparse.ArgumentParser(description='Parses a Google Voice Takeout folder and turns it into a CSV')
    parser.add_argument('indir', help="The directory containing the HTML files")
    parser.add_argument('outfile', help="The CSV file that should be written")
    parsed_args = parser.parse_args()
    indir = parsed_args.indir
    outfile = parsed_args.outfile
    file_count, csv_entries = google_voice_takeout_parser.process_directory(indir)
    google_voice_takeout_parser.write_to_csv(outfile, csv_entries)
    print(f"Completed parsing {file_count} files")


def gui_main():
    root = tkinter.Tk()
    ProcessHTML(root)
    root.mainloop()


class ProcessHTML:

    def get_input_directory(self):
        directory = tkinter.filedialog.askdirectory(mustexist=True)
        self.srcpath.set(directory)

    def get_output_file(self):
        output_fpath = tkinter.filedialog.asksaveasfilename()
        if not output_fpath.lower().endswith('.csv'):
            output_fpath += '.csv'
        self.destpath.set(output_fpath)

    def __init__(self, master):
        # First the entry for the input folder
        srcGroup = tkinter.LabelFrame(master, text="Google Voice Takeout HTML folder", padx=5, pady=5)
        srcGroup.grid(row=0, column=0, sticky='WE')
        self.srcpath = tkinter.StringVar()
        # Browse button
        tkinter.ttk.Button(srcGroup, text="Browse", command=self.get_input_directory).grid(row=0, column=1)
        # And the text entry
        tkinter.Entry(srcGroup, textvariable=self.srcpath, width=150).grid(row=0, column=2)

        # Next the entry for where to save the file
        destGroup = tkinter.LabelFrame(master, text="Destination", padx=5, pady=5)
        destGroup.grid(row=1, column=0, sticky='WE')
        self.destpath = tkinter.StringVar()
        # Browse button
        tkinter.ttk.Button(destGroup, text="Browse", command=self.get_output_file).grid(row=0, column=1)
        # And the text entry
        tkinter.Entry(destGroup, textvariable=self.destpath, width=150).grid(row=0, column=2)

        # Then a button to run:
        chooseSave = tkinter.Button(master, text="Run", command=self.process_google_voice_directory)
        chooseSave.grid(row=2, column=0)

    def process_google_voice_directory(self):
        """This function will write the output to a file
        """
        srcpath = self.srcpath.get()
        destpath = self.destpath.get()

        file_count, csv_entries = google_voice_takeout_parser.process_directory(srcpath)
        google_voice_takeout_parser.write_to_csv(destpath, csv_entries)
        tkinter.messagebox.showinfo(title='Complete!', message="Your Google Voice HTML parsing is complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_main()
    else:
        gui_main()
