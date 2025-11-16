Clinical Anonymizer

Clinical Anonymizer is a free, open-source desktop tool designed to help clinicians, researchers, and students safely share clinical or research PDF documents with large language models (LLMs) and other AI tools.

It works by redacting (blacking out) a list of sensitive, identifying terms (like "Name", "Date of Birth", "Patient ID", etc.) to protect patient privacy and help comply with data-protection regulations (e.g., GDPR, HIPAA).

1) Overview

This tool provides an intuitive interface to:

Load any PDF document.

Manage a list of sensitive terms (labels) to find.

Anonymize the document by blacking out the found terms.

Save a new, anonymized PDF, ready to be shared.

All processing is done 100% locally on your machine. Your documents are never uploaded or sent anywhere.

2) Download & Usage (Portable App)

This application is provided as a portable .zip file. No installation is required.

Download the .zip file:

Link: https://heibox.uni-heidelberg.de/f/194430ba907f4eea89f6/

Extract the .zip file:

Right-click the downloaded .zip file and select "Extract All...".

Choose a folder to extract the application. It is recommended to use a simple path on a main drive (e.g., C:\ClinicalAnonymizer\) rather than your "Downloads" folder.

Run the application:

Open the folder you just extracted.

Double-click the Clinical_Anonymizer.exe file to run the application.

3) Key Features

Load Any PDF: Anonymize any PDF document.

Two Redaction Modes:

Standard Protection: Redacts only the identified sensitive words.

Enhanced Protection: Redacts the words and a contextual area to the right and below, to hide the corresponding values.

Customizable Term List: Open the "Manage Redaction Terms" window to add, edit, or delete sensitive terms. This allows you to add project-specific identifiers or institution names.

Built-in Terms: Includes a default, multi-language list of common sensitive terms in English, German, and French.


4) System Requirements

Windows 10 or later.


5) Quick Start

Launch the application by double-clicking the Clinical_Anonymizer.exe file.

Click "Browse" next to "Source PDF Document" to select your file.

The "Destination Folder" and "Output Filename" will be set automatically. You can change them if needed.

Select "Standard Protection" or "Enhanced Protection".

(Optional) Click "Manage Redaction Terms" to review or add to the list of terms that will be redacted.

Click the "Execute Anonymization" button.

A progress bar will show the status. When finished, you will be asked if you want to open the output folder.

6) Help Guide

A detailed user guide is built into the application.
Please launch the app and click "Help" > "Usage Help" in the menu bar.

7) Data Storage

The application saves your custom-defined redaction terms in a JSON file named redaction_terms.json. This file is created in the same directory as the .exe file.

8) Privacy and Responsibility

This tool is provided to support your anonymization workflow. All file processing happens locally on your computer. No documents or data are ever transmitted to any external server.

You remain solely responsible for verifying the final anonymized document to ensure all sensitive information has been removed before sharing it. This tool cannot guarantee 100% redaction. Always manually inspect the output.

9) License

This software is released under the GNU General Public License v3.0 (GPLv3).

You are free to use, modify, and redistribute the software under the GPLv3.

This program is provided “AS IS,” without warranty of any kind.

10) Acknowledgments and Donations

This application was developed by Mehrdad Davoudi, PhD student, Clinic for Orthopaedics, Heidelberg University Hospital, Heidelberg, Germany.

We gratefully acknowledge the support of the Gesellschaft der Freunde der Universität Heidelberg e.V. (Society of Friends of Heidelberg University).

This app is free to use. If it helps your work, please consider a donation to support students and early-career researchers:

Recipient: Gesellschaft der Freunde der Universität Heidelberg e.V.

Bank: Deutsche Bank Heidelberg

IBAN: DE22 6727 0003 0049 4005 00

BIC (SWIFT): DEUTDESM672

Reference (optional): Spende – Förderung Studierende/Promotion