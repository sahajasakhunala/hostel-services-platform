from app.db.connection import get_db_cursor


class StudentRepository:
    """Data Access Object (DAO) for Student entity operations."""

    @staticmethod
    def get_all(limit=100, offset=0):
        """Retrieves paginated list of students with academic details."""
        query = """
            SELECT 
                s.student_id,
                s.registration_number,
                s.first_name,
                s.last_name,
                CONCAT(s.first_name, ' ', s.last_name) AS full_name,
                s.dob,
                s.gender,
                s.email,
                s.phone,
                d.code AS department_code,
                c.name AS course_name,
                ay.year_label AS academic_year,
                s.status,
                s.created_at
            FROM students s
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON s.course_id = c.course_id
            JOIN academic_years ay ON s.academic_year_id = ay.academic_year_id
            ORDER BY s.student_id DESC
            LIMIT %s OFFSET %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()

    @staticmethod
    def get_by_id(student_id):
        """Retrieves a single student by primary key ID."""
        query = """
            SELECT 
                s.student_id,
                s.registration_number,
                s.first_name,
                s.last_name,
                s.dob,
                s.gender,
                s.email,
                s.phone,
                s.department_id,
                s.course_id,
                s.academic_year_id,
                s.status,
                s.created_at
            FROM students s
            WHERE s.student_id = %s
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (student_id,))
            return cursor.fetchone()

    @staticmethod
    def get_by_registration_number(registration_number):
        """Finds student by registration number."""
        query = "SELECT * FROM students WHERE registration_number = %s"
        with get_db_cursor() as cursor:
            cursor.execute(query, (registration_number,))
            return cursor.fetchone()

    @staticmethod
    def get_by_email(email):
        """Finds student by email address."""
        query = "SELECT * FROM students WHERE email = %s"
        with get_db_cursor() as cursor:
            cursor.execute(query, (email,))
            return cursor.fetchone()

    @staticmethod
    def create(data):
        """Inserts a new student record into the database."""
        query = """
            INSERT INTO students (
                registration_number, first_name, last_name, dob, gender, email, phone, department_id, course_id, academic_year_id, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['registration_number'],
            data['first_name'],
            data['last_name'],
            data['dob'],
            data['gender'],
            data['email'],
            data['phone'],
            data['department_id'],
            data['course_id'],
            data['academic_year_id'],
            data.get('status', 'active')
        )
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
