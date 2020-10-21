from server import User, db

db.drop_all()
db.create_all()

admin = User(username='admin')
guest = User(username='guest')

db.session.add(admin)
db.session.add(guest)
db.session.commit()

print User.query.all()
