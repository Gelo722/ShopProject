from app import app, db
from app.models import Shop, Deliveries

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Shop': Shop, 'Deliveries': Deliveries}

if __name__ =="__main__":
        app.run(debug=True)
