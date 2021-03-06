import json
import csv
from typing import List, Dict
from pathlib import Path


class Customer:
    def __init__(self):
        self.ticket_ids: Dict[str, int] = {}
        self.emails: List[str] = []
        self.phones: List[str] = []
        self.order_ids: List[str] = []
        self.contacts_sum = 0


email = {}

c1 = Customer()
c2 = Customer()

email["haha"] = c1
email["thishih"] = c2


if c1 is c2:
    print("a")

if c1 == c2:
    print("a")


print(id(c1))
print(id(c2))

pool = [c1, c2]

if c1 in pool:
    print("YES")

print(id(pool[0]))


print("-----------")

a = email["haha"]
b = email["thishih"]


print(id(a))
print(id(b))

if a in pool:
    print("YES")

if a in email.values():
    print("YES")
