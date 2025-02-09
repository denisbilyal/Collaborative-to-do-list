# Collaborative To-Do List

## Overview
This is a collaborative To-Do List application built with Flask and SQLAlchemy. It allows users to create and manage task tables, invite others to collaborate, and track task progress. Users can register, log in, and manage their tasks in an organized manner. This feature lets you work together with others who are on the same network as the server. It makes it easy to communicate and share information with your team.

## Features
- **User Authentication**: Register and log in with a username and password.
- **Task Tables**: Create and manage collaborative task tables.
- **Roles & Permissions**: Users can be assigned roles (CREATOR, ADMIN, REGULAR).
- **Task Management**:
  - Tasks have a title, description, tags, priority, and due date.
  - Tasks progress through three columns: "To Do Tasks", "In Progress Tasks", and "Completed Tasks".
  - Users can pick tasks, complete them, and track their progress.
  - Task updates are real-time using WebSockets.

- **Collaboration**:
  - Users can invite others via their usernames.
  - Only the table creator can remove users or assign management roles.
  - Users can leave tables whenever they want.
- **Action History**:
  - Tracks task creation, deletions, user additions/removals, and other changes.
- **Custom Tags**: Users can create and assign custom tags to tasks.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip (Python package manager)

### Setup Instructions
1. **Clone the repository**
   ```sh
   git clone https://github.com/denisbilyal/Collaborative-to-do-list
   cd Collaborative-to-do-list
   ```

2. **Create a virtual environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```sh
   python main.py
   ```

## Technologies Used
- **Backend**: Flask
- **Database**: SQLAlchemy (with SQLite)
- **Authentication**: Flask-Login
- **Real-time Updates**: WebSockets
