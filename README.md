Group members:
CS23B019
CS23B034
CS23B098
CS23B083
CS22B010



### Requirements

- Python 3.6+
- mysql-connector-python
- MySQL Server with `academic_insti` database as its name 


```

### Usage

Run the application:


python main.py -u yourusername -p yourpassword

```


```

### Application 

After connecting, there will be the main menu with three options:

```
MAIN MENU
─────────────────────────────────────
1. Add course (Even Semester 2006)
2. Enroll student (Even Semester 2006) 
3. Exit
─────────────────────────────────────
```

### Feature 1: Add Course

Input required:
- **Department ID** - Must exist in database
- **Course ID** - Must exist and belong to the specified department
- **Teacher (Emp) ID** - Must exist and belong to the specified department
- **Classroom** - Room number/identifier



### Feature 2: Enroll Student

Input required:
- **Student Roll No** - Must exist in database
- **Course IDs** - Comma-separated list of course IDs to enroll in (e.g., "101,105,123"),this course should be taught and student should have cleared all prerequisites

