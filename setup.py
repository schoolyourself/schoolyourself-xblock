"""Setup for schoolyourself-lesson XBlock."""

import os
from setuptools import setup

def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, or editable.
    """
    # Remove whitespace at the start/end of the line
    line = line.strip()

    # Skip blank lines, comments, and editable installs
    return not (
        line == '' or
        line.startswith('-r') or
        line.startswith('#') or
        line.startswith('-e') or
        line.startswith('git+')
    )

def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.strip() for line in open(path).readlines()
            if is_requirement(line)
        )
    return list(requirements)


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='schoolyourself_lesson_xblock',
    version='0.1',
    description='School Yourself lesson player',
    packages=[
        'schoolyourself_lesson',
    ],
    install_requires=load_requirements('requirements.txt'),
    entry_points={
        'xblock.v1': [
            'schoolyourself_lesson = schoolyourself_lesson:SchoolYourselfLessonXBlock',
        ]
    },
    package_data=package_data("schoolyourself_lesson",
                              ["static", "public", "templates"]),
)
