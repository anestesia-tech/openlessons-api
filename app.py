import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()
app = Flask(__name__)

url = os.environ.get("DB_URL")
connection = psycopg2.connect(url)

# Create tables if not exists
CREATE_LESSONS_TABLE = ("CREATE TABLE IF NOT EXISTS lessons(id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL);")

CREATE_THEMES_TABLE = ("CREATE TABLE IF NOT EXISTS themes(lesson_id INT, theme VARCHAR(255), FOREIGN KEY(lesson_id) REFERENCES lessons(id) ON DELETE CASCADE);")

# Add lesson
INSERT_LESSON = ("INSERT INTO lessons (name) VALUES (%s) RETURNING id;")
INSERT_THEME = ("INSERT INTO themes (lesson_id, theme) VALUES (%s, %s);")

# Select lesson with theme
LESSON_NAME = ("SELECT name FROM lessons WHERE id = (%s);")
LESSON_THEME = ("SELECT theme FROM themes WHERE lesson_id = (%s);")


@app.post("/api/lesson")
def create_lesson():
    data = request.get_json()
    name = data["name"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_LESSONS_TABLE)
            cursor.execute(INSERT_LESSON, (name,))
            lesson_id = cursor.fetchone()[0]
    return {"id": lesson_id, "message": f"Lesson {name} created"}, 200


@app.post("/api/theme")
def create_theme():
    data = request.get_json()
    theme = data["theme"]
    lesson_id = data["lesson_id"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_THEMES_TABLE)
            cursor.execute(INSERT_THEME, (lesson_id, theme))
    return {"message": f"Theme {theme} for lesson {lesson_id} added"}, 200


@app.get("/api/lesson/<int:lesson_id>")
def get_lesson(lesson_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(LESSON_NAME, (lesson_id,))
            name = cursor.fetchone()[0]
            cursor.execute(LESSON_THEME, (lesson_id,))
            theme = cursor.fetchone()[0]
    return {"Lesson name": name, "Lesson theme": theme}, 200



