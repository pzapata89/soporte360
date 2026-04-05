import bcrypt

password = "123456"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

print(hashed.decode())