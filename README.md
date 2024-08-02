General functionality: Custom system for managing tasks
Features: 
- user levels - managers and members
- custom login - manager recognition
- add / view / delete / set status to tasks
- add / view / delete comments
- email notifications on email assignment
- menu buttons:
  - Create task
  - View tasks
  - View Weekly tasks
  - View Monthly tasks
  - View closed tasks
  - Task charts (for managers)
  - Search field
- Models:
  - Users:
    - id
    - username
    - password
    - email
    - is_admin
    - tasks
   
  - Task:
    - id
    - title
    - body
    - creation_date
    - exp_date
    - user_id
    - status
    - comments
      
  - Comment:
    - id
    - body
    - creation_date
    - task_id
    - user_id
    - comment_owner
    - user
Members can:
- create task
- delete own tasks
- set status to own tasks
- add comments
- update / delete own comments
Managers can:
- create task and assign it to a member
- delete any task
- set status to any task
- view charts
- add comments
- update / delete own comments
