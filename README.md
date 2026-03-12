# 🗓️ STT — School Time Table

[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Release](https://img.shields.io/github/v/release/USERK8/stt)](https://github.com/USERK8/stt/releases)

An advanced **constraint-based timetable generator** built for schools following KVS timetable guidelines.

---

## 🚀 Purpose

STT intelligently generates school timetables while respecting:

- Teacher workload limitations
- Class availability constraints
- Lab period allocation for Classes 11 & 12
- Mathematics period distribution for:
  - Bio-Maths students  
  - Computer Science–Maths students  
  - Commerce with Maths students
- Fully structured, conflict-free scheduling  

Every timetable generated is **optimized, constraint-aware, and logically structured**.

> Built for Viksit Bharat and Digital India, STT modernizes school systems — moving from manual scheduling to **efficient, tech-driven planning**.  
> Goal: *“Make schools smarter, more organized, and future-ready.”*

---

## 🏫 Features

- Timetable generation for Classes 6–12  
- Three sections per class (adjustable in-app)  
- Teacher-wise timetable  
- Class-wise timetable  
- Day-wise timetable  
- Fully offline functionality (some updates may require internet)

---

## 📈 Latest Version Updates – STT

### 🟢 v1.0.0
- ⚡ Firmware development & basic app GUI

### 🟡 v2.3.6
- 🛠 Initial generation features added
- ✨ Minor GUI polish using GTK

### 🔵 v4.3.5
- 🧩 Advanced controller for full customization:
  - 👩‍🏫 Add teacher names & classes
  - 📅 Manage schedules
  - 📄 Generate PDFs, including class-wise timetables

### 🟣 v5.6.0 – Major Update!
- 🔄 Full switch to **PyQt6** for wide accessibility
- 🧠 Smarter, conflict-free timetable allotments
- 🛠 Practical session management & enhanced GUI

### 🔶 v6.0.3
- 🐧 Linux downloadable distro
- 📊 Expanded PDF options: class-wise, teacher-wise, day-wise (in development)
- 🎨 Smoother & more responsive GUI

### 🔥 v7.3.1 – Ultra-Fast STT Generator
- ⚡ Lightning-fast & reliable timetable creation
- ⏱ Live progress tracking
- 🏆 Best allotment model yet, with extended GUI features & complete teacher/class management

---

## 🔐 Privacy & Security

- No client-side data collection  
- Completely self-contained  
- No background tracking

---

## 💻 Platform Support

- **Linux (64-bit)** — fully supported  
- **Windows** — run source code via Python, or wait for upcoming executable release

---

## 🛠 Built With

- **Python**  
- **PyQt6** for UI management  
- Continuous logic improvements, UI updates, and bug fixes

---

## 🐧 Linux Installation Manual

### 1️⃣ System Requirements

- 64-bit Linux OS (Ubuntu, Kali, Debian, Fedora, Arch, Pop!\_OS recommended)  
- Latest Python version

### 2️⃣ Install Dependencies

**Ubuntu / Kali / Debian**:
```bash
sudo apt update
sudo apt install -y build-essential libssl-dev zlib1g-dev \
libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev \
tk-dev libffi-dev wget
```
### 3️⃣ Download the App

Go to the Releases section, download the file named `main`, and place it in a separate folder to avoid clutter during updates.

### 4️⃣ Make Executable

Open the folder → Right-click the file → Properties → Enable Executable → Double-click to run.  
On first launch: click Yes when prompted for updates.

### 5️⃣ Using the App

* Modify teacher names
* Adjust class availability
* Assign subjects
* Generate timetables: class-wise, teacher-wise, day-wise
* Makes timetable management fast, structured, and efficient

### 🪟 Windows Users

Official executable under development.  
Source code runnable with any Python compiler.

### ⚠️ Trial Version Notice

This is a trial version.  
Active development continues.  
Built by USERK8.  
No user data is collected.

### 📩 Support

Email: userk8.dev@gmail.com  
Thanks for trying STT! Your feedback helps shape smarter, future-ready schools.
