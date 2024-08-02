from task_manager import app, db
from task_manager.views import *
from task_manager.models import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)