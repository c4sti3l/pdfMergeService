import os
import time
import shutil
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

class PDFMergerHandler(FileSystemEventHandler):
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
    
    def on_any_event(self, event):
        if event.is_directory:
            return
        if len(os.listdir(self.input_directory)) >= 2:  # at least 2 files in directory
            print("New pdf-files found. Begin merge...") 
            self.merge_pdfs()

    def merge_pdfs(self):
        input_files = sorted(os.listdir(self.input_directory), key=lambda x: os.path.getmtime(os.path.join(self.input_directory, x)))
        first_file_name = input_files[0]  # Get name of first file
        odd_pdf = PdfReader(os.path.join(self.input_directory, input_files[0]))
        even_pdf = PdfReader(os.path.join(self.input_directory, input_files[1]))

        total_pages = max(len(odd_pdf.pages), len(even_pdf.pages))
        
        merged_pdf = PdfWriter()
        for page_num in range(total_pages):
            if page_num < len(odd_pdf.pages):
                merged_pdf.add_page(odd_pdf.pages[page_num])
            if page_num < len(even_pdf.pages):
                merged_pdf.add_page(even_pdf.pages[page_num])

        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d")
        output_file = os.path.join(self.output_directory, f"{timestamp}_{os.path.splitext(first_file_name)[0]}_merged.pdf")

        
         # check, if output file already exists to create identical suffix
        counter = 1
        while os.path.exists(output_file):
            output_file = os.path.join(self.output_directory, f"{timestamp}_{os.path.splitext(first_file_name)[0]}_merged({counter}).pdf")
            counter += 1
        
        with open(output_file, 'wb') as output_pdf:
            merged_pdf.write(output_pdf)
        print(f"Merging complete. Created file: {output_file}") 
        
        # Remove Source files
        for filename in input_files:
            file_path = os.path.join(self.input_directory, filename)
            os.remove(file_path)
            print(f"Source file deleted: {file_path}") 


if __name__ == "__main__":
    input_directory = '/app/input'
    output_directory = '/app/output'
    observer = PollingObserver()
    
    event_handler = PDFMergerHandler(input_directory, output_directory)
    observer.schedule(event_handler, path=input_directory, recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
