print("python is fun!")

a = [1, 2, 3]
b = a
a[0] = 0

print(a) # [0, 2, 3]
print(b) # [0, 2, 3]
print(a is b) # True