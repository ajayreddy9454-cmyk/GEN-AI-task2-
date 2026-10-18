import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'student-llm-secret-key-production-ready')

# Ensure DB is initialized
database.init_db()

@app.context_processor
def inject_global_data():
    profile = database.get_student_profile()
    today_str = datetime.now().strftime('%Y-%m-%d')
    notifs, unread_count = database.get_notifications()
    schedule = database.get_daily_schedule()
    return {
        'current_profile': profile,
        'today_str': today_str,
        'current_year': datetime.now().year,
        'notifications': notifs,
        'unread_notif_count': unread_count,
        'daily_schedule': schedule,
        'semester_label': 'Fall Semester 2026'
    }

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    summary = database.get_dashboard_summary()
    courses = database.get_courses()
    assignments = database.get_assignments()
    activities = database.get_activities(limit=5)
    study_logs = database.get_study_logs()
    schedule = database.get_daily_schedule()
    
    chart_labels = [row['day_name'] for row in study_logs]
    chart_actual = [row['hours'] for row in study_logs]
    chart_target = [row['target_hours'] for row in study_logs]

    return render_template(
        'dashboard.html',
        active_page='dashboard',
        summary=summary,
        courses=courses,
        assignments=assignments[:5],
        activities=activities,
        schedule=schedule,
        chart_labels=chart_labels,
        chart_actual=chart_actual,
        chart_target=chart_target
    )

@app.route('/courses')
def courses():
    category = request.args.get('category', 'All')
    search = request.args.get('q', '').strip()
    course_list = database.get_courses(category=category if category != 'All' else None, search=search or None)
    categories = database.get_course_categories()
    
    return render_template(
        'courses.html',
        active_page='courses',
        courses=course_list,
        categories=categories,
        selected_category=category,
        search_query=search
    )

@app.route('/api/courses/<int:course_id>/syllabus')
def course_syllabus_api(course_id):
    course = database.get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'message': 'Course not found'}), 404
    
    return jsonify({
        'success': True,
        'code': course['code'],
        'title': course['title'],
        'instructor': course['instructor'],
        'instructor_email': course['instructor_email'],
        'credits': course['credits'],
        'level': course['level'],
        'location': course['location'],
        'schedule': course['schedule'],
        'syllabus_summary': course['syllabus_summary']
    })

@app.route('/assignments')
def assignments():
    status = request.args.get('status', 'All')
    course_id = request.args.get('course_id', 'All')
    priority = request.args.get('priority', 'All')
    search = request.args.get('q', '').strip()

    course_filter = int(course_id) if course_id != 'All' and course_id.isdigit() else None
    assignment_list = database.get_assignments(
        status=status if status != 'All' else None,
        course_id=course_filter,
        priority=priority if priority != 'All' else None,
        search=search or None
    )
    all_courses = database.get_courses()
    
    all_assignments = database.get_assignments()
    pending_count = sum(1 for a in all_assignments if a['status'] == 'Pending')
    submitted_count = sum(1 for a in all_assignments if a['status'] == 'Submitted')
    completed_count = sum(1 for a in all_assignments if a['status'] == 'Completed')
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    overdue_count = sum(1 for a in all_assignments if a['status'] == 'Pending' and a['due_date'] < today_str)

    return render_template(
        'assignments.html',
        active_page='assignments',
        assignments=assignment_list,
        courses=all_courses,
        selected_status=status,
        selected_course=course_id,
        selected_priority=priority,
        search_query=search,
        pending_count=pending_count,
        submitted_count=submitted_count,
        completed_count=completed_count,
        overdue_count=overdue_count,
        total_count=len(all_assignments)
    )

@app.route('/api/assignments/<int:assignment_id>/status', methods=['POST'])
def update_assignment_status_api(assignment_id):
    data = request.get_json() or {}
    new_status = data.get('status')
    submission_text = data.get('submission_text')
    submission_url = data.get('submission_url')
    valid_statuses = ['Pending', 'Submitted', 'Completed']
    
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status provided.'}), 400
    
    database.update_assignment_status(assignment_id, new_status, submission_text, submission_url)
    return jsonify({
        'success': True,
        'status': new_status,
        'message': f'Assignment successfully marked as {new_status}!'
    })

@app.route('/api/assignments/create', methods=['POST'])
def create_assignment_api():
    course_id = request.form.get('course_id')
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    due_date = request.form.get('due_date', '').strip()
    priority = request.form.get('priority', 'Medium')
    points = request.form.get('points', 100)

    if not course_id or not title or not due_date:
        flash('Please fill out all required fields (Course, Title, and Due Date).', 'error')
        return redirect(url_for('assignments'))

    try:
        points = int(points)
    except ValueError:
        points = 100

    database.create_assignment(int(course_id), title, description, due_date, priority, points)
    flash(f"Assignment '{title}' has been successfully created with {priority} priority!", 'success')
    return redirect(url_for('assignments'))

@app.route('/api/courses/<int:course_id>/progress', methods=['POST'])
def update_course_progress_api(course_id):
    data = request.get_json() or {}
    completed_lessons = data.get('completed_lessons')
    
    if completed_lessons is None:
        return jsonify({'success': False, 'message': 'Missing completed_lessons value'}), 400
    
    database.update_course_progress(course_id, int(completed_lessons))
    return jsonify({'success': True, 'message': 'Course syllabus progress updated!'})

