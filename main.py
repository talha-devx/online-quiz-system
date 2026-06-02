from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Collections
students_collection = db["students"]
teachers_collection = db["teachers"]
quizzes_collection = db["quizzes"]
questions_collection = db["questions"]
results_collection = db["results"]


@app.get("/")
def home():
    return {
        "message": "Quiz System API Running"
    }


@app.get("/test-db")
def test_db():
    collections = db.list_collection_names()
    return {
        "collections": collections
    }


# =========================
# STUDENT REGISTER
# =========================

@app.post("/register")
def register(user: dict):

    existing_student = students_collection.find_one({
        "email": user["email"]
    })

    if existing_student:
        return {
            "message": "Email already registered"
        }

    students_collection.insert_one(user)

    return {
        "message": "Student registered successfully"
    }


# =========================
# STUDENT LOGIN
# =========================

@app.post("/student-login")
def student_login(user: dict):

    student = students_collection.find_one({
        "email": user["email"],
        "password": user["password"]
    })

    if student:
        return {
            "message": "Login successful",
            "name": student["name"],
            "email": student["email"]
        }

    return {
        "message": "Invalid email or password"
    }


# =========================
# TEACHER LOGIN
# =========================

@app.post("/teacher-login")
def teacher_login(user: dict):

    teacher = teachers_collection.find_one({
        "email": user["email"],
        "password": user["password"]
    })

    if teacher:
        return {
            "message": "Login successful",
            "name": teacher["name"]
        }

    return {
        "message": "Invalid email or password"
    }


# =========================
# CREATE QUIZ
# =========================

@app.post("/create-quiz")
def create_quiz(quiz: dict):

    quizzes_collection.insert_one(quiz)

    return {
        "message": "Quiz created successfully"
    }


# =========================
# GET ALL QUIZZES
# =========================

@app.get("/quizzes")
def get_quizzes():

    quizzes = list(
        quizzes_collection.find({}, {"_id": 0})
    )

    return quizzes


# =========================
# ADD QUESTION
# =========================

@app.post("/add-question")
def add_question(question: dict):

    questions_collection.insert_one(question)

    return {
        "message": "Question added successfully"
    }


# =========================
# GET QUESTIONS BY QUIZ
# =========================

@app.get("/quiz-questions/{quiz_title}")
def get_questions(quiz_title: str):

    questions = list(
        questions_collection.find(
            {
                "quiz_title": quiz_title
            },
            {
                "_id": 0
            }
        )
    )

    return questions

# =========================
# SUBMIT QUIZ
# =========================

@app.post("/submit-quiz")
def submit_quiz(data: dict):

    question = questions_collection.find_one({
        "question": data["question"]
    })

    score = 0

    if question and data["answer"] == question["correct_answer"]:
        score = 1

    result = {
        "student": data["student"],
        "question": data["question"],
        "answer": data["answer"],
        "score": score
    }

    results_collection.insert_one(result)

    return {
        "message": "Quiz submitted",
        "score": score
    }


# =========================
# RESULTS
# =========================

@app.get("/results")
def get_results():

    results = list(
        results_collection.find({}, {"_id": 0})
    )

    return results

@app.delete("/delete-quiz/{title}")
def delete_quiz(title: str):

    db.quizzes.delete_one({
        "title": title
    })

    return {
        "message": "Quiz deleted successfully"
    }

@app.post("/save-result")
def save_result(data: dict):

    results_collection.insert_one(data)

    return {
        "message": "Result saved successfully"
    }

@app.get("/my-results/{email}")
def my_results(email: str):

    results = list(
        results_collection.find(
            {"email": email},
            {"_id": 0}
        )
    )

    return results

@app.get("/check-attempt/{email}/{quiz}")
def check_attempt(email: str, quiz: str):

    result = results_collection.find_one({
        "email": email,
        "quiz": quiz
    })

    if result:
        return {
            "attempted": True
        }

    return {
        "attempted": False
    }

@app.get("/analytics")
def analytics():

    total_students = students_collection.count_documents({})
    total_quizzes = quizzes_collection.count_documents({})
    total_attempts = results_collection.count_documents({})

    top_student = None

    top_result = results_collection.find_one(
        sort=[("score", -1)]
    )

    if top_result:
        percentage = round(
            (top_result["score"] / top_result["total"]) * 100
        )

        top_student = {
            "name": top_result["student"],
            "percentage": percentage
        }

    quiz_stats = []

    quizzes = list(
        quizzes_collection.find({}, {"_id": 0})
    )

    for quiz in quizzes:

        attempts = list(
            results_collection.find(
                {"quiz": quiz["title"]}
            )
        )

        attempt_count = len(attempts)

        average_score = 0

        if attempt_count > 0:

            total_scores = sum(
                r["score"] for r in attempts
            )

            average_score = round(
                total_scores / attempt_count,
                2
            )

        quiz_stats.append({
            "quiz": quiz["title"],
            "attempts": attempt_count,
            "average_score": average_score
        })

    return {
        "students": total_students,
        "quizzes": total_quizzes,
        "attempts": total_attempts,
        "top_student": top_student,
        "quiz_stats": quiz_stats
    }

@app.post("/create-full-quiz")
def create_full_quiz(data: dict):

    quiz = {
        "title": data["title"],
        "description": data["description"],
        "total_marks": data["total_marks"]
    }

    quizzes_collection.insert_one(quiz)

    for question in data["questions"]:

        question["quiz_title"] = data["title"]

        questions_collection.insert_one(
            question
        )

    return {
        "message": "Quiz and Questions saved successfully"
    }