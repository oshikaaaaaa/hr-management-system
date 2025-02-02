import enum
# Enums
class Gender(str, enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class EmploymentStatus(str, enum.Enum):
    Active = "Active"
    Resigned = "Resigned"
    Terminated = "Terminated"
    On_Leave = "On_Leave"
    Absent = "Absent"

class PositionType(str, enum.Enum):
    Full = "Full"
    Part = "Part"

class LeaveStatus(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


class ApplicationStatus(str, enum.Enum):
    PENDING = "Pending"
    SHORTLISTED = "Shortlisted"
    INTERVIEWED = "Interviewed"
    HIRED = "Hired"
    REJECTED = "Rejected"


class InterviewStatus(str, enum.Enum):
    PENDING = "Pending"
    COMPLETED= "Completed"
    RESCHEDULED = "Rescheduled"
    CANCELLED= "Cancelled"
    