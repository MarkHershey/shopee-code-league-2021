import json
import csv
from typing import List, Dict
from pathlib import Path

source_file = Path("contacts.json")

assert source_file.exists

with source_file.open() as f:
    content: List[dict] = json.load(f)


class Customer:
    def __init__(self):
        self.ticket_ids: Dict[str, int] = {}
        self.emails: List[str] = []
        self.phones: List[str] = []
        self.order_ids: List[str] = []
        self.contacts_sum = 0


pool_of_customer = []

tickets = {}  # ticket_id -> Customer
email_dict = {}
phone_dict = {}
order_id_dict = {}


def merge(customer_found: list):
    global pool_of_customer
    global email_dict
    global phone_dict
    global order_id_dict

    if len(customer_found) == 0:
        print("something went wrong")
        return
    elif len(customer_found) == 1:
        pass
    else:
        for i in range(1, len(customer_found)):
            to_be_merged = customer_found[i]
            customer_found[0].ticket_ids = (
                customer_found[0].ticket_ids | to_be_merged.ticket_ids
            )
            to_be_merged = customer_found[i]

            customer_found[0].emails += to_be_merged.emails
            customer_found[0].phones += to_be_merged.phones
            customer_found[0].order_ids += to_be_merged.order_ids

            customer_found[0].emails = list(set(customer_found[0].emails))
            customer_found[0].phones = list(set(customer_found[0].phones))
            customer_found[0].order_ids = list(set(customer_found[0].order_ids))

            if to_be_merged in pool_of_customer:
                pool_of_customer.remove(to_be_merged)

    ## update dictionaries
    for email in customer_found[0].emails:
        email_dict[email] = customer_found[0]

    for phone in customer_found[0].phones:
        phone_dict[phone] = customer_found[0]

    for order_id in customer_found[0].order_ids:
        order_id_dict[order_id] = customer_found[0]

    for ticket_id in customer_found[0].ticket_ids:
        tickets[ticket_id] = customer_found[0]

    pool_of_customer.append(customer_found[0])


limit = 50000000
counter = 0

for ticket in content:
    counter += 1
    if counter >= limit:
        break

    contacts: int = int(ticket.get("Contacts", 0))
    ticket_id = ticket.get("Id")
    email = ticket.get("Email")
    phone = ticket.get("Phone")
    order_id = ticket.get("OrderId")

    customer_found = []

    if email in email_dict:
        customer = email_dict[email]
        customer_found.append(customer)

    if phone in phone_dict:
        customer = phone_dict[phone]
        if id(customer) not in [id(x) for x in customer_found]:
            customer_found.append(customer)

    if order_id in order_id_dict:
        customer = order_id_dict[order_id]
        if id(customer) not in [id(x) for x in customer_found]:
            customer_found.append(customer)

    customer = Customer()
    customer.ticket_ids[ticket_id] = contacts
    if email:
        customer.emails.append(email)
    if phone:
        customer.phones.append(phone)
    if order_id:
        customer.order_ids.append(order_id)

    customer_found.append(customer)

    merge(customer_found)


all_rows = ["ticket_id,ticket_trace/contact"]

for i in sorted(tickets.keys()):
    cus = tickets[i]

    cus.contacts_sum = sum(cus.ticket_ids.values())

    sorted_tickets_id = [str(x) for x in list(sorted(cus.ticket_ids.keys()))]

    column1 = str(i)

    column2 = "-".join(sorted_tickets_id)
    column2 = column2 + ", " + str(cus.contacts_sum)
    row = column1 + "," + '"' + column2 + '"'
    all_rows.append(row)

with open("output.csv", "w") as f:
    f.write("\n".join(all_rows))
