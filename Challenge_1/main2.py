import json
from typing import List, Dict, Set
from pathlib import Path

source_file = Path("contacts.json")
assert source_file.exists

with source_file.open() as f:
    source_data: List[dict] = json.load(f)


class Customer:
    def __init__(self):
        self.ticket_ids: Dict[str, int] = {}
        self.emails: Set[str] = set()
        self.phones: Set[str] = set()
        self.order_ids: Set[str] = set()
        self.contacts_sum = 0


## Global variables
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
        print("Unexpected error: this should not happen.")
        return
    elif len(customer_found) == 1:
        pass
    else:
        for i in range(1, len(customer_found)):
            to_be_merged = customer_found[i]
            customer_found[0].ticket_ids = {
                **customer_found[0].ticket_ids,
                **to_be_merged.ticket_ids,
            }
            customer_found[0].emails.union(to_be_merged.emails)
            customer_found[0].phones.union(to_be_merged.phones)
            customer_found[0].order_ids.union(to_be_merged.order_ids)

    ## update global dictionaries
    for email in customer_found[0].emails:
        email_dict[email] = customer_found[0]

    for phone in customer_found[0].phones:
        phone_dict[phone] = customer_found[0]

    for order_id in customer_found[0].order_ids:
        order_id_dict[order_id] = customer_found[0]

    for ticket_id in customer_found[0].ticket_ids:
        tickets[ticket_id] = customer_found[0]


for ticket in source_data:
    contacts: int = int(ticket.get("Contacts", 0))
    ticket_id: int = int(ticket.get("Id"))
    email: str = ticket.get("Email")
    phone: str = ticket.get("Phone")
    order_id: str = ticket.get("OrderId")

    customer_found = []
    customer_found_id = []

    if email in email_dict:
        customer = email_dict[email]
        customer_found.append(customer)
        customer_found_id.append(id(customer))

    if phone in phone_dict:
        customer = phone_dict[phone]
        if id(customer) not in customer_found_id:
            customer_found.append(customer)
            customer_found_id.append(id(customer))

    if order_id in order_id_dict:
        customer = order_id_dict[order_id]
        if id(customer) not in customer_found_id:
            customer_found.append(customer)
            customer_found_id.append(id(customer))

    ## create a new customer to capture this ticket
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


## Write outputs

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

output_file = Path("output.csv")
with output_file.open(mode="w") as f:
    f.write("\n".join(all_rows))
