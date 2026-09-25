import torch

a = torch.rand(4, 4)
b = torch.zeros(4, 4)
c = torch.ones(4, 4)
print(a)
print(b)
print(c)

import numpy as np
arr = np.array([[1.0, 2.0], [3.0, 4.0]])
print(type(arr))
t = torch.from_numpy(arr)
print(type(t))

print(a+b)
print(a*b)
print(a.sum())
print(a.mean())

x = torch.tensor([2.0], requires_grad=True)
y = x ** 2
y.backward()
print(x.grad)