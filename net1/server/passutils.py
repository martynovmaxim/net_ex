import hashlib
import string
import random

import binascii


def generate_salt(length=10):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

def sha256pass(password, num_of_iterations, salt=None):
	if salt is None:
		salt = generate_salt()
	tmp = hashlib.sha256(bytes(password, 'utf-8'))
	for i in range(int(num_of_iterations)):
		tmp = hashlib.sha256(tmp.digest())
	tmp = hashlib.sha256(tmp.digest() + bytes(salt, 'utf-8'))
	return "sha256${}${}${}".format(num_of_iterations, tmp.hexdigest(), salt)

def pbkdf2pass(password, num_of_iterations, salt=None):
	if salt is None:
		salt = generate_salt()
	dk = hashlib.pbkdf2_hmac('sha256', bytes(password, 'utf-8'), bytes(salt, 'utf-8'), int(num_of_iterations))
	tmp = binascii.hexlify(dk).decode('utf-8')
	return "pbkdf2${}${}${}".format(num_of_iterations, tmp, salt)

def create_password(raw_pass, cipher, num_of_iterations=10000, salt=None):
	if cipher == "sha256":
		return sha256pass(raw_pass, num_of_iterations, salt)
	elif cipher == "pbkdf2":
		return pbkdf2pass(raw_pass, num_of_iterations, salt)

def check_password(original_pass, raw_pass):
	cipher, num_of_iterations, hash, salt = str(original_pass).split('$')
	new_pass = create_password(raw_pass, cipher, num_of_iterations, salt)
	return original_pass == new_pass