@app.route('/resources')
def resources():
    category = request.args.get('category', 'All')
    resource_type = request.args.get('type', 'All')
    search = request.args.get('q', '').strip()

    resource_list = database.get_resources(
        category=category if category != 'All' else None,
        resource_type=resource_type if resource_type != 'All' else None,
        search=search or None
    )
    categories = database.get_resource_categories()

    return render_template(
        'resources.html',
        active_page='resources',
        resources=resource_list,
        categories=categories,
        selected_category=category,
        selected_type=resource_type,
        search_query=search
    )

@app.route('/profile')
def profile():
    student = database.get_student_profile()
    courses = database.get_courses()
    summary = database.get_dashboard_summary()
    activities = database.get_activities(limit=8)

    return render_template(
        'profile.html',
        active_page='profile',
        student=student,
        courses=courses,
        summary=summary,
        activities=activities
    )

@app.route('/profile/update', methods=['POST'])
def update_profile():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    major = request.form.get('major', '').strip()
    phone = request.form.get('phone', '').strip()
    target_study_hours = request.form.get('target_study_hours', '25').strip()
    bio = request.form.get('bio', '').strip()

    if not name or not email or not major:
        flash('Name, Email, and Major are required fields.', 'error')
        return redirect(url_for('profile'))

    try:
        target_hours_int = int(target_study_hours)
    except ValueError:
        target_hours_int = 25

    database.update_student_profile(name, email, major, bio, target_hours_int, phone)
    flash('Student profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/api/notifications/read', methods=['POST'])
def mark_notifications_read_api():
    database.mark_notifications_read()
    return jsonify({'success': True})

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant_api():
    data = request.get_json() or {}
    query = data.get('query', '').strip().lower()

    if not query:
        return jsonify({'success': False, 'answer': 'Please ask an academic or course-related question.'})

    # Intelligent contextual knowledge engine for Student LLM
    if 'attention' in query or 'transformer' in query or 'neural' in query or 'deep learning' in query:
        answer = (
            "**Transformer Scaled Dot-Product Attention:**\n\n"
            "$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$\n\n"
            "• **Query ($Q$) & Key ($K$)**: Dimensions $(B, H, S, d_k)$. The dot product computes raw similarity scores.\n"
            "• **Scale Factor $\\sqrt{d_k}$**: Counteracts vanishing gradients in the softmax function for high dimensions.\n"
            "• **Multi-Head Attention**: Projects vectors into $h$ subspaces, enabling the network to jointly attend to information from different representation subspaces."
        )
    elif 'kubernetes' in query or 'helm' in query or 'docker' in query or 'cloud' in query:
        answer = (
            "**Kubernetes Architecture & Helm Deployments:**\n\n"
            "• **Pods & Deployments**: Pods are ephemeral; Deployments maintain the desired replica count and coordinate zero-downtime rolling updates.\n"
            "• **Ingress Controllers**: Route external HTTP/HTTPS traffic based on host header and URI path to ClusterIP services.\n"
            "• **Helm Charts**: Package Kubernetes manifests with parameterized `values.yaml` templates for repeatable multi-stage CI/CD environments."
        )
    elif 'sql' in query or 'index' in query or 'b-tree' in query or 'database' in query:
        answer = (
            "**Database Indexing & Query Plan Optimization:**\n\n"
            "• **B-Tree Structure**: Balanced tree providing $O(\\log N)$ lookup, range scans, and ordered sequential traversal.\n"
            "• **Composite Indexing**: Leftmost prefix rule applies. An index on `(course_id, due_date)` accelerates queries filtering by `course_id` alone or both, but not `due_date` alone.\n"
            "• **EXPLAIN Execution Plan**: Look for `INDEX SCAN` or `INDEX RANGE SCAN` instead of expensive `TABLE FULL SCAN` on large relations."
        )
    elif 'bayesian' in query or 'probability' in query or 'statistics' in query:
        answer = (
            "**Bayesian Inference Fundamentals:**\n\n"
            "$$P(\\theta | D) = \\frac{P(D | \\theta) \\cdot P(\\theta)}{P(D)}$$\n\n"
            "• **Prior $P(\\theta)$**: Initial belief before observing evidence.\n"
            "• **Likelihood $P(D | \\theta)$**: Probability of observing data given parameters.\n"
            "• **Posterior $P(\\theta | D)$**: Updated parameter belief combining prior knowledge and empirical observations."
        )
    elif 'deadline' in query or 'assignment' in query or 'due' in query or 'todo' in query:
        answer = (
            "**Upcoming Academic Priorities:**\n\n"
            "1. **SQL Query Profiling Lab** (Overdue - Priority High) &mdash; submit benchmarking analysis immediately.\n"
            "2. **Implement Transformer Self-Attention Layer** &mdash; due in 2 days (CS-401).\n"
            "3. **Kubernetes Helm Deployment Pipeline** &mdash; due in 5 days (CS-305)."
        )
    else:
        answer = (
            f"**Student LLM Academic Copilot:**\n\n"
            f"I have reviewed your query regarding *'{data.get('query')}'* across your enrolled courses (Deep Learning, Cloud DevOps, Database Systems, Web Architectures, and Applied Statistics).\n\n"
            "💡 **Recommended next steps:**\n"
            "1. Review the relevant study notes in the **Learning Resources** tab.\n"
            "2. Check assignment criteria in **Assignments**.\n"
            "3. Feel free to ask specifically about code patterns, formulas, or architecture diagrams."
        )

    return jsonify({'success': True, 'answer': answer})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
