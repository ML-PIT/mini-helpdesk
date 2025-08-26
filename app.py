import os
from flask.cli import with_appcontext
import click
from app import create_app, db
from app.models.user import User
from app.models.ticket import Ticket
from app.models.knowledge import KnowledgeArticle
from app.models.audit import AuditLog

app = create_app(os.getenv('FLASK_ENV'))

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Run tests under code coverage.')
@with_appcontext
def test(coverage):
    """Run the unit tests."""
    import unittest
    import sys
    
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command()
@with_appcontext
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models.user import User
    
    # Migrate database to latest revision
    upgrade()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(email='admin@mlgruppe.de').first()
    if admin is None:
        admin = User(
            username='admin',
            email='admin@mlgruppe.de',
            first_name='System',
            last_name='Administrator',
            role='admin'
        )
        admin.set_password('ChangeMe123!')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created: admin@mlgruppe.de / ChangeMe123!')

@app.cli.command()
@with_appcontext
def create_sample_data():
    """Create sample data for development."""
    from app.models.user import User
    from app.models.ticket import Ticket
    import datetime
    
    # Create sample users
    users = [
        {'username': 'teamlead1', 'email': 'teamlead@mlgruppe.de', 'role': 'team_leader', 'first_name': 'Team', 'last_name': 'Leader'},
        {'username': 'agent1', 'email': 'agent1@mlgruppe.de', 'role': 'support_agent', 'first_name': 'Support', 'last_name': 'Agent'},
        {'username': 'customer1', 'email': 'kunde@example.com', 'role': 'customer', 'first_name': 'Max', 'last_name': 'Mustermann'}
    ]
    
    for user_data in users:
        if not User.query.filter_by(email=user_data['email']).first():
            user = User(**user_data)
            user.set_password('test123')
            db.session.add(user)
    
    db.session.commit()
    print('Sample users created!')

if __name__ == '__main__':
    app.run(debug=True)
