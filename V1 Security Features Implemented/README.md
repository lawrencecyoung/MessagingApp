# Secure Messaging Application



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
- [Security Considerations](#security-onsiderations)
- [Developing Team](#developing-team)

## Overview

This is a secure end-to-end messaging application developed as part of the INFO2222 course assignment. The application allows users to sign up, log in, add friends, and communicate securely with each other through an encrypted messaging system.

## Features

- User authentication with secure password storage (hashing and salting)
- HTTPS communication between the client and server
- End-to-end encryption of messages using a symmetric encryption algorithm (e.g., AES-GCM)
- Message authentication code (HMAC) to ensure message integrity and authenticity
- Friend management system (add friends, view friend requests, accept/reject requests)
- Secure storage of encrypted messages on the server
- Message history retrieval and display in chatrooms

## Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: JavaScript, Socket.IO
- **Database**: SQLite, SQLAlchemy (ORM)
- **Cryptographic Libraries**: PyCryptodome (or PyCA/cryptography)
- **Authentication**: JSON Web Tokens (JWT) or server-side sessions

## Getting Started

1. Clone the repository: `git clone https://github.com/your-repo-url.git`
2. Navigate to the project directory: `cd secure-messaging-app`
3. Install the required Python packages: `pip install -r requirements.txt` and `pip install --upgrade sqlalchemy`
4. Set up the database: `python setup_database.py` (or a similar command to initialize the database)
5. Generate SSL/TLS certificates for HTTPS (e.g., self-signed for local development)
6. Configure the application with the appropriate security settings (e.g., SSL/TLS certificates, secret keys)
7. Run the application: `python app.py`
8. Access the application in your web browser at `https://localhost:5000` (or the appropriate URL)

## Contributing

Read the guidelines below to write good commit messages, branch names, and make pull requests that follow the conventions we will be using throughout the project.

### Commit Messages

- Capitalise the subject line.
- Do not end with a period.
- Use imperative mood, i.e. instead of *"Added ..."* write *"Add ..."*.
- Keep messages logical and relevant, do not write things like *"Please work"* or *"I hate frontend"*. To help decide the extent of this, imagine trying to access a point in the project 2 weeks ago, it would be better to have something like *"Add CSS for Navbar template"* or , so that we know from a glance what the commit is for.
- For more detailed messages, use `git commit -m <title> -m <description>`, however short and concise is still preferred.

### Branch Names
Make a branch using `git checkout -b <branch_name>`.
- Names fall under one of **4** categories
	- Minor Feature: `minor-FeatureName`
	- Major Feature: `major-FeatureName`
	- Patch: `patch-PatchName`
	- Miscellaneous: `name`
		- For example `documentation` for changing the README, or adding another markdown

### Pull Requests
*Summarised from [this article](https://namingconvention.org/git/pull-request-naming.html).*

#### Title
- Short and descriptive summary
- Start with corresponding ticket/story id (e.g. from Jira, GitHub issue)
- Should be capitalized and written in imperative present tense
- Do not end with period
- Suggested format: *#<Ticket_ID> PR description*

#### Description
- Separated with a blank line from the subject
- Explain what, why, etc.
- Max 72 chars
- Each paragraph capitalized

#### Example Pull Request
```
This pull request is part of the work to make it easier for people to contribute to naming convention guides. One of the easiest way to make small changes would be using the Edit on Github button.

To achieve this, we needed to:
- Find the best Gitbook plugin which can do the work
- Integrate it in all the pages to redirect the user to the right page on GitHub for editing
- Make it visible on the page so users can notice it easily
```

## Usage

1. Sign up for a new account or log in with an existing account.
2. Add friends by entering their usernames.
3. View and manage friend requests (sent/received).
4. Click on a friend's username to open a secure chatroom.
5. Start sending and receiving encrypted messages with your friends.
6. View the message history when opening a chatroom.

## Security Considerations

- Passwords are securely hashed and salted before storage in the database.
- All communication between the client and server is encrypted using HTTPS.
- Messages are end-to-end encrypted using a symmetric encryption algorithm (e.g., AES-GCM) with a shared key between clients.
- Message integrity and authenticity are ensured using HMAC or a similar mechanism.
- Encrypted messages are stored on the server, and the user's password is used as the encryption key (or to derive the key).
- Proper authentication and authorization checks are in place for all operations.
- Input validation and sanitization are implemented to prevent potential security vulnerabilities.

## Developing Team
- [Devanshi Mirchandani](https://github.com/devanshimirchandani)
- Lawrence Young

