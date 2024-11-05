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
        print(f"PDFMergerHandler initialized with input: {self.input_directory}, output: {self.output_directory}")
        self.check_existing_files()  # Prüft vorhandene Dateien beim Start

    def check_existing_files(self):
        print("Checking for existing files in input directory for merging...")
        if len(os.listdir(self.input_directory)) >= 2:  # Falls mindestens 2 Dateien vorhanden sind
            print("Existing pdf-files found. Begin merge...")
            self.merge_pdfs()

    def on_any_event(self, event):
        if event.is_directory:
            return
        print("Event detected in input directory for merging.")
        if len(os.listdir(self.input_directory)) >= 2:  # Falls mindestens 2 neue Dateien vorhanden sind
            print("New pdf-files found. Begin merge...")
            self.merge_pdfs()

    def merge_pdfs(self):
        print("Starting PDF merge process...")
        input_files = sorted(os.listdir(self.input_directory), key=lambda x: os.path.getmtime(os.path.join(self.input_directory, x)))
        first_file_name = input_files[0]  # Name der ersten Datei
        print(f"Files to merge: {input_files}")

        # Verwende das Erstelldatum der jüngeren Datei
        latest_file = input_files[-1]  # Die jüngste Datei ist die letzte in der sortierten Liste
        creation_time = os.path.getmtime(os.path.join(self.input_directory, latest_file))
        timestamp = datetime.fromtimestamp(creation_time).strftime("%Y_%m_%d")

        odd_pdf = PdfReader(os.path.join(self.input_directory, input_files[0]))
        even_pdf = PdfReader(os.path.join(self.input_directory, input_files[1]))
        total_pages = max(len(odd_pdf.pages), len(even_pdf.pages))
        
        merged_pdf = PdfWriter()
        for page_num in range(total_pages):
            if page_num < len(odd_pdf.pages):
                merged_pdf.add_page(odd_pdf.pages[page_num])
            if page_num < len(even_pdf.pages):
                merged_pdf.add_page(even_pdf.pages[page_num])

        output_file = os.path.join(self.output_directory, f"{timestamp}_{os.path.splitext(first_file_name)[0]}_merged.pdf")

        # Überprüfen, ob Ausgabedatei bereits existiert, und ggf. Suffix hinzufügen
        counter = 1
        while os.path.exists(output_file):
            output_file = os.path.join(self.output_directory, f"{timestamp}_{os.path.splitext(first_file_name)[0]}_merged({counter}).pdf")
            counter += 1

        print(f"Saving merged PDF as: {output_file}")
        with open(output_file, 'wb') as output_pdf:
            merged_pdf.write(output_pdf)
        print(f"Merging complete. Created file: {output_file}")
        
        # Quell-Dateien entfernen
        for filename in input_files:
            file_path = os.path.join(self.input_directory, filename)
            os.remove(file_path)
            print(f"Source file deleted: {file_path}")


class SingleFileHandler(FileSystemEventHandler):
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        print(f"SingleFileHandler initialized with input: {self.input_directory}, output: {self.output_directory}")
        self.check_existing_files()  # Prüft vorhandene Dateien beim Start

    def check_existing_files(self):
        print("Checking for existing files in input_single directory...")
        for filename in os.listdir(self.input_directory):
            file_path = os.path.join(self.input_directory, filename)
            if os.path.isfile(file_path):
                print(f"Found existing file for processing: {filename}")
                self.process_single_file(file_path)

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected in input_single: {event.src_path}")
            self.process_single_file(event.src_path)

    def process_single_file(self, file_path):
        filename = os.path.basename(file_path)
        print(f"Processing single file: {filename}")

        # Verwende das Erstelldatum der Datei
        creation_time = os.path.getmtime(file_path)
        timestamp = datetime.fromtimestamp(creation_time).strftime("%Y_%m_%d")

        output_file = os.path.join(self.output_directory, f"{timestamp}_{filename}")

        # Überprüfen, ob Ausgabedatei bereits existiert, und ggf. Suffix hinzufügen
        counter = 1
        while os.path.exists(output_file):
            output_file = os.path.join(self.output_directory, f"{timestamp}_{os.path.splitext(filename)[0]}({counter}){os.path.splitext(filename)[1]}")
            counter += 1

        print(f"Moving file to output directory as: {output_file}")
        shutil.move(file_path, output_file)
        print(f"Single file processed and moved: {output_file}")


if __name__ == "__main__":
    input_directory = '/app/input'
    output_directory = '/app/output'
    input_single_directory = '/app/input_single'

    observer = PollingObserver()
    
    # Beobachter für den PDF-Merge-Handler
    pdf_merge_handler = PDFMergerHandler(input_directory, output_directory)
    observer.schedule(pdf_merge_handler, path=input_directory, recursive=True)

    # Beobachter für den Single-File-Handler
    single_file_handler = SingleFileHandler(input_single_directory, output_directory)
    observer.schedule(single_file_handler, path=input_single_directory, recursive=True)

    print("Starting observers...")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping observers...")
        observer.stop()
    observer.join()
    print("Observers stopped.")
