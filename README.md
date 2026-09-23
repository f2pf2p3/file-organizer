# File Organizer

A simple Python file organizer that automatically moves files into categorized folders based on their file extensions.

The program provides two organization modes and a Revert feature:

* Config Mode — organizes the current user's Downloads folder using `config.txt`
* Auto Mode — lets the user select a directory and uses built-in categories
* Revert Last Action — restores files moved by the most recent organization operation

---

## Features

* Organize files by file extension
* Configurable categories using `config.txt`
* Built-in categories for Auto Mode
* Automatically detects the current Windows user
* Automatically uses the current user's Downloads folder in Config Mode
* Select a directory manually in Auto Mode
* Confirm the selected directory before organizing
* Does not overwrite existing files
* Skips files without extensions
* Skips unknown file extensions
* Only processes files directly inside the selected directory
* Revert the most recent organization operation
* Revert history is saved to `history.json`
* Revert still works after closing and reopening the program
* Uses only Python standard libraries

---

## Project Structure

```text
file-organizer/
├── file_organizer.py
├── config.txt
├── history.json
├── run.bat
└── README.md
```

### File Description

| File                | Description                                   |
| ------------------- | --------------------------------------------- |
| `file_organizer.py` | Main Python program                           |
| `config.txt`        | User-defined file organization rules          |
| `history.json`      | Automatically generated file movement history |
| `run.bat`           | Windows script for starting the program       |
| `README.md`         | Project documentation                         |

> `history.json` does not need to be created manually. The program creates it automatically after files are successfully moved.

---

## Requirements

* Python 3.10 or newer
* Windows recommended

The program uses only Python standard libraries:

```text
pathlib
shutil
os
json
```

No external packages are required.

---

## How to Run

### Option 1: Python

Open a terminal inside the project folder:

```bash
python file_organizer.py
```

### Option 2: run.bat

Double-click:

```text
run.bat
```

---

## Main Menu

When the program starts, it displays:

```text
=======================================================
                 FILE ORGANIZER
=======================================================

  1. Config Mode
  2. Auto Mode
  3. Revert Last Action
  4. Exit

-------------------------------------------------------
  Select option [1-4]:
```

---

# 1. Config Mode

Config Mode uses the rules defined in `config.txt`.

It automatically detects the current Windows user's home directory and uses:

```text
C:\Users\<Username>\Downloads
```

For example:

```text
Username: catme
Target directory: C:\Users\catme\Downloads
```

No username needs to be stored inside `config.txt`.

---

## config.txt

Example:

```text
# Folder name = file extensions
# Separate multiple extensions with commas

img=jpg,jpeg,png,gif,webp,bmp
pdf=pdf
python=py
video=mp4,mkv,avi,mov
document=doc,docx,txt
archive=zip,rar,7z
exe=exe
```

The format is:

```text
folder_name=extension1,extension2,extension3
```

For example:

```text
img=jpg,png,gif
```

means:

```text
.jpg → img/
.png → img/
.gif → img/
```

---

## Config Mode Example

Before:

```text
Downloads/
├── image.jpg
├── report.pdf
├── program.py
└── movie.mp4
```

After:

```text
Downloads/
├── img/
│   └── image.jpg
├── pdf/
│   └── report.pdf
├── python/
│   └── program.py
└── video/
    └── movie.mp4
```

---

# 2. Auto Mode

Auto Mode uses built-in categories defined in `AUTO_CATEGORIES` inside `file_organizer.py`.

The user first selects a directory.

Example:

```text
Available directories:

  1. Desktop
     C:\Users\Username\Desktop

  2. Documents
     C:\Users\Username\Documents

  3. Downloads
     C:\Users\Username\Downloads

  4. Pictures
     C:\Users\Username\Pictures

  5. Custom Path
```

The program then asks:

```text
Confirm this directory? [Y/N]:
```

The organization starts only after confirming with `Y`.

---

## Built-in Auto Categories

| Folder         | Extensions                                          |
| -------------- | --------------------------------------------------- |
| `img`          | jpg, jpeg, png, gif, webp, bmp, svg, ico, tiff, tif |
| `video`        | mp4, mkv, avi, mov, wmv, flv, webm, m4v             |
| `audio`        | mp3, wav, flac, aac, ogg, m4a                       |
| `document`     | txt, doc, docx, odt, rtf                            |
| `pdf`          | pdf                                                 |
| `spreadsheet`  | xls, xlsx, csv, ods                                 |
| `presentation` | ppt, pptx, odp                                      |
| `archive`      | zip, rar, 7z, tar, gz                               |
| `code`         | py, js, ts, java, cpp, c, h, hpp, cs, go, rs, php   |
| `font`         | ttf, otf, woff, woff2                               |
| `exe`          | exe                                                 |

