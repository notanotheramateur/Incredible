from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
courses = [
    {'id': 1, 'title': 'Introduction to Python'},
    {'id': 2, 'title': 'Web Development Basics'},
]
users = [
    {'id': 1, 'name': 'Alice'},
    {'id': 2, 'name': 'Bob'},
]
@app.route('/')
def home():
    return render_template('index.html', courses=courses, users=users)

@app.route('/course/<int:course_id>')
def course(course_id):
    course = next((c for c in courses if c['id'] == course_id), None)
    if not course:
        return "Course not found", 404

    user_id = request.args.get('user_id', type=int)
    user = next((u for u in users if u['id'] == user_id), None)

    return render_template('course.html', course=course, user=user)

if __name__ == '__main__':
    app.run(debug=True)
