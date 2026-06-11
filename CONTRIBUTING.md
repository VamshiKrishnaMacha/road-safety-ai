# Contributing to Intelligent Road Infrastructure Assessment Using YOLO

Thank you for your interest in contributing to this project. We welcome contributions from developers, researchers, and enthusiasts who want to help improve road infrastructure assessment through computer vision and YOLO-based detection.

## Development Environment Setup

To set up your local development environment:

1. **Clone the repository**
   ```bash
   git clone https://github.com/VamshiKrishnaMacha/Intelligent-Road-Infrastructure-Assessment-Using-YOLO.git
   cd Intelligent-Road-Infrastructure-Assessment-Using-YOLO
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import cv2; import streamlit; import ultralytics; print('Dependencies installed successfully')"
   ```

## Reporting Bugs

If you discover a bug, please report it by creating a new issue using the bug report template. Before submitting:

- Search existing issues to avoid duplicates
- Include detailed steps to reproduce the issue
- Specify your environment (OS, Python version, package versions)
- Provide any relevant screenshots or log output

Reference: [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)

## Suggesting Enhancements

We welcome suggestions for new features and improvements. When proposing an enhancement:

- Clearly describe the feature or improvement you envision
- Explain the problem it addresses
- Provide use cases and examples where possible
- Consider alternatives and their trade-offs

Reference: [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)

## Pull Request Process

Follow these steps when submitting a pull request:

1. **Fork the repository** and create a feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Commit your changes** using conventional commit messages
   ```bash
   git commit -m "feat: add new detection class for crosswalks"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** with a clear description of your changes

6. **Complete the PR checklist** in the pull request template

7. Wait for review. We aim to review all PRs within 7 days.

## Coding Standards

- **PEP 8**: Follow the Python Enhancement Proposal 8 style guide
- **Docstrings**: Document all functions, classes, and modules using Google-style or NumPy-style docstrings
- **Type Hints**: Encourage the use of type hints for function parameters and return values
- **Testing**: Add unit tests for new functionality where applicable
- **Error Handling**: Handle exceptions gracefully with appropriate error messages

Example of a well-documented function:

```python
def detect_road_markings(image_path: str, confidence_threshold: float = 0.5) -> List[dict]:
    """
    Detect road markings in an image using the trained YOLO model.

    Args:
        image_path: Path to the input image file.
        confidence_threshold: Minimum confidence score for detections (default: 0.5).

    Returns:
        List of dictionaries containing detection results with keys:
        'class', 'confidence', 'bbox', and 'label'.

    Raises:
        FileNotFoundError: If the image file does not exist.
        ValueError: If the confidence threshold is not between 0 and 1.
    """
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("Confidence threshold must be between 0 and 1")
    # ... implementation
```

## Commit Message Conventions

We follow the Conventional Commits specification. Format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

| Type | Description |
|------|-------------|
| feat | A new feature |
| fix | A bug fix |
| docs | Documentation only changes |
| style | Formatting, missing semicolons, etc. |
| refactor | Code change that neither fixes a bug nor adds a feature |
| test | Adding or updating tests |
| chore | Maintenance tasks (dependencies, build config) |

**Examples:**

```
feat(detection): add support for new road marking class
fix(ui): correct Streamlit layout responsiveness
docs(readme): update installation instructions
refactor(model): simplify inference pipeline
test(detection): add unit tests for marking classifier
chore(ci): add GitHub Actions workflow for testing
```

## Questions or Need Help?

If you have questions about the project:

- Open a discussion at https://github.com/VamshiKrishnaMacha/Intelligent-Road-Infrastructure-Assessment-Using-YOLO/discussions
- Search existing issues and discussions for similar topics
- Check the README.md for project documentation

## Community Guidelines

We are committed to fostering a welcoming and respectful community. All contributors are expected to follow our Code of Conduct.

Please read: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

By participating in this project, you agree to abide by its terms.