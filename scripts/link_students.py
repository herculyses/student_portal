from app import app, db, User, Student

with app.app_context():
    students = Student.query.all()

    linked = 0
    skipped = 0
    missing = 0

    for s in students:
        if s.user_id:
            skipped += 1
            continue

        user = User.query.filter_by(username=s.student_id.strip()).first()

        if not user:
            print(f"NO USER FOUND for {s.student_id}")
            missing += 1
            continue

        s.user_id = user.id
        linked += 1
        print(f"Linked {s.student_id} -> User ID {user.id}")

    db.session.commit()

    print("\nDONE")
    print(f"Linked: {linked}")
    print(f"Skipped: {skipped}")
    print(f"Missing: {missing}")