Only categories containing recognized files are created.

For example, if the directory only contains:

```text
photo.jpg
movie.mp4
```

the program creates:

```text
img/
video/
```

It does not create empty folders such as:

```text
audio/
pdf/
code/
archive/
```

---

# 3. Revert Last Action

Revert Last Action restores files moved by the most recent organization operation.

Example:

```text
Before:

Downloads/
├── image.jpg
└── movie.mp4
```

After Auto Mode:

```text
Downloads/
├── img/
│   └── image.jpg
└── video/
    └── movie.mp4
```

Selecting:

```text
3. Revert Last Action
```

restores:

```text
Downloads/
├── image.jpg
└── movie.mp4
```

---

## History File

The program automatically creates:

```text
history.json
```

after files are successfully moved.

You do not need to create this file manually.

Example:

```json
[
    {
        "original": "C:\\Users\\Username\\Downloads\\image.jpg",
        "current": "C:\\Users\\Username\\Downloads\\img\\image.jpg"
    },
    {
        "original": "C:\\Users\\Username\\Downloads\\movie.mp4",
        "current": "C:\\Users\\Username\\Downloads\\video\\movie.mp4"
    }
]
```

The history stores:

* Original file location
* Current file location

This allows the program to restore files even after the program has been closed and opened again.

---

## Revert Behavior

Only the most recent organization operation is stored.

For example:

```text
Organize #1
    ↓
history.json

Organize #2
    ↓
history.json is replaced with Organize #2
```

The program does not keep unlimited undo history.

If a file cannot be reverted, the failed operation remains in `history.json` so it can be retried later.

When all files are successfully reverted:

```text
history.json
```

is automatically deleted.

---

# File Handling Rules

The program follows these rules when organizing files.

### Files without extensions

Files without extensions are skipped:

```text
README
LICENSE
filename
```

Example output:

```text
[SKIP] README - no extension
```

### Unknown extensions

Extensions that are not included in the configuration are skipped:

```text
.xyz
.abc
```

Example:

```text
[SKIP] file.xyz - unknown extension
```

### Existing files

The program never overwrites an existing destination file.

Example:

```text
img/photo.jpg
```

already exists.

The new `photo.jpg` will be skipped:

```text
[SKIP] photo.jpg - destination already exists
```

### Direct files only

The program only processes files directly inside the selected directory.

It does not recursively scan subdirectories.

For example:

```text
Downloads/
├── image.jpg        ← processed
├── movie.mp4        ← processed
└── old/
    └── document.pdf ← not processed
```

---

# Output Example

During organization:

```text
[MOVE] image.jpg -> img/
[MOVE] movie.mp4 -> video/
[SKIP] README - no extension
[SKIP] file.xyz - unknown extension
[SKIP] existing.pdf - destination already exists

Moved: 2
Skipped: 3
```

During revert:

```text
Reverting last action...

[REVERT] movie.mp4 <- C:\Users\Username\Downloads
[REVERT] image.jpg <- C:\Users\Username\Downloads

Reverted: 2
Failed: 0
```

---

# Configuration Mode vs Auto Mode

| Feature          | Config Mode      | Auto Mode           |
| ---------------- | ---------------- | ------------------- |
| Configuration    | `config.txt`     | Built-in categories |
| Directory        | User's Downloads | User selects        |
| Custom directory | No               | Yes                 |
| Confirmation     | No               | Yes                 |
| Revert           | Yes              | Yes                 |
| `history.json`   | Yes              | Yes                 |

---

# Important Notes

### `history.json`

Do not edit `history.json` manually unless you understand the stored paths.

The program manages this file automatically.

### `config.txt`

`config.txt` is editable and can be changed to add or remove file categories.

Example:

```text
python=py
javascript=js,jsx
web=html,css
```

### Existing folders

The program does not delete category folders during Revert.

For example:

```text
Downloads/
└── img/
```

may remain after all files are reverted.

This prevents the program from accidentally deleting folders that may contain other user files.

---

# Limitations

* Only the most recent organization operation can be reverted.
* Revert history is stored locally in `history.json`.
* If `history.json` is deleted, the previous operation cannot be automatically reverted.
* The program does not recursively organize subdirectories.
* Existing destination files are not overwritten.
* Unknown file extensions are skipped.
* Files without extensions are skipped.
* Empty category folders are not automatically removed.

---

# License

This project is for educational and personal use.


## Credits

Application icon:
[Automatic icon](https://www.flaticon.com/free-icon/automatic_8101857)
designed by [Shahid-Mehmood](https://www.flaticon.com/authors/shahid-mehmood)
from [Flaticon](https://www.flaticon.com/)