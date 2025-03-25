import requests
import json
from collections import defaultdict

# URL of the Spliit group expenses page
group_url = "https://spliit.app/groups/b8PXTcpwcUsy1gMGGU1fA/expenses/export/json"

# Attempt to fetch the data (hypothesizing an API endpoint or direct data)
# Note: We’ll try the URL directly first, then adjust if needed
response = requests.get(group_url)

# Check if we got HTML instead of JSON (indicating we need to find the API endpoint)
if 'text/html' in response.headers['Content-Type']:
    print("Received HTML instead of JSON. Attempting to find API endpoint...")
    # Hypothetical API endpoint (based on common patterns, not confirmed)
    api_url = "https://spliit.app/api/groups/b8PXTcpwcUsy1gMGGU1fA/expenses"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        print(f"Error: Unable to fetch data from {api_url}. Status code: {response.status_code}")
        print("The Spliit app may not expose a public API, or authentication is required.")
        print("Please manually export the JSON from the website and use the file-based approach.")
        exit(1)

try:
    data = response.json()
except json.JSONDecodeError:
    print("Error: Response is not valid JSON. Manual export may be required.")
    exit(1)

# Create mapping of participant IDs to names
participant_names = {p['id']: p['name'] for p in data['participants']}

# Track what each person owes for
owes_by_person = defaultdict(list)

# Process each expense
for expense in data['expenses']:
    amount_cents = expense['amount']  # Amount in cents
    amount_dollars = amount_cents / 100  # Convert to dollars
    title = expense['title']
    date = expense['expenseDate'].split('T')[0]
    category = expense['category']['name']
    split_mode = expense['splitMode']
    participants = expense['paidFor']
    num_participants = len(participants)
    
    if split_mode == 'EVENLY':
        amount_per_person_dollars = amount_dollars / num_participants
        for participant in participants:
            participant_id = participant['participantId']
            owes_by_person[participant_id].append({
                'title': title,
                'amount': amount_per_person_dollars,
                'date': date,
                'category': category
            })
    elif split_mode == 'BY_AMOUNT':
        total_shares = sum(p['shares'] for p in participants)
        for participant in participants:
            participant_id = participant['participantId']
            share = participant['shares']
            amount_owed_dollars = amount_dollars * (share / total_shares)
            owes_by_person[participant_id].append({
                'title': title,
                'amount': amount_owed_dollars,
                'date': date,
                'category': category
            })

# Print detailed breakdown of what each person owes
print("Detailed Owed Amounts Breakdown (in $):")
print("=" * 60)
for participant_id in participant_names:
    name = participant_names[participant_id]
    expenses = owes_by_person[participant_id]
    
    print(f"\n{name}")
    print("-" * 40)
    
    if expenses:
        # Sort expenses by date
        expenses.sort(key=lambda x: x['date'])
        
        total_owed_dollars = 0
        for expense in expenses:
            print(f"Item: {expense['title']}")
            print(f"Category: {expense['category']}")
            print(f"Amount Owed: ${expense['amount']:,.2f}")
            print()
            total_owed_dollars += expense['amount']
        
        print(f"Total Owed by {name}: ${total_owed_dollars:,.2f}")
    else:
        print("No expenses owed")
    print("=" * 40)