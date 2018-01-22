import hashlib
from tornado import web, template
from db import DB
import trust

loader = template.Loader('templates')
collection = DB('users')

roles = {
        'viewer': 'Invitado',
        'adder': 'Digitador',
        'editor': 'Editor',
        'reviewer': 'Revisor',
        'operator': 'Operador'
}

def encrypt(password):
    m = hashlib.md5()
    m.update(password.encode('utf-8'))
    return m.digest()

def checkPassword(ID, password):
    user = collection.get({'ID': int(ID)})
    if not user:
        # User does not exist
        return False 
    if not 'password' in user:
        # Password has not been set
        return True
    if user['password'] == encrypt(password):
        # Password is correct
        return True
    # Any other case, it fails
    return False

class List(web.RequestHandler):
    def get(self):
        skip = self.get_argument('skip', 0)
        limit = self.get_argument('limit', 10)
        n = collection.count() 
        users = collection.list(skip, limit)
        self.write(loader.load('users/list.html').generate(users=users, n=n))

class Edit(web.RequestHandler):
    def get(self, ID):
        if ID == '0':
            user = {'ID': 0, 'name': '', 'email': '', 'role': ''}
        else:
            user = collection.get({'ID': int(ID)})
        if user:
            self.write(loader.load('users/edit.html').generate(user=user, roles=roles))
        else:
            self.write("User does not exist")
    def post(self, ID):
        if ID == '0':
            isNew = True
            ID = str(collection.count() + 1)
        else:
            isNew = False
        user = {
            'ID': int(ID),
            'name': self.get_argument('name', ''),
            'email': self.get_argument('email', ''),
            'role': self.get_argument('role', 'viewer')
        }
        if isNew:
            collection.new(user) 
        else:
            collection.update({'ID': user['ID'] }, user)
        self.redirect('/users/' + ID)

class Password(web.RequestHandler):
    def get(self, ID):
        messages = 'Si aún no ha establecido una contraseña, deje el campo de "Contraseña actual" vacío. '
        self.write(loader.load('users/password.html').generate(ID=ID, messages=messages))
    def post(self, ID):
        messages = ''
        current = self.get_argument('current', '')
        newpass = self.get_argument('new', '')
        confirm = self.get_argument('confirm', '')
        if not checkPassword(ID, current):
            messages += 'La contraseña actual es incorrecta. '
        else:
            if not (newpass == confirm):
                messages += 'Verifique que la nueva contraseña coincida. '
            else:
                collection.update({'ID': int(ID)}, {'password': encrypt(newpass)})
                messages += 'Contraseña cambiada con éxito. '
        self.write(loader.load('users/password.html').generate(ID=ID, messages=messages))
       
class Login(web.RequestHandler):
    def get(self):
        self.write(loader.load('users/login.html').generate(messages=None))
    def post(self):
        messages = ''
        valid = False
        email = self.get_argument('email', '')
        password = self.get_argument('password', '')
        remember = self.get_argument('remember', 'off')
        user = collection.get({'email': email})
        if not user:
            messages += 'Usuario no existe. Verifique la dirección de correo. '
        else:
            if not 'password' in user:
                messages += 'Contraseña aún no ha sido asignada. '
                valid = True
            else:
                valid = user['password'] == encrypt(password)
        if valid:
            messages += 'Registro exitoso. Bienvenido(a). '
            self.set_secure_cookie('user', user['_id'])
        self.write(loader.load('users/login.html').generate(messages=messages))
        
