from app.repositories.student_repository import StudentRepository


class StudentService:
    """Service engine for student registration and record management."""

    @staticmethod
    def get_students(limit=100, offset=0):
        """Retrieves list of student records."""
        return StudentRepository.get_all(limit=limit, offset=offset)

    @staticmethod
    def get_student_by_id(student_id):
        """Retrieves single student record or raises ValueError if not found."""
        student = StudentRepository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student ID {student_id} not found.")
        return student

    @staticmethod
    def register_student(data):
        """
        Validates input and registers a new resident student.
        Raises ValueError on validation failure or duplicate entry.
        """
        required_fields = ['registration_number', 'first_name', 'last_name', 'dob', 'gender', 'email', 'phone', 'department_id', 'course_id', 'academic_year_id']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: '{field}'")

        # Duplicate registration number check
        existing_reg = StudentRepository.get_by_registration_number(data['registration_number'])
        if existing_reg:
            raise ValueError(f"Registration number '{data['registration_number']}' already exists.")

        # Duplicate email check
        existing_email = StudentRepository.get_by_email(data['email'])
        if existing_email:
            raise ValueError(f"Email address '{data['email']}' already registered.")

        # Persist student record
        student_id = StudentRepository.create(data)
        return StudentRepository.get_by_id(student_id)
