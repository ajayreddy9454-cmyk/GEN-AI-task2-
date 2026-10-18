# Student LLM — Enterprise Academic Learning Management System (LMS)

A modern, attractive, and responsive **Student Learning Management System (LMS)** built with **Python Flask**, **SQLite**, **HTML5**, **CSS3**, and **JavaScript**. Engineered to meet enterprise academic SaaS standards with deep navy typography, indigo/violet primary accents, rounded cards, micro-animations, Lucide SVG icons, Chart.js visualizations, and an embedded **Student LLM AI Study Copilot**.

---

## 🌟 Executive Features Overview

### 1. 📊 Executive Dashboard (`/dashboard`)
- **Academic Term Banner**: Displays current semester ("Fall Semester 2026 • Week 9"), academic standing, cumulative GPA (3.88 / 4.0), and degree progress (108 / 120 units).
- **Core Metrics Overview**: Real-time counter cards for Enrolled Modules (22.0 credits), Pending Deliverables (with overdue warnings), Completed Tasks, and Overall Syllabus Completion.
- **Weekly Study Progress Chart**: High-performance Chart.js dual-dataset chart comparing daily recorded study hours against the university's 25h academic benchmark.
- **Live Class Schedule**: Daily lecture schedule widget displaying course code, title, meeting room, instructor, and "In Progress" status badges.
- **Course Progress Cards**: Direct visual progress bars with one-click "Next Lesson" logger and "View Syllabus" modal launcher.
- **Upcoming Assignment Deadlines**: Priority-tagged deadlines (High, Medium, Low) with overdue indicators and quick completion actions.
- **Academic Timeline**: Real-time audit log of submitted work, lesson milestones, and published grades.

### 2. 🤖 Student LLM AI Study Copilot (Modal Integration)
- Accessible from any page via the top navigation header button: **"Ask LLM Copilot"**.
- Built-in contextual AI tutor capable of answering questions about:
  - Deep Learning & Transformer Self-Attention formulas
  - Kubernetes Helm pipelines & cloud container architecture
  - SQL query profiling, B-tree indexes & EXPLAIN plans
  - Bayesian parameter estimation & statistics
  - Assignment deadlines and prioritization advice
- Interactive quick prompt chips for one-click questions.

### 3. 📚 Enrolled Modules & Syllabi (`/courses`)
- Grid of enrolled modules showing Course Code, Title, Credits (3.0–4.0), Academic Level (Upper Division/Senior/Capstone), Location, and Instructor.
- **Detailed Syllabus Modal**: Comprehensive syllabus breakdown with module outlines and grading weights (e.g., Labs 40%, Midterm 25%, Final Project 35%).
- Interactive category pills (*Artificial Intelligence*, *Systems & Cloud*, *Data Engineering*, *Software Engineering*, *Mathematics*, *Senior Seminar*).
- Live search by title, code, or instructor name.
- Interactive "Continue Learning" button that increments syllabus progress and saves directly to SQLite.

### 4. 📝 Assignment Management & Submission (`/assignments`)
- Filter tabs: **All**, **Pending**, **Submitted**, and **Completed**.
- Priority filtering (High, Medium, Low) and course-specific dropdown.
- **Assignment Submission Modal**: Allows students to submit deliverables with technical notes and GitHub repository URLs.
- **Grade & Evaluation Feedback Display**: Displays instructor grades (e.g., `100/100`) and written faculty feedback.
- Automated overdue indicator flagging pending tasks past due date.
- "+ Add New Assignment" modal dialog with input validation.

### 5. 📖 Digital Resource Library (`/resources`)
- Verified lecture notes, reference textbooks, cheat sheets, and lab code repositories.
- Filterable by Category and Format (*PDF*, *Notes*, *Lab Code*).
- Difficulty badges (*Beginner*, *Intermediate*, *Advanced*).
- Interactive **"Preview Notes" Modal** displaying study summaries and verified direct links to academic papers and documentation.

