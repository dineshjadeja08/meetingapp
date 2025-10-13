# Contributing to Meeting App

First off, thank you for considering contributing to Meeting App! It's people like you that make this project better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. We pledge to:

- Be respectful and inclusive
- Welcome newcomers warmly
- Be patient and understanding
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community

### Unacceptable Behavior

- Harassment, discrimination, or trolling
- Personal attacks or political arguments
- Publishing others' private information
- Any conduct that could reasonably be considered inappropriate

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:

- Python 3.11 or higher
- Git
- MySQL or PostgreSQL
- Basic understanding of Django and Django REST Framework
- Familiarity with JWT authentication

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/meetingapp.git
   cd meetingapp
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/dineshjadeja08/meetingapp.git
   ```

4. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

6. **Set up database**
   ```bash
   # Create database
   mysql -u root -p
   CREATE DATABASE meetingapp_dev;
   
   # Run migrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

---

## 🔄 Development Process

### 1. Choose What to Work On

- Check [Issues](https://github.com/dineshjadeja08/meetingapp/issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it
- If you have a new idea, open an issue first to discuss it

### 2. Create a Branch

Always create a new branch for your work:

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance tasks

### 3. Make Changes

- Write clean, readable code
- Follow the project's coding standards
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

### 4. Commit Your Changes

Write meaningful commit messages:

```bash
git add .
git commit -m "feat: Add real-time chat functionality

- Implement WebSocket connection
- Add chat message model
- Create chat API endpoints
- Add tests for chat functionality

Closes #123"
```

**Commit message format:**
```
<type>: <short summary>

<detailed description>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

---

## 🔍 Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**
   ```bash
   python manage.py test
   ```

3. **Check code quality**
   ```bash
   # Format code
   black .
   
   # Lint
   flake8 .
   
   # Sort imports
   isort .
   ```

4. **Update documentation**
   - Update README if needed
   - Add/update docstrings
   - Update API documentation

### Submitting Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

3. **PR Title Format**
   ```
   [Type] Short description
   
   Examples:
   [Feature] Add real-time chat
   [Fix] Resolve OAuth redirect issue
   [Docs] Update API documentation
   ```

4. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Related Issues
   Closes #123
   
   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

### Review Process

1. **Wait for review** - Maintainers will review your PR
2. **Address feedback** - Make requested changes
3. **Update PR** - Push additional commits if needed
4. **Approval** - Once approved, your PR will be merged

---

## 💻 Coding Standards

### Python Style Guide

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:

**Line Length:**
- Maximum 100 characters (not 79)
- Use implicit line continuation for long lines

**Imports:**
```python
# Standard library
import os
import sys

# Third-party
from django.db import models
from rest_framework import serializers

# Local
from accounts.models import UserProfile
```

**Naming Conventions:**
```python
# Variables and functions: snake_case
user_profile = get_user_profile()

# Classes: PascalCase
class UserProfileView(APIView):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_PARTICIPANTS = 100

# Private methods: _leading_underscore
def _internal_method(self):
    pass
```

**Docstrings:**
```python
def create_meeting_room(title, host, max_participants=100):
    """
    Create a new meeting room.
    
    Args:
        title (str): The title of the meeting room
        host (User): The user who will host the meeting
        max_participants (int): Maximum number of participants (default: 100)
    
    Returns:
        MeetingRoom: The created meeting room object
    
    Raises:
        ValueError: If title is empty or max_participants is invalid
    """
    pass
```

### Django Specific

**Models:**
```python
class MeetingRoom(models.Model):
    """Video meeting room model."""
    
    title = models.CharField(max_length=200)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Meeting Room'
    
    def __str__(self):
        return f"{self.title} ({self.room_code})"
```

**Views:**
```python
class MeetingRoomView(APIView):
    """API view for meeting room operations."""
    
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List meeting rooms",
        responses={200: MeetingRoomSerializer(many=True)}
    )
    def get(self, request):
        """Get list of meeting rooms."""
        pass
```

### Code Quality Tools

**Black (Code Formatter):**
```bash
black . --line-length 100
```

**Flake8 (Linter):**
```bash
flake8 . --max-line-length=100 --exclude=migrations,venv
```

**isort (Import Sorter):**
```bash
isort . --profile black
```

**Configuration (.flake8):**
```ini
[flake8]
max-line-length = 100
exclude = migrations,venv,__pycache__
ignore = E203,W503
```

---

## 🧪 Testing Guidelines

### Writing Tests

**Test Structure:**
```python
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile

class UserProfileTestCase(TestCase):
    """Tests for UserProfile model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created with User."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_full_name_property(self):
        """Test the full_name property."""
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        self.assertEqual(self.user.profile.full_name, 'John Doe')
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app
python manage.py test accounts

# Run specific test case
python manage.py test accounts.tests.UserProfileTestCase

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Coverage

- Aim for 80%+ code coverage
- All new features must include tests
- Bug fixes should include regression tests

---

## 📖 Documentation

### Code Documentation

- Add docstrings to all classes and functions
- Use clear, descriptive variable names
- Comment complex logic

### API Documentation

- Use Swagger decorators for all API endpoints
- Provide examples in docstrings
- Document all parameters and responses

### Project Documentation

Update relevant files when making changes:
- README.md - Project overview
- API_DOCUMENTATION.md - API reference
- SECURITY_RECOMMENDATIONS.md - Security info
- IMPROVEMENTS_ROADMAP.md - Future plans

---

## 👥 Community

### Getting Help

- **GitHub Issues:** Report bugs or ask questions
- **Discussions:** General questions and ideas
- **Email:** contact@meetingapp.local

### Communication

- Be respectful and professional
- Ask questions clearly
- Provide context and details
- Be patient - maintainers are volunteers

### Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Thanked in commit messages

---

## 🎯 Areas We Need Help

### High Priority
- Writing tests (unit, integration, e2e)
- WebRTC implementation
- Real-time chat functionality
- Performance optimization
- Security audits

### Medium Priority
- UI/UX improvements
- Mobile app development
- Documentation improvements
- Internationalization (i18n)
- Accessibility (a11y)

### Good First Issues
- Documentation updates
- Code formatting
- Adding tests
- Bug fixes
- Minor feature additions

---

## 📝 Additional Resources

### Learning Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [WebRTC Tutorials](https://webrtc.org/getting-started/overview)
- [Git Basics](https://git-scm.com/book/en/v2)

### Project Resources
- [API Documentation](API_DOCUMENTATION.md)
- [Security Guide](SECURITY_RECOMMENDATIONS.md)
- [Roadmap](IMPROVEMENTS_ROADMAP.md)
- [Project Review](PROJECT_REVIEW.md)

---

## ❓ Questions?

Don't hesitate to ask! Open an issue or reach out to the maintainers.

**Thank you for contributing to Meeting App! 🎉**
