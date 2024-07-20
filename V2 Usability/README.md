# INFO2222 Usability Project

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
   - [Commit Messages](#commit-messages)
   - [Branch Names](#branch-names)
   - [Pull Requests](#pull-requests)
   	- [Title](#title)
   	- [Description](#description)
   	- [Example Pull Request](#example-pr)
- [Usage](#usage)
- [Deliverables](#deliverables)
- [Developing Team](#developing-team)

## Overview

This project extends the basic E2E secure messaging app developed in the previous assignment to create a website support system for undergraduate School of Computer Science University of Sydney students. The system allows students to share experiences, seek help for their academic studies, and access a knowledge repository where they can share useful reading or learning materials.

## Features

- Improved messaging and friends list functionality
 - Enhanced design for usability and user experience
 - Online status and account role displayed for friends
 - Ability to remove friends
 - Offline message storage and retrieval
- Multi-user chatrooms 
- User account permissions system with different roles (student, staff, admin)
- Knowledge repository
 - Staff and students can create, modify, and comment on articles
 - Staff have additional privileges to delete articles, modify others' articles, and delete comments
 - Staff can mute/unmute users
- One user-specific function based on user investigation

## Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: JavaScript, HTML, CSS
- **Database**: SQLite, SQLAlchemy (ORM)
- **Cryptographic Libraries**: PyCryptodome (or PyCA/cryptography)
- **Authentication**: JSON Web Tokens (JWT) or server-side sessions

## Getting Started

1. Clone the repository: `git clone https://github.com/your-repo-url.git`
2. Navigate to the project directory: `cd info2222-usability-project` 
3. Install the required Python packages: `pip install -r requirements.txt`
4. Set up the database: `python setup_database.py` 
5. Generate SSL/TLS certificates for HTTPS (e.g., self-signed for local development)
6. Configure the application with the appropriate security settings 
7. Run the application: `python app.py`
8. Access the application in your web browser at `https://localhost:5000`

## Contributing

Follow the guidelines in the [Contributing](#contributing) section of the previous README for writing commit messages, branch names, and making pull requests.

## Usage

1. Sign up for a new account or log in with an existing account.
2. Explore the enhanced messaging and friends list features.
3. Join or create multi-user chatrooms.
4. Browse, create, modify and comment on articles in the knowledge repository, depending on your user role permissions.
5. Test out the user-specific function implemented based on user investigation findings.


## Deliverables
Latex Report — https://www.overleaf.com/4482754941grqmqcnsjpnd#14cddd 

## Developing Team
- [Devanshi Mirchandani](https://github.com/devanshimirchandani)
- Lawrence Young