### 6. 👤 Academic Profile & Transcript (`/profile`)
- Student credentials, degree program, cumulative GPA (3.88/4.0), and weekly target hours.
- **Graduation Degree Audit**: Visual progress bar showing 108 / 120 completed units (90% to degree).
- Working **Profile Edit Form** allowing full name, email, major, phone, target study hours, and bio updates directly saved to SQLite.

### 7. 🔔 Notification Tray
- Top header bell icon with unread count badge.
- Interactive dropdown showing deadline alerts, grade publications, and curriculum updates.
- One-click "Mark read" button that updates state in SQLite.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12+, Flask |
| **Database** | SQLite3 (`instance/student_llm.db`) |
| **Frontend Structure** | Semantic HTML5, Jinja2 Templates |
| **Styling** | Vanilla CSS3 (Custom SaaS Design System, CSS Variables, Responsive Layouts) |
| **Icons** | Lucide Icons (CDN) |
| **Data Visualization** | Chart.js (CDN) |
| **Typography** | Plus Jakarta Sans (Google Fonts) |

---

## 📁 Project Structure

```
task2/
├── app.py                  # Flask server routes, AI Copilot API & data endpoints
├── database.py             # SQLite schema, seed data, queries & CRUD helpers
├── requirements.txt        # Python dependencies (Flask)
├── README.md               # Documentation & execution instructions
│
├── instance/
│   └── student_llm.db      # SQLite database (auto-generated on first run)
│
├── templates/
│   ├── base.html           # Base layout with sidebar, navbar, notifications & modals
│   ├── dashboard.html      # Executive dashboard with banner, Chart.js & schedule
│   ├── courses.html        # Courses grid with syllabus viewer & category pills
│   ├── assignments.html    # Assignments management with priority & submission dialog
│   ├── resources.html      # Resource library with preview modal & difficulty tags
│   └── profile.html        # Academic profile, GPA, degree audit & working edit form
│
└── static/
    ├── css/
    │   └── style.css       # Enterprise SaaS styling & design system
    └── js/
        └── app.js          # Client-side interactions, AI Copilot engine & AJAX
```

---

## 🚀 Quickstart Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Flask Application
```bash
python app.py
```

### Step 3: Open in Browser
Navigate to:
```
http://127.0.0.1:5000
```
or
```
http://localhost:5000
```

---

## 💻 Running in Visual Studio Code

1. Open the folder `task2` in **VS Code**:
   - `File` &rarr; `Open Folder` &rarr; select `task2`.
2. Open the terminal (``Ctrl + ` ``).
3. Ensure your Python 3.x interpreter is active.
4. Execute:
   ```powershell
   python app.py
   ```
5. Click on `http://127.0.0.1:5000` to launch the platform in your browser.

---

## 🧪 Interactive Faculty Demonstration Checklist

- [x] **Executive Academic Banner**: Verify student greeting, GPA, and graduation unit audit.
- [x] **Ask Student LLM AI Copilot**: Click "Ask LLM Copilot" in the header and click any quick chip (e.g. *Transformer Attention* or *Priority Deadlines*) to test the interactive AI tutor.
- [x] **Notification Tray**: Click the bell icon in the top header, inspect notification cards, and click "Mark read".
- [x] **Today's Class Schedule**: Check today's schedule card on the dashboard showing active lectures and room locations.
- [x] **Course Syllabus Viewer**: In `/courses`, click the document icon on any course to open the full syllabus and grading weights modal.
- [x] **Assignment Work Submission**: In `/assignments`, click "Submit Work" on any pending assignment, attach notes/link, and verify submission status.
- [x] **Priority Filtering & Overdue Tags**: Filter assignments by Priority (High/Medium/Low) and check overdue visual flags.
- [x] **Profile Edit Persistence**: In `/profile`, edit target study hours or bio, click Save, and verify instant SQLite updates.
