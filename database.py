import sqlite3
import os
from datetime import datetime, timedelta

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
DB_PATH = os.path.join(DB_DIR, 'student_llm.db')

def get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Student Profile table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            student_id TEXT NOT NULL,
            major TEXT NOT NULL,
            bio TEXT,
            avatar_url TEXT,
            current_semester TEXT,
            gpa REAL DEFAULT 3.88,
            target_study_hours INTEGER DEFAULT 25,
            phone TEXT,
            academic_standing TEXT DEFAULT "Dean's Honor Roll",
            credits_completed INTEGER DEFAULT 108,
            total_credits INTEGER DEFAULT 120
        )
    ''')

    # Courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            title TEXT NOT NULL,
            instructor TEXT NOT NULL,
            instructor_email TEXT DEFAULT 'instructor@university.edu',
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            credits REAL DEFAULT 4.0,
            level TEXT DEFAULT 'Upper Division',
            total_lessons INTEGER NOT NULL DEFAULT 12,
            completed_lessons INTEGER NOT NULL DEFAULT 0,
            progress INTEGER NOT NULL DEFAULT 0,
            color_accent TEXT DEFAULT '#4f46e5',
            schedule TEXT DEFAULT 'Mon, Wed 10:00 AM',
            location TEXT DEFAULT 'Science Hall 402',
            syllabus_summary TEXT
        )
    ''')

    # Assignments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            priority TEXT DEFAULT 'Medium',
            points INTEGER DEFAULT 100,
            grade TEXT,
            feedback TEXT,
            submitted_at TEXT,
            submission_text TEXT,
            submission_url TEXT,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')

    # Learning Resources table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            file_size TEXT,
            read_time TEXT,
            content_snippet TEXT,
            external_url TEXT,
            difficulty TEXT DEFAULT 'Intermediate',
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')

    # Activity Log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            timestamp TEXT NOT NULL,
            icon_name TEXT DEFAULT 'activity'
        )
    ''')

    # Weekly Study Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_name TEXT NOT NULL,
            hours REAL NOT NULL,
            target_hours REAL NOT NULL
        )
    ''')

    # Today's Scheduled Classes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room TEXT NOT NULL,
            instructor TEXT NOT NULL,
            is_active INTEGER DEFAULT 0
        )
    ''')

    # Notifications Tray
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            time_ago TEXT NOT NULL,
            category TEXT DEFAULT 'academic',
            is_read INTEGER DEFAULT 0
        )
    ''')

    conn.commit()

    # Seed data if empty
    cursor.execute('SELECT COUNT(*) FROM student_profile')
    if cursor.fetchone()[0] == 0:
        seed_data(conn)
    else:
        # Check if daily_schedule is empty
        cursor.execute('SELECT COUNT(*) FROM daily_schedule')
        if cursor.fetchone()[0] == 0:
            seed_additional_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    # 1. Seed Profile
    cursor.execute('''
        INSERT INTO student_profile (
            name, email, student_id, major, bio, avatar_url, current_semester,
            gpa, target_study_hours, phone, academic_standing, credits_completed, total_credits
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Alex Morgan',
        'alex.morgan@university.edu',
        'CS-2024-8842',
        'Computer Science & Artificial Intelligence',
        'Senior undergraduate student specializing in machine learning systems, distributed cloud architectures, and scalable web platforms. Preparing for the Spring 2027 Capstone Showcase.',
        'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250',
        'Semester 7 (Senior)',
        3.88,
        25,
        '+1 (555) 349-8210',
        "Dean's First Class Honors",
        108,
        120
    ))

    # 2. Seed Courses with Syllabi & credits
    courses = [
        ('CS-401', 'Deep Learning & Neural Networks', 'Dr. Katherine Vance', 'vance.k@university.edu', 'Artificial Intelligence',
         'Fundamentals of deep feedforward networks, convolutional architectures, and transformer attention mechanisms with PyTorch labs.',
         4.0, 'Upper Division / Senior', 16, 12, 75, '#4f46e5', 'Mon, Wed 10:00 AM - 11:30 AM', 'Turing Hall 402',
         'Module 1: Backpropagation & Optimization (SGD, Adam)\nModule 2: CNNs & Visual Representations (ResNet)\nModule 3: Sequence Modeling & RNN/LSTM\nModule 4: Self-Attention & Vision Transformers\nGrading: Labs 40%, Midterm Exam 25%, Final Project 35%'),
        
        ('CS-305', 'Cloud Infrastructure & DevOps', 'Prof. Marcus Chen', 'chen.m@university.edu', 'Systems & Cloud',
         'Building resilient distributed architectures, container orchestration with Kubernetes, and enterprise CI/CD pipelines.',
         4.0, 'Upper Division', 14, 9, 64, '#06b6d4', 'Tue, Thu 02:00 PM - 03:30 PM', 'Ada Lovelace Virtual Lab',
         'Module 1: Linux Containers & Docker Runtime\nModule 2: Kubernetes Ingress & Autoscaling\nModule 3: Terraform Infrastructure as Code\nModule 4: Prometheus & Grafana Observability\nGrading: Cloud Labs 50%, Architecture Quizzes 20%, Term Project 30%'),
        
        ('CS-320', 'Database Systems & Query Optimization', 'Dr. Elena Rostova', 'rostova.e@university.edu', 'Data Engineering',
         'Relational schema design, ACID transactions, B-Tree indexing, execution plan analysis, and distributed storage engines.',
         3.0, 'Upper Division', 12, 10, 83, '#10b981', 'Mon, Fri 01:30 PM - 03:00 PM', 'von Neumann Hall 210',
         'Module 1: Relational Algebra & Normalization\nModule 2: Query Optimization & EXPLAIN Plans\nModule 3: Concurrency Control & WAL\nModule 4: NoSQL & Distributed Consensus\nGrading: Assignments 35%, Benchmark Lab 25%, Final Exam 40%'),
        
        ('CS-415', 'Full-Stack Web Architectures', 'Prof. Liam Patel', 'patel.l@university.edu', 'Software Engineering',
         'Modern client-server architectures, RESTful API contract design, state management patterns, and web security compliance.',
         4.0, 'Upper Division', 15, 6, 40, '#8b5cf6', 'Wed, Fri 09:00 AM - 10:30 AM', 'Babbage Hall 105',
         'Module 1: High-Performance DOM & Reactive State\nModule 2: RESTful & GraphQL API Contracts\nModule 3: OWASP Security & JWT OAuth\nModule 4: Micro-frontends & Edge Caching\nGrading: Bi-weekly Projects 45%, Code Reviews 15%, Capstone Demo 40%'),
        
        ('MATH-330', 'Applied Probability & Statistics', 'Dr. Sarah Jenkins', 'jenkins.s@university.edu', 'Mathematics',
         'Probability distributions, Bayesian hypothesis testing, Markov chains, and multivariate regression modeling for computing.',
         3.0, 'Core STEM', 12, 3, 25, '#f59e0b', 'Tue, Thu 11:30 AM - 01:00 PM', 'Euclid Hall B',
         'Module 1: Combinatorics & Conditional Probability\nModule 2: Random Variables & Joint Distributions\nModule 3: Central Limit Theorem & Inference\nModule 4: Markov Decision Processes\nGrading: Problem Sets 30%, 2 Midterms 30%, Final 40%'),
        
        ('CS-490', 'Capstone Project & System Design', 'Dr. Robert Torres', 'torres.r@university.edu', 'Senior Seminar',
         'End-to-end design, implementation, and academic presentation of an industry-grade software product or research artifact.',
         4.0, 'Capstone / Honors', 10, 5, 50, '#ec4899', 'Friday 03:00 PM - 05:00 PM', 'Innovation Studio 3',
         'Phase 1: Project Proposal & C4 System Architecture\nPhase 2: Sprint 1 & 2 Prototype Verification\nPhase 3: Security & Load Testing\nPhase 4: Faculty Jury Presentation\nGrading: Architecture 25%, Working Prototype 45%, Final Defense 30%')
    ]

    cursor.executemany('''
        INSERT INTO courses (
            code, title, instructor, instructor_email, category, description,
            credits, level, total_lessons, completed_lessons, progress, color_accent, schedule, location, syllabus_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', courses)

    # 3. Seed Assignments
    today = datetime.now()
    assignments = [
        (1, 'Implement Transformer Self-Attention Layer',
         'Build scaled dot-product multi-head attention from scratch using PyTorch tensors. Include shape assertions and unit tests.',
         (today + timedelta(days=2)).strftime('%Y-%m-%d'), 'Pending', 'High', 100, None, None, None, None, None),
        
        (2, 'Kubernetes Helm Deployment Pipeline',
         'Configure a production Helm chart with horizontal pod autoscaling (HPA) and ingress routing rules for microservices.',
         (today + timedelta(days=5)).strftime('%Y-%m-%d'), 'Pending', 'Medium', 100, None, None, None, None, None),
        
        (3, 'SQL Query Profiling & Index Optimization Lab',
         'Analyze execution plans for slow nested join queries on a 5M row dataset. Benchmark B-Tree vs Hash index performance.',
         (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'Pending', 'High', 75, None, None, None, None, None), # Overdue
        
        (4, 'REST API Authentication & Token Refresh',
         'Implement stateless JWT token issuance, refresh token rotation, and role-based route guard middleware.',
         (today + timedelta(days=8)).strftime('%Y-%m-%d'), 'Submitted', 'Medium', 100, None, None,
         (today - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'),
         'Submitted git commit SHA-256 for review. Implemented rotating refresh cookies with HTTP-only flags.', 'https://github.com/alex-morgan/auth-service'),
        
        (5, 'Bayesian Parameter Estimation Problem Set',
         'Derive posterior distributions for conjugate priors and compute 95% credible intervals in a Jupyter notebook.',
         (today - timedelta(days=4)).strftime('%Y-%m-%d'), 'Completed', 'Low', 100, '98/100',
         'Flawless mathematical proof for Beta-Binomial conjugate pair. Great visualization of prior vs posterior distributions.',
         (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M'), 'All analytical proofs provided in LaTeX appendix.', None),
        
        (1, 'CNN Image Classification Benchmark',
         'Train ResNet-18 variant on CIFAR-10 dataset achieving >88% test set accuracy with data augmentations.',
         (today - timedelta(days=7)).strftime('%Y-%m-%d'), 'Completed', 'High', 100, '100/100',
         'Outstanding performance! Achieved 89.4% test accuracy with Cosine Annealing learning rate schedule.',
         (today - timedelta(days=8)).strftime('%Y-%m-%d %H:%M'), 'Code and training logs uploaded to cluster registry.', None),
        
        (6, 'Capstone Project Scope & Architectural Diagram',
         'Submit system context diagram (C4 Model Level 1 & 2) and technical dependency matrix for faculty committee review.',
         (today + timedelta(days=12)).strftime('%Y-%m-%d'), 'Pending', 'High', 50, None, None, None, None, None)
    ]

    cursor.executemany('''
        INSERT INTO assignments (
            course_id, title, description, due_date, status, priority, points,
            grade, feedback, submitted_at, submission_text, submission_url
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', assignments)

    # 4. Seed Resources
    resources = [
        (1, 'Attention Is All You Need - Annotated Reading Notes', 'Lecture Notes', 'Notes', '420 KB', '25 min read',
         'Key conceptual breakdown of Multi-Head Scaled Dot-Product Attention, Positional Encodings, and residual layer normalization formulas.',
         'https://arxiv.org/abs/1706.03762', 'Advanced'),
        (1, 'PyTorch Tensor Operations & Autograd Quick Reference', 'Cheat Sheet', 'PDF', '1.8 MB', '15 min read',
         'Compact reference sheet containing common tensor reshaping (view, transpose, permute), broadcasting rules, and backward graph operations.',
         'https://pytorch.org/docs/stable/torch.html', 'Intermediate'),
        (2, 'Kubernetes Production Best Practices Guidebook', 'Reference Book', 'PDF', '5.4 MB', '45 min read',
         'Comprehensive deployment patterns: resource requests and limits, readiness/liveness probes, ConfigMaps, and secret management.',
         'https://kubernetes.io/docs/concepts/', 'Advanced'),
        (3, 'Database Normalization & Indexing Cheat Sheet', 'Cheat Sheet', 'PDF', '1.1 MB', '10 min read',
         'Visual summary of 1NF through BCNF normalization rules, composite index leftmost prefixing, and EXPLAIN command analysis.',
         'https://use-the-index-luke.com/', 'Beginner'),
        (4, 'Web Security Checklist: OWASP Top 10 Mitigations', 'Lecture Notes', 'Notes', '680 KB', '20 min read',
         'Practical security safeguards: CSRF token patterns, Content Security Policy (CSP) headers, and parameterized SQL prevention.',
         'https://owasp.org/www-project-top-ten/', 'Intermediate'),
        (5, 'Statistical Distributions Summary & Formulas', 'Lecture Notes', 'PDF', '2.2 MB', '30 min read',
         'Mathematical properties, PDF/PMF equations, expected values, and variances for Normal, Poisson, Binomial, and Gamma distributions.',
         'https://online.stat.psu.edu/stat414/', 'Intermediate'),
        (2, 'Terraform Infrastructure as Code Sample Repository', 'Practice Lab', 'Lab Code', '3.1 MB', '40 min lab',
         'Modular Terraform definitions provisioning AWS VPC, subnets, route tables, and EKS managed node groups with tagging standards.',
         'https://developer.hashicorp.com/terraform', 'Advanced'),
        (6, 'Software Architecture Document (SAD) Template', 'Reference Book', 'Notes', '350 KB', '15 min read',
         'Industry-standard IEEE 1471/ISO 42010 aligned template for documenting architectural styles, quality attributes, and interface contracts.',
         'https://c4model.com/', 'Intermediate')
    ]

    cursor.executemany('''
        INSERT INTO resources (course_id, title, category, resource_type, file_size, read_time, content_snippet, external_url, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', resources)

    # 5. Seed Activities
    activities = [
        ('assignment_submit', 'Submitted Assignment', 'REST API Authentication & Token Refresh was submitted for grading.',
         (today - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'), 'check-circle-2'),
        ('course_progress', 'Completed Lesson 12', 'Finished "Multi-Head Attention Layers" in Deep Learning & Neural Networks.',
         (today - timedelta(hours=7)).strftime('%Y-%m-%d %H:%M'), 'book-open'),
        ('resource_view', 'Accessed Study Material', 'Read "Kubernetes Production Best Practices Guidebook".',
         (today - timedelta(days=1, hours=2)).strftime('%Y-%m-%d %H:%M'), 'file-text'),
        ('assignment_grade', 'Grade Published (100/100)', 'Received full marks on CNN Image Classification Benchmark.',
         (today - timedelta(days=2)).strftime('%Y-%m-%d %H:%M'), 'award'),
        ('course_enrolled', 'Course Enrolled', 'Enrolled in Capstone Project & System Design with Dr. Robert Torres.',
         (today - timedelta(days=6)).strftime('%Y-%m-%d %H:%M'), 'graduation-cap')
    ]

    cursor.executemany('''
        INSERT INTO activities (activity_type, title, description, timestamp, icon_name)
        VALUES (?, ?, ?, ?, ?)
    ''', activities)

    # 6. Seed Weekly Study Logs
    study_logs = [
        ('Mon', 4.5, 4.0),
        ('Tue', 3.0, 3.5),
        ('Wed', 5.5, 4.0),
        ('Thu', 4.0, 3.5),
        ('Fri', 6.0, 4.0),
        ('Sat', 2.5, 3.0),
        ('Sun', 3.5, 3.0)
    ]

    cursor.executemany('''
        INSERT INTO study_logs (day_name, hours, target_hours)
        VALUES (?, ?, ?)
    ''', study_logs)

    seed_additional_data(conn)
    conn.commit()

def seed_additional_data(conn):
    cursor = conn.cursor()
    # 7. Today's Classes Schedule
    classes = [
        ('CS-401', 'Deep Learning & Neural Networks', '10:00 AM', '11:30 AM', 'Turing Hall 402', 'Dr. Katherine Vance', 1),
        ('MATH-330', 'Applied Probability & Statistics', '11:30 AM', '01:00 PM', 'Euclid Hall B', 'Dr. Sarah Jenkins', 0),
        ('CS-320', 'Database Systems & Query Optimization', '01:30 PM', '03:00 PM', 'von Neumann Hall 210', 'Dr. Elena Rostova', 0)
    ]
    cursor.executemany('''
        INSERT INTO daily_schedule (course_code, title, start_time, end_time, room, instructor, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', classes)

    # 8. Notifications Tray
    notifications = [
        ('Assignment Deadline Warning', 'SQL Query Profiling lab is due soon. Check submission criteria.', '1 hour ago', 'alert', 0),
        ('Grade Published', 'Dr. Vance published your score: 100/100 on CNN Benchmark.', '2 days ago', 'academic', 0),
        ('Curriculum Announcement', 'New Kubernetes Helm slides uploaded by Prof. Marcus Chen.', '3 days ago', 'course', 1),
        ('Dean\'s List Recognition', 'Congratulations! Your Fall GPA places you in the top 5% of class.', '5 days ago', 'honor', 1)
    ]
    cursor.executemany('''
        INSERT INTO notifications (title, message, time_ago, category, is_read)
        VALUES (?, ?, ?, ?, ?)
    ''', notifications)

# Helper queries
def get_student_profile():
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM student_profile LIMIT 1').fetchone()
    conn.close()
    return profile

def update_student_profile(name, email, major, bio, target_study_hours, phone):
    conn = get_db_connection()
    conn.execute('''
        UPDATE student_profile
        SET name = ?, email = ?, major = ?, bio = ?, target_study_hours = ?, phone = ?
        WHERE id = 1
    ''', (name, email, major, bio, target_study_hours, phone))
    conn.commit()
    conn.close()

def get_courses(category=None, search=None):
    conn = get_db_connection()
    query = 'SELECT * FROM courses WHERE 1=1'
    params = []
    if category and category != 'All':
        query += ' AND category = ?'
        params.append(category)
    if search:
        query += ' AND (title LIKE ? OR code LIKE ? OR instructor LIKE ?)'
        search_pattern = f'%{search}%'
        params.extend([search_pattern, search_pattern, search_pattern])
    query += ' ORDER BY progress DESC'
    courses = conn.execute(query, params).fetchall()
    conn.close()
    return courses

def get_course_by_id(course_id):
    conn = get_db_connection()
    course = conn.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    conn.close()
    return course

def get_course_categories():
    conn = get_db_connection()
    rows = conn.execute('SELECT DISTINCT category FROM courses ORDER BY category').fetchall()
    conn.close()
    return [r['category'] for r in rows]

def get_assignments(status=None, course_id=None, priority=None, search=None):
    conn = get_db_connection()
    query = '''
        SELECT a.*, c.title AS course_title, c.code AS course_code, c.color_accent
        FROM assignments a
        JOIN courses c ON a.course_id = c.id
        WHERE 1=1
    '''
    params = []
    if status and status != 'All':
        query += ' AND a.status = ?'
        params.append(status)
    if course_id and course_id != 'All':
        query += ' AND a.course_id = ?'
        params.append(course_id)
    if priority and priority != 'All':
        query += ' AND a.priority = ?'
        params.append(priority)
    if search:
        query += ' AND (a.title LIKE ? OR c.title LIKE ?)'
        search_pattern = f'%{search}%'
        params.extend([search_pattern, search_pattern])
    
    query += ' ORDER BY a.due_date ASC'
    assignments = conn.execute(query, params).fetchall()
    conn.close()
    return assignments

def update_assignment_status(assignment_id, new_status, submission_text=None, submission_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M') if new_status in ['Submitted', 'Completed'] else None
    
    cursor.execute('''
        UPDATE assignments
        SET status = ?, submitted_at = COALESCE(?, submitted_at),
            submission_text = COALESCE(?, submission_text),
            submission_url = COALESCE(?, submission_url)
        WHERE id = ?
    ''', (new_status, submitted_at, submission_text, submission_url, assignment_id))
    
    assignment = cursor.execute('''
        SELECT a.title, c.title AS course_title 
        FROM assignments a 
        JOIN courses c ON a.course_id = c.id 
        WHERE a.id = ?
    ''', (assignment_id,)).fetchone()
    
    if assignment:
        action_title = f"Assignment Marked {new_status}"
        desc = f"'{assignment['title']}' for {assignment['course_title']} set to {new_status}."
        icon = "check-circle-2" if new_status == 'Completed' else ("send" if new_status == 'Submitted' else "clock")
        cursor.execute('''
            INSERT INTO activities (activity_type, title, description, timestamp, icon_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('assignment_update', action_title, desc, datetime.now().strftime('%Y-%m-%d %H:%M'), icon))

    conn.commit()
    conn.close()

def create_assignment(course_id, title, description, due_date, priority='Medium', points=100):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO assignments (course_id, title, description, due_date, priority, status, points)
        VALUES (?, ?, ?, ?, ?, 'Pending', ?)
    ''', (course_id, title, description, due_date, priority, points))
    
    cursor.execute('''
        INSERT INTO activities (activity_type, title, description, timestamp, icon_name)
        VALUES (?, ?, ?, ?, ?)
    ''', ('assignment_create', 'New Assignment Added', f"Task '{title}' scheduled for {due_date} ({priority} Priority).",
          datetime.now().strftime('%Y-%m-%d %H:%M'), 'plus-circle'))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_resources(category=None, resource_type=None, search=None):
    conn = get_db_connection()
    query = '''
        SELECT r.*, c.title AS course_title, c.code AS course_code
        FROM resources r
        LEFT JOIN courses c ON r.course_id = c.id
        WHERE 1=1
    '''
    params = []
    if category and category != 'All':
        query += ' AND r.category = ?'
        params.append(category)
    if resource_type and resource_type != 'All':
        query += ' AND r.resource_type = ?'
        params.append(resource_type)
    if search:
        query += ' AND (r.title LIKE ? OR r.content_snippet LIKE ? OR c.title LIKE ?)'
        sp = f'%{search}%'
        params.extend([sp, sp, sp])
    query += ' ORDER BY r.id ASC'
    resources = conn.execute(query, params).fetchall()
    conn.close()
    return resources

def get_resource_categories():
    conn = get_db_connection()
    rows = conn.execute('SELECT DISTINCT category FROM resources ORDER BY category').fetchall()
    conn.close()
    return [r['category'] for r in rows]

def get_activities(limit=6):
    conn = get_db_connection()
    activities = conn.execute('SELECT * FROM activities ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return activities

def get_study_logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM study_logs ORDER BY id ASC').fetchall()
    conn.close()
    return logs

def get_daily_schedule():
    conn = get_db_connection()
    schedule = conn.execute('SELECT * FROM daily_schedule ORDER BY id ASC').fetchall()
    conn.close()
    return schedule

def get_notifications():
    conn = get_db_connection()
    notifs = conn.execute('SELECT * FROM notifications ORDER BY id DESC LIMIT 5').fetchall()
    unread_count = conn.execute('SELECT COUNT(*) FROM notifications WHERE is_read = 0').fetchone()[0]
    conn.close()
    return notifs, unread_count

def mark_notifications_read():
    conn = get_db_connection()
    conn.execute('UPDATE notifications SET is_read = 1')
    conn.commit()
    conn.close()

def update_course_progress(course_id, completed_lessons):
    conn = get_db_connection()
    cursor = conn.cursor()
    course = cursor.execute('SELECT total_lessons FROM courses WHERE id = ?', (course_id,)).fetchone()
    if course:
        total = course['total_lessons']
        completed = min(max(0, completed_lessons), total)
        progress = int((completed / total) * 100) if total > 0 else 0
        cursor.execute('''
            UPDATE courses
            SET completed_lessons = ?, progress = ?
            WHERE id = ?
        ''', (completed, progress, course_id))
        conn.commit()
    conn.close()

def get_dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    total_courses = cursor.execute('SELECT COUNT(*) FROM courses').fetchone()[0]
    pending_assignments = cursor.execute("SELECT COUNT(*) FROM assignments WHERE status = 'Pending'").fetchone()[0]
    completed_assignments = cursor.execute("SELECT COUNT(*) FROM assignments WHERE status = 'Completed'").fetchone()[0]
    submitted_assignments = cursor.execute("SELECT COUNT(*) FROM assignments WHERE status = 'Submitted'").fetchone()[0]
    
    avg_progress = cursor.execute('SELECT AVG(progress) FROM courses').fetchone()[0] or 0
    weekly_hours = cursor.execute('SELECT SUM(hours) FROM study_logs').fetchone()[0] or 0
    weekly_target = cursor.execute('SELECT SUM(target_hours) FROM study_logs').fetchone()[0] or 25
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    overdue_assignments = cursor.execute(
        "SELECT COUNT(*) FROM assignments WHERE status = 'Pending' AND due_date < ?", (today_str,)
    ).fetchone()[0]

    conn.close()

    return {
        'total_courses': total_courses,
        'pending_assignments': pending_assignments,
        'completed_assignments': completed_assignments,
        'submitted_assignments': submitted_assignments,
        'avg_progress': round(avg_progress, 1),
        'weekly_hours': round(weekly_hours, 1),
        'weekly_target': round(weekly_target, 1),
        'overdue_assignments': overdue_assignments
    }
