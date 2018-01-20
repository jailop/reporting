from tornado import web, template
from db import DB
import trust

loader = template.Loader('templates')

roles = {
        'viewer': 'Invitado',
        'adder': 'Digitador',
        'editor': 'Editor',
        'reviewer': 'Revisor',
        'operator': 'Operador'
}

class List(web.RequestHandler):
    collection = DB('users')
    def get(self):
        skip = self.get_argument('skip', 0)
        limit = self.get_argument('limit', 10)
        n = self.collection.count() 
        users = self.collection.list(skip, limit)
        self.write(loader.load('users/list.html').generate(users=users, n=n))

class Edit(web.RequestHandler):
    collection = DB('users')
    def get(self, ID):
        if ID == '0':
            user = {'ID': 0, 'name': '', 'email': '', 'role': ''}
        else:
            user = self.collection.get({'id': int(ID)})
        print(user)
        self.write(loader.load('users/edit.html').generate(user=user, roles=roles))
    def post(self, ID):
        if ID == '0':
            isNew = True
            ID = str(self.collection.count() + 1)
        else:
            isNew = False
        user = {
            'ID': int(ID),
            'name': self.get_argument('name', ''),
            'email': self.get_argument('email', ''),
            'role': self.get_argument('role', 'viewer')
        }
        if isNew:
            self.collection.new(user) 
        else:
            self.collection.update({'id': user['ID'] }, user)
        self.redirect('/users/' + ID)
