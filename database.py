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
            gpa REAL DEFAULT 10.0,
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

    # Companies & Placement Drives
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies_drives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            logo_badge TEXT NOT NULL,
            logo_color TEXT DEFAULT '#4f46e5',
            role_title TEXT NOT NULL,
            package_lpa TEXT NOT NULL,
            location TEXT NOT NULL,
            drive_date TEXT NOT NULL,
            deadline_date TEXT NOT NULL,
            min_gpa REAL DEFAULT 8.0,
            eligible_branches TEXT DEFAULT 'CS, AI, IT, ECE',
            status TEXT DEFAULT 'Open',
            rounds_count INTEGER DEFAULT 4,
            rounds_detail TEXT,
            job_description TEXT,
            tags TEXT
        )
    ''')

    # Student Drive Applications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_drive_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drive_id INTEGER NOT NULL,
            student_id INTEGER DEFAULT 1,
            applied_at TEXT NOT NULL,
            status TEXT DEFAULT 'Applied',
            resume_link TEXT,
            cover_note TEXT,
            FOREIGN KEY (drive_id) REFERENCES companies_drives (id)
        )
    ''')

    # Course Attendance Records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            session_date TEXT NOT NULL,
            session_topic TEXT NOT NULL,
            status TEXT NOT NULL,
            remarks TEXT,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')

    # Student & Placement Feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            target_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review_title TEXT NOT NULL,
            review_text TEXT NOT NULL,
            author_name TEXT NOT NULL,
            is_anonymous INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            upvotes INTEGER DEFAULT 0,
            sentiment TEXT DEFAULT 'Positive'
        )
    ''')

    conn.commit()

    # Seed data if empty
    cursor.execute('SELECT COUNT(*) FROM student_profile')
    if cursor.fetchone()[0] == 0:
        seed_data(conn)
    else:
        # Automatically migrate existing profile to Ajay Reddy and 10.0 CGPA
        cursor.execute('''
            UPDATE student_profile
            SET name = 'Ajay Reddy', email = 'ajay.reddy@university.edu', gpa = 10.0
            WHERE name = 'Alex Morgan' OR gpa <= 4.0
        ''')
        conn.commit()

        # Check if daily_schedule is empty
        cursor.execute('SELECT COUNT(*) FROM daily_schedule')
        if cursor.fetchone()[0] == 0:
            seed_additional_data(conn)

    # Check and seed companies_drives
    cursor.execute('SELECT COUNT(*) FROM companies_drives')
    if cursor.fetchone()[0] == 0:
        seed_placement_data(conn)

    # Check and seed attendance_records
    cursor.execute('SELECT COUNT(*) FROM attendance_records')
    if cursor.fetchone()[0] == 0:
        seed_attendance_data(conn)

    # Check and seed feedback_submissions
    cursor.execute('SELECT COUNT(*) FROM feedback_submissions')
    if cursor.fetchone()[0] == 0:
        seed_feedback_data(conn)

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
        'Ajay Reddy',
        'ajay.reddy@university.edu',
        'CS-2024-8842',
        'Computer Science & Artificial Intelligence',
        'Senior undergraduate student specializing in machine learning systems, distributed cloud architectures, and scalable web platforms. Preparing for the Spring 2027 Capstone Showcase.',
        'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250',
        'Semester 7 (Senior)',
        10.0,
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

def seed_placement_data(conn):
    cursor = conn.cursor()
    drives = [
        ('Google', 'GOOGL', '#4285f4', 'Staff Software Engineer - Cloud & AI', '$175,000 / 48 LPA',
         'Mountain View / Hybrid', '2026-11-15', '2026-11-05', 8.5, 'CS, AI, IT, ECE', 'Open', 4,
         'Round 1: 90min Online Coding OA (LeetCode Hard Graphs & DP)\nRound 2: Technical Interview 1 (Distributed Algorithms)\nRound 3: System Design (Scalable Pub/Sub Queue)\nRound 4: Googleyness & Leadership Principles',
         'Join Google Cloud Core Engineering team building next-gen hyperscale infrastructure, Tensor Processing Unit runtime orchestration, and global distributed storage layers.',
         'Tier-1 Global, Top CTC, High Impact'),

        ('NVIDIA', 'NVDA', '#10b981', 'AI Platform & CUDA Systems Engineer', '$185,000 / 52 LPA',
         'Santa Clara / Austin', '2026-11-22', '2026-11-10', 8.8, 'CS, AI, ECE', 'Open', 4,
         'Round 1: Low-level C++ & GPU Compute OA\nRound 2: CUDA Kernel Optimization & Memory Hierarchy\nRound 3: Transformer Serving & TensorRT Benchmarking\nRound 4: Director Systems Architecture Panel',
         'Architect cutting-edge GPU kernel acceleration for LLM inference clusters. Optimize memory access, NCCL inter-node communications, and TensorRT deployment runtimes.',
         'Semiconductor, AI Hardware, Elite'),

        ('Microsoft', 'MSFT', '#0284c7', 'Azure Distributed Cloud Engineer', '$155,000 / 42 LPA',
         'Redmond / Hyderabad', '2026-12-02', '2026-11-20', 8.0, 'CS, AI, IT', 'Shortlisted', 3,
         'Round 1: Codility Algorithm Assessment\nRound 2: Live Virtual Onsite (Microservices & Concurrency)\nRound 3: Azure Architecture & Hiring Manager Discussion',
         'Develop mission-critical control planes for Azure Kubernetes Service (AKS), edge compute nodes, and cloud-native state replication across availability zones.',
         'Cloud Leader, Fortune 50, Hybrid'),

        ('Amazon AWS', 'AWS', '#f59e0b', 'SDE II - Distributed Storage Systems', '$160,000 / 44 LPA',
         'Seattle / Bangalore', '2026-12-08', '2026-11-25', 8.0, 'CS, AI, IT', 'Applied', 4,
         'Round 1: HackerRank Coding + AWS Work Style Assessment\nRound 2: Deep Dive Data Structures & B-Trees\nRound 3: Object-Oriented & System Architecture\nRound 4: Amazon Leadership Principles & Bar Raiser',
         'Engineer exabyte-scale key-value storage primitives, consensus algorithms (Raft/Paxos), and multi-tenant isolation protocols for AWS storage services.',
         'Tier-1 Global, High Growth, AWS'),

        ('Goldman Sachs', 'GS', '#6366f1', 'Quantitative Technology & High-Frequency Systems', '$165,000 / 45 LPA',
         'New York / Hybrid', '2026-12-14', '2026-12-01', 8.5, 'CS, AI, Math, Finance', 'Open', 3,
         'Round 1: Quantitative Probability & Algorithmic Problem Solving\nRound 2: Low-Latency Java/C++ Systems & Memory Profiling\nRound 3: Superday Panel with Senior Trading Strategists',
         'Build ultra-low latency execution engines, risk simulation pipelines, and automated algorithmic trading platforms operating at sub-millisecond precision.',
         'FinTech, Wall Street, Elite Package'),

        ('Atlassian', 'ATLS', '#06b6d4', 'Full-Stack Platform Infrastructure Engineer', '$142,000 / 38 LPA',
         'Remote / Sydney', '2026-12-20', '2026-12-08', 7.8, 'CS, AI, IT, Software', 'Open', 3,
         'Round 1: HackerRank OA (Data Structures & RESTful Contract Design)\nRound 2: Pair Programming (Building Real-time Collab Feature)\nRound 3: System Architecture & Values Fit',
         'Design distributed real-time collaboration engines, high-speed GraphQL gateways, and asynchronous event streams powering millions of developers worldwide.',
         'Work From Anywhere, Developer Tools, Tier-1'),

        ('Adobe', 'ADBE', '#ef4444', 'Generative AI & Creative Cloud Engineer', '$158,000 / 43 LPA',
         'San Jose / Noida', '2027-01-08', '2026-12-28', 8.2, 'CS, AI, Data Science', 'Upcoming', 4,
         'Round 1: Computer Vision & Python Algorithmic Test\nRound 2: Diffusion Models & Image Synthesis Lab\nRound 3: Scalable Web Inference Architecture\nRound 4: Engineering Director Interview',
         'Contribute to Adobe Firefly research, latent diffusion models, neural rendering pipelines, and real-time generative media APIs deployed across Creative Cloud.',
         'Generative AI, Innovation Lab, High CTC'),

        ('Apple', 'AAPL', '#8b5cf6', 'CoreOS Systems & Machine Intelligence', '$170,000 / 46 LPA',
         'Cupertino / Hybrid', '2027-01-15', '2027-01-02', 8.7, 'CS, AI, ECE', 'Upcoming', 4,
         'Round 1: Low-level Systems OA (POSIX Threads, Pointers, Memory)\nRound 2: Operating System Internals & Cache Architecture\nRound 3: CoreML Neural Engine Acceleration\nRound 4: Apple Leadership & Architecture Jury',
         'Pioneer embedded machine intelligence on Apple Silicon. Optimize unified memory bandwidth, CoreML hardware acceleration, and next-generation operating system primitives.',
         'Hardware-Software Synergy, Elite Prestige, Silicon Valley')
    ]

    cursor.executemany('''
        INSERT INTO companies_drives (
            company_name, logo_badge, logo_color, role_title, package_lpa,
            location, drive_date, deadline_date, min_gpa, eligible_branches, status,
            rounds_count, rounds_detail, job_description, tags
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', drives)

    # Seed initial student drive applications for Ajay Reddy
    cursor.execute('''
        INSERT INTO student_drive_applications (drive_id, student_id, applied_at, status, resume_link, cover_note)
        VALUES (3, 1, '2026-10-15 14:30', 'Shortlisted', 'https://ajayreddy.dev/resume.pdf', 'Applied for Azure Cloud Systems position with strong emphasis on Kubernetes and distributed storage.')
    ''')
    cursor.execute('''
        INSERT INTO student_drive_applications (drive_id, student_id, applied_at, status, resume_link, cover_note)
        VALUES (4, 1, '2026-10-18 09:15', 'Applied', 'https://ajayreddy.dev/resume.pdf', 'Prepared for AWS SDE II distributed systems role.')
    ''')
    conn.commit()

def seed_attendance_data(conn):
    cursor = conn.cursor()
    today = datetime.now()
    attendance_records = []
    
    # CS-401 Deep Learning (Course ID: 1) - 24 classes: 22 Present, 1 Late, 1 Absent (95.8%)
    cs401_topics = [
        "Introduction to Deep Learning & Perceptrons", "Gradient Descent & Backpropagation Derivatives",
        "Loss Functions & Cross-Entropy", "Stochastic & Mini-batch Optimization (Adam, RMSProp)",
        "Vanishing/Exploding Gradients & BatchNorm", "Convolutional Filters & Feature Maps",
        "ResNet Architecture & Residual Connections", "Data Augmentation & Regularization Strategies",
        "Recurrent Neural Networks & BPTT", "LSTM & GRU Gating Mechanisms",
        "Sequence to Sequence & Encoder-Decoder", "Attention Mechanism & Bahdanau Alignment",
        "Transformer Scaled Dot-Product Attention", "Multi-Head Attention & Positional Encodings",
        "Transformer Layer Normalization & FFN", "Vision Transformers (ViT) Architecture",
        "Generative Adversarial Networks (GANs)", "Variational Autoencoders (VAEs)",
        "Diffusion Models & Denoising Objectives", "Reinforcement Learning with PPO",
        "PyTorch Model Profiling & GPU Memory", "Distributed Data Parallel (DDP)",
        "Midterm Lab Exam & Benchmark Review", "Capstone Deep Learning Project Showcase"
    ]
    for i, topic in enumerate(cs401_topics):
        date_str = (today - timedelta(days=(24 - i) * 2 + 1)).strftime('%Y-%m-%d')
        status = 'Absent' if i == 5 else ('Late' if i == 11 else 'Present')
        remarks = 'On time' if status == 'Present' else ('Arrived 10 min late' if status == 'Late' else 'Medical leave notice submitted')
        attendance_records.append((1, date_str, topic, status, remarks))

    # CS-305 Cloud Infrastructure (Course ID: 2) - 20 classes: 18 Present, 2 Absent (90.0%)
    cs305_topics = [
        "Linux Virtualization & Cgroups", "Docker Container Images & Multi-stage Builds",
        "Container Networking & Storage Volumes", "Kubernetes Architecture Overview",
        "Pods, ReplicaSets, and Deployments", "ClusterIP & NodePort Services",
        "Kubernetes Ingress Controllers & NGINX", "ConfigMaps & Secrets Encryption",
        "Persistent Volumes & CSI Drivers", "Helm Chart Templates & Packaging",
        "Helm Multi-environment Releases", "Horizontal Pod Autoscaler (HPA)",
        "Terraform Providers & State Management", "AWS VPC & Subnet Automation",
        "EKS Cluster Provisioning with Terraform", "CI/CD GitHub Actions & Docker Push",
        "Prometheus Metrics & AlertManager", "Grafana Dashboard Observability",
        "Distributed Tracing with OpenTelemetry", "Site Reliability Engineering (SRE) Post-Mortems"
    ]
    for i, topic in enumerate(cs305_topics):
        date_str = (today - timedelta(days=(20 - i) * 2 + 2)).strftime('%Y-%m-%d')
        status = 'Absent' if i in [3, 14] else 'Present'
        remarks = 'Full participation' if status == 'Present' else 'Missed due to hackathon clash'
        attendance_records.append((2, date_str, topic, status, remarks))

    # CS-320 Database Systems (Course ID: 3) - 22 classes: 19 Present, 1 Late, 2 Absent (86.4%)
    cs320_topics = [
        "Relational Model & Codd's Rules", "Relational Algebra Operators",
        "Complex SQL Queries & CTEs", "Window Functions & Analytic Partitions",
        "Schema Design & 1NF to BCNF Normalization", "Storage Engines & Page Layouts",
        "B-Tree & B+ Tree Indexing Internals", "Hash Indexes & LSM Trees",
        "Query Parsing & Logical Query Plans", "Cost-Based Query Optimizer & EXPLAIN",
        "Transaction ACID Properties", "Concurrency Control & 2PL Locking",
        "Deadlock Detection & Resolution", "Write-Ahead Logging (WAL) & ARIES",
        "Database Crash Recovery Mechanisms", "Distributed Databases & CAP Theorem",
        "Consensus Protocols: Two-Phase Commit", "Distributed Sharding & Partition Keys",
        "NoSQL Document Stores vs Relational", "Benchmark Lab: 5M Row Joins",
        "PostgreSQL Performance Tuning", "Columnar Stores & Analytical Warehouses"
    ]
    for i, topic in enumerate(cs320_topics):
        date_str = (today - timedelta(days=(22 - i) * 2 + 1)).strftime('%Y-%m-%d')
        status = 'Absent' if i in [4, 16] else ('Late' if i == 9 else 'Present')
        remarks = 'Active in lab' if status == 'Present' else ('Traffic delay' if status == 'Late' else 'Excused absence')
        attendance_records.append((3, date_str, topic, status, remarks))

    # CS-415 Web Architectures (Course ID: 4) - 18 classes: 16 Present, 2 Absent (88.9%)
    cs415_topics = [
        "Modern Browser Architecture & Event Loop", "DOM Tree Rendering & Reflow Optimization",
        "CSS Grid, Flexbox & Responsive Layouts", "JavaScript Engines & V8 Optimization",
        "Client-side State Management Patterns", "REST API Contract Design & Standards",
        "GraphQL Schemas, Resolvers & DataLoader", "WebSockets & Real-time Bi-directional Comms",
        "Browser Security: SOP, CORS, CSP", "Authentication: JWT, Sessions & OAuth2",
        "OWASP Top 10 Web Vulnerabilities", "Service Workers & Progressive Web Apps",
        "Performance Audits: Core Web Vitals (LCP, INP)", "Edge Caching & Cloudflare Workers",
        "Micro-Frontends & Module Federation", "Server-Side Rendering (SSR) vs SSG",
        "End-to-End Testing with Playwright", "Full-Stack System Design Case Study"
    ]
    for i, topic in enumerate(cs415_topics):
        date_str = (today - timedelta(days=(18 - i) * 2 + 3)).strftime('%Y-%m-%d')
        status = 'Absent' if i in [2, 11] else 'Present'
        remarks = 'Engaged' if status == 'Present' else 'Unexcused absence'
        attendance_records.append((4, date_str, topic, status, remarks))

    # MATH-330 Applied Statistics (Course ID: 5) - 20 classes: 16 Present, 4 Absent (80.0%)
    math_topics = [
        "Sample Spaces & Axioms of Probability", "Conditional Probability & Bayes Theorem",
        "Discrete Random Variables: Binomial, Poisson", "Continuous Variables: Normal, Exponential",
        "Joint Probability Distributions & Covariance", "Expectation, Variance & Moments",
        "Central Limit Theorem & Law of Large Numbers", "Parameter Estimation: Method of Moments",
        "Maximum Likelihood Estimation (MLE)", "Confidence Intervals & Margin of Error",
        "Hypothesis Testing: Z-test & Student t-test", "P-values, Type I & Type II Errors",
        "Chi-Square Goodness of Fit Test", "Linear Regression & Ordinary Least Squares",
        "Multiple Regression & Collinearity", "Bayesian Inference: Prior & Likelihood",
        "Conjugate Priors: Beta-Binomial Model", "Markov Chains & Transition Matrices",
        "Stationary Distributions & Ergodicity", "Monte Carlo Simulation Methods"
    ]
    for i, topic in enumerate(math_topics):
        date_str = (today - timedelta(days=(20 - i) * 2 + 1)).strftime('%Y-%m-%d')
        status = 'Absent' if i in [1, 7, 13, 17] else 'Present'
        remarks = 'Attended' if status == 'Present' else 'Missed lecture'
        attendance_records.append((5, date_str, topic, status, remarks))

    # CS-490 Capstone Project (Course ID: 6) - 12 classes: 12 Present (100%)
    capstone_topics = [
        "Capstone Proposal & Problem Definition", "Literature Review & Prior Art Analysis",
        "System Requirements Specification (SRS)", "C4 Architecture Diagrams (Context & Container)",
        "Sprint 1 Prototype Demo & Faculty Feedback", "Database Schema & API Design Defense",
        "Sprint 2 Implementation Review", "Integration Testing & Security Audits",
        "Load Testing & Latency Benchmarks", "Pre-Defense Jury Rehearsal",
        "User Acceptance Testing & Feedback", "Final Capstone Presentation"
    ]
    for i, topic in enumerate(capstone_topics):
        date_str = (today - timedelta(days=(12 - i) * 4 + 2)).strftime('%Y-%m-%d')
        status = 'Present'
        remarks = 'Sprint review completed'
        attendance_records.append((6, date_str, topic, status, remarks))

    cursor.executemany('''
        INSERT INTO attendance_records (course_id, session_date, session_topic, status, remarks)
        VALUES (?, ?, ?, ?, ?)
    ''', attendance_records)
    conn.commit()

def seed_feedback_data(conn):
    cursor = conn.cursor()
    feedbacks = [
        ('Course Curriculum', 'CS-401 Deep Learning', 5,
         'PyTorch Tensor & Self-Attention Labs are World Class',
         'The curriculum hands-on exercises for building Transformers from scratch gave me immense confidence during company technical interviews. Dr. Vance explains complex backpropagation gradients with unmatched clarity.',
         'Priya Sharma', 0, '2026-10-18 16:40', 38, 'Positive'),

        ('Placement & Career Drives', 'Google Campus Drive', 5,
         'System Architecture Mock Interviews Were Invaluable',
         'The placement cell coordinated with Google engineering alumni to conduct realistic mock interviews. The distributed queues question in Round 3 was identical to what we practiced in our capstone prep sessions.',
         'Ajay Reddy', 0, '2026-10-19 11:20', 47, 'Positive'),

        ('Faculty Guidance', 'Dr. Katherine Vance', 5,
         'Incredible mentorship and research office hours',
         'Dr. Vance always dedicates extra time after hours to review thesis proposals and debugging PyTorch GPU memory leaks. Outstanding academic mentor!',
         'Marcus Chen', 0, '2026-10-14 09:30', 29, 'Positive'),

        ('Placement & Career Drives', 'NVIDIA Drive Prep', 5,
         'CUDA & Kernel Profiling preparation material was top-notch',
         'Really appreciated the high-performance computing cheat sheets provided before the NVIDIA OA. Covered memory coalescence and shared memory caching thoroughly.',
         'Kavya Patel', 0, '2026-10-16 14:15', 31, 'Positive'),

        ('Course Curriculum', 'CS-305 Cloud DevOps', 4,
         'Great Kubernetes curriculum, suggest adding more Helm labs',
         'The Docker and Kubernetes ingress labs are super well designed. It would be awesome if we could have 1 more dedicated session on ArgoCD GitOps pipelines before the final exam.',
         'David Kim', 0, '2026-10-12 18:05', 18, 'Constructive'),

        ('LMS Platform', 'Student LLM Platform', 5,
         'Theme customization & AI Academic Copilot is breathtaking',
         'The new dark themes and instant AI code/math explanations make studying at night an absolute joy. Real-time attendance tracking and drive registration in one place is unmatched.',
         'Elena Rostova', 0, '2026-10-20 20:10', 54, 'Positive'),

        ('Campus Facilities', 'Innovation Studio 3 & Lab Desktops', 4,
         'High-end RTX 4090 workstations available for capstone',
         'Access to local GPU nodes enabled us to train our ResNet and Transformer models without running up huge AWS cloud bills. Lab air conditioning can sometimes be chilly.',
         'Rahul Verma', 0, '2026-10-10 15:45', 16, 'Positive'),

        ('Placement & Career Drives', 'General Placement Cell', 4,
         'Resume screening feedback turnaround was under 24 hours',
         'The career advisors helped align my GitHub repo links and highlighted relevant distributed systems coursework for the upcoming Amazon and Goldman Sachs drives.',
         'Anonymous Student', 1, '2026-10-15 13:00', 22, 'Positive')
    ]

    cursor.executemany('''
        INSERT INTO feedback_submissions (
            category, target_name, rating, review_title, review_text, author_name,
            is_anonymous, created_at, upvotes, sentiment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', feedbacks)
    conn.commit()

# Helper queries
def get_student_profile():
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM student_profile LIMIT 1').fetchone()
    conn.close()
    return profile

def update_student_profile(name, email, major, bio, target_study_hours, phone, gpa=None):
    conn = get_db_connection()
    if gpa is not None:
        conn.execute('''
            UPDATE student_profile
            SET name = ?, email = ?, major = ?, bio = ?, target_study_hours = ?, phone = ?, gpa = ?
            WHERE id = 1
        ''', (name, email, major, bio, target_study_hours, phone, gpa))
    else:
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

# ==============================================================================
# Companies & Placement Drives Management
# ==============================================================================

def get_companies_drives(status=None, search=None, role=None):
    conn = get_db_connection()
    query = '''
        SELECT d.*, 
               (SELECT a.status FROM student_drive_applications a 
                WHERE a.drive_id = d.id AND a.student_id = 1 LIMIT 1) AS app_status,
               (SELECT a.applied_at FROM student_drive_applications a 
                WHERE a.drive_id = d.id AND a.student_id = 1 LIMIT 1) AS applied_at
        FROM companies_drives d
        WHERE 1=1
    '''
    params = []
    if status and status != 'All':
        if status in ['Applied', 'Shortlisted']:
            query += ' AND d.id IN (SELECT drive_id FROM student_drive_applications WHERE student_id = 1 AND status = ?)'
            params.append(status)
        else:
            query += ' AND d.status = ?'
            params.append(status)
    if role and role != 'All':
        query += ' AND d.role_title LIKE ?'
        params.append(f'%{role}%')
    if search:
        query += ' AND (d.company_name LIKE ? OR d.role_title LIKE ? OR d.tags LIKE ? OR d.location LIKE ?)'
        sp = f'%{search}%'
        params.extend([sp, sp, sp, sp])

    query += ' ORDER BY d.drive_date ASC'
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows

def get_drive_by_id(drive_id):
    conn = get_db_connection()
    drive = conn.execute('''
        SELECT d.*, 
               (SELECT a.status FROM student_drive_applications a 
                WHERE a.drive_id = d.id AND a.student_id = 1 LIMIT 1) AS app_status,
               (SELECT a.applied_at FROM student_drive_applications a 
                WHERE a.drive_id = d.id AND a.student_id = 1 LIMIT 1) AS applied_at,
               (SELECT a.resume_link FROM student_drive_applications a 
                WHERE a.drive_id = d.id AND a.student_id = 1 LIMIT 1) AS app_resume
        FROM companies_drives d
        WHERE d.id = ?
    ''', (drive_id,)).fetchone()
    conn.close()
    return drive

def apply_to_drive(drive_id, student_id=1, resume_link=None, cover_note=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    applied_at = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Check if application already exists
    existing = cursor.execute('SELECT id FROM student_drive_applications WHERE drive_id = ? AND student_id = ?', (drive_id, student_id)).fetchone()
    if existing:
        cursor.execute('''
            UPDATE student_drive_applications
            SET applied_at = ?, resume_link = COALESCE(?, resume_link), cover_note = COALESCE(?, cover_note)
            WHERE id = ?
        ''', (applied_at, resume_link, cover_note, existing['id']))
    else:
        cursor.execute('''
            INSERT INTO student_drive_applications (drive_id, student_id, applied_at, status, resume_link, cover_note)
            VALUES (?, ?, ?, 'Applied', ?, ?)
        ''', (drive_id, student_id, applied_at, resume_link, cover_note))

    # Also log activity
    drive = cursor.execute('SELECT company_name, role_title FROM companies_drives WHERE id = ?', (drive_id,)).fetchone()
    if drive:
        cursor.execute('''
            INSERT INTO activities (activity_type, title, description, timestamp, icon_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('drive_applied', f"Applied to {drive['company_name']}",
              f"Submitted candidacy for {drive['role_title']} campus hiring drive.",
              applied_at, 'briefcase'))

    conn.commit()
    conn.close()
    return True

def get_placement_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    total_drives = cursor.execute('SELECT COUNT(*) FROM companies_drives').fetchone()[0]
    active_drives = cursor.execute("SELECT COUNT(*) FROM companies_drives WHERE status IN ('Open', 'Shortlisted')").fetchone()[0]
    applied_count = cursor.execute('SELECT COUNT(*) FROM student_drive_applications WHERE student_id = 1').fetchone()[0]
    shortlisted_count = cursor.execute("SELECT COUNT(*) FROM student_drive_applications WHERE student_id = 1 AND status = 'Shortlisted'").fetchone()[0]
    conn.close()

    return {
        'total_drives': total_drives,
        'active_drives': active_drives,
        'applied_count': applied_count,
        'shortlisted_count': shortlisted_count,
        'highest_package': '$185,000 / 52 LPA',
        'avg_package': '$161,000 / 44.5 LPA',
        'placement_rate': '96.4%'
    }

# ==============================================================================
# Attendance Management
# ==============================================================================

def get_attendance_overview():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_classes = cursor.execute('SELECT COUNT(*) FROM attendance_records').fetchone()[0]
    attended_classes = cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE status IN ('Present', 'Late')").fetchone()[0]
    absent_classes = cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE status = 'Absent'").fetchone()[0]

    overall_pct = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 0.0

    # Safe bunk calculator (buffer before dropping below 75%)
    # Let x be absences we can take: (attended) / (total + x) >= 0.75
    # attended >= 0.75 * total + 0.75 * x => x <= (attended - 0.75 * total) / 0.75
    safe_bunks = max(0, int((attended_classes - 0.75 * total_classes) / 0.75)) if total_classes > 0 else 0

    conn.close()
    return {
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'absent_classes': absent_classes,
        'overall_pct': overall_pct,
        'safe_bunks': safe_bunks,
        'status_standing': 'Safe & Eligible' if overall_pct >= 75.0 else 'Attendance Warning (<75%)'
    }

def get_course_attendance_details(course_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    courses_query = 'SELECT * FROM courses'
    params = []
    if course_id:
        courses_query += ' WHERE id = ?'
        params.append(course_id)
    courses_query += ' ORDER BY id ASC'

    courses = cursor.execute(courses_query, params).fetchall()
    details = []

    for c in courses:
        cid = c['id']
        total = cursor.execute('SELECT COUNT(*) FROM attendance_records WHERE course_id = ?', (cid,)).fetchone()[0]
        attended = cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE course_id = ? AND status IN ('Present', 'Late')", (cid,)).fetchone()[0]
        absent = cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE course_id = ? AND status = 'Absent'", (cid,)).fetchone()[0]
        late = cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE course_id = ? AND status = 'Late'", (cid,)).fetchone()[0]

        pct = round((attended / total * 100), 1) if total > 0 else 100.0

        # Safe bunks or need-to-attend count
        if pct >= 75.0:
            can_miss = max(0, int((attended - 0.75 * total) / 0.75))
            advice = f"Safe: Can miss {can_miss} more session{'s' if can_miss != 1 else ''}"
            advice_type = 'safe'
        else:
            # Need to attend y consecutive classes: (attended + y) / (total + y) >= 0.75 => y >= 3*total - 4*attended
            need_attend = max(1, 3 * total - 4 * attended)
            advice = f"Warning: Must attend next {need_attend} classes"
            advice_type = 'warning'

        details.append({
            'course_id': cid,
            'course_code': c['code'],
            'course_title': c['title'],
            'instructor': c['instructor'],
            'color_accent': c['color_accent'] or '#4f46e5',
            'schedule': c['schedule'],
            'location': c['location'],
            'total_classes': total,
            'attended_classes': attended,
            'absent_classes': absent,
            'late_classes': late,
            'percentage': pct,
            'advice': advice,
            'advice_type': advice_type
        })

    conn.close()
    return details

def get_recent_attendance_logs(course_id=None, status=None, limit=40):
    conn = get_db_connection()
    query = '''
        SELECT a.*, c.title AS course_title, c.code AS course_code, c.color_accent
        FROM attendance_records a
        JOIN courses c ON a.course_id = c.id
        WHERE 1=1
    '''
    params = []
    if course_id and course_id != 'All':
        query += ' AND a.course_id = ?'
        params.append(course_id)
    if status and status != 'All':
        query += ' AND a.status = ?'
        params.append(status)

    query += ' ORDER BY a.session_date DESC, a.id DESC LIMIT ?'
    params.append(limit)

    logs = conn.execute(query, params).fetchall()
    conn.close()
    return logs

def mark_attendance(course_id, status='Present', session_topic=None, remarks=None, session_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    date_str = session_date or datetime.now().strftime('%Y-%m-%d')
    topic = session_topic or 'Live Class Lecture Session'
    rem = remarks or ('Marked via portal' if status == 'Present' else 'Reported absence')

    cursor.execute('''
        INSERT INTO attendance_records (course_id, session_date, session_topic, status, remarks)
        VALUES (?, ?, ?, ?, ?)
    ''', (course_id, date_str, topic, status, rem))

    course = cursor.execute('SELECT code, title FROM courses WHERE id = ?', (course_id,)).fetchone()
    if course:
        cursor.execute('''
            INSERT INTO activities (activity_type, title, description, timestamp, icon_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('attendance_marked', f"Attendance Logged: {course['code']}",
              f"Marked as '{status}' for {course['title']} ({topic}).",
              datetime.now().strftime('%Y-%m-%d %H:%M'), 'check-square'))

    conn.commit()
    conn.close()
    return True

# ==============================================================================
# Feedback & Reviews Management
# ==============================================================================

def get_feedbacks(category=None, min_rating=None, search=None):
    conn = get_db_connection()
    query = 'SELECT * FROM feedback_submissions WHERE 1=1'
    params = []

    if category and category != 'All':
        query += ' AND category = ?'
        params.append(category)
    if min_rating and min_rating != 'All':
        query += ' AND rating >= ?'
        params.append(int(min_rating))
    if search:
        query += ' AND (target_name LIKE ? OR review_title LIKE ? OR review_text LIKE ? OR author_name LIKE ?)'
        sp = f'%{search}%'
        params.extend([sp, sp, sp, sp])

    query += ' ORDER BY id DESC'
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows

def get_feedback_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    total_count = cursor.execute('SELECT COUNT(*) FROM feedback_submissions').fetchone()[0]
    avg_rating = cursor.execute('SELECT AVG(rating) FROM feedback_submissions').fetchone()[0] or 5.0
    positive_count = cursor.execute("SELECT COUNT(*) FROM feedback_submissions WHERE sentiment = 'Positive'").fetchone()[0]

    pct_positive = round((positive_count / total_count * 100), 1) if total_count > 0 else 100.0

    conn.close()
    return {
        'total_count': total_count,
        'avg_rating': round(avg_rating, 1),
        'positive_count': positive_count,
        'pct_positive': pct_positive,
        'curriculum_sat': '97%',
        'placements_sat': '95%',
        'faculty_sat': '98%'
    }

def submit_feedback(category, target_name, rating, review_title, review_text, author_name='Ajay Reddy', is_anonymous=0, sentiment='Positive'):
    conn = get_db_connection()
    cursor = conn.cursor()

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M')
    name_to_record = 'Anonymous Student' if is_anonymous else (author_name or 'Ajay Reddy')

    cursor.execute('''
        INSERT INTO feedback_submissions (
            category, target_name, rating, review_title, review_text, author_name,
            is_anonymous, created_at, upvotes, sentiment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    ''', (category, target_name, int(rating), review_title, review_text, name_to_record, int(is_anonymous), created_at, sentiment))

    cursor.execute('''
        INSERT INTO activities (activity_type, title, description, timestamp, icon_name)
        VALUES (?, ?, ?, ?, ?)
    ''', ('feedback_submitted', 'Review Submitted',
          f"Feedback posted for {target_name} ({rating}/5 Stars).",
          created_at, 'star'))

    conn.commit()
    conn.close()
    return True

def upvote_feedback(feedback_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE feedback_submissions SET upvotes = upvotes + 1 WHERE id = ?', (feedback_id,))
    new_votes = cursor.execute('SELECT upvotes FROM feedback_submissions WHERE id = ?', (feedback_id,)).fetchone()
    conn.commit()
    conn.close()
    return new_votes['upvotes'] if new_votes else 0

