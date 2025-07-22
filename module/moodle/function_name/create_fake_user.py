# import requests
# import pandas as pd
# import os
# import sys
# from faker import Faker


# MOODLE_URL = "https://moodle.c3l.ai"
# # TOKEN = "4ba3fd94d4276b536e2958c7a575e00b"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# FUNCTION = "core_user_create_users"
# REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"

# # Read the CSV file
# df = pd.read_csv('allterm_course163601_finalgrade.csv')

# # users = []
# # for i, row in df.iterrows():
# #     user = {
# #         "username": row["username"],
# #         "password": "FakePassword@123",  # or set to something valid
# #         "firstname": f"Test{row['username']}",
# #         "lastname": "User",
# #         "email": f"{row['username']}@example.com",
# #         "auth": "manual",
# #         "createpassword": 0,   # 0 = password provided, 1 = send setup email
# #         "city": "FakeCity",
# #         "country": "AU"
# #     }
# #     users.append(user)

# # # Prepare POST data
# # post_data = {
# #     "wstoken": TOKEN,
# #     "wsfunction": FUNCTION,
# #     "moodlewsrestformat": "json"
# # }

# # # Add users to POST data with correct keys: users[0][field], users[1][field], etc.
# # for i, user in enumerate(users):
# #     for key, value in user.items():
# #         post_data[f"users[{i}][{key}]"] = value

# # # Send the request
# # response = requests.post(REST_URL, data=post_data)

# # # Print the response JSON
# # print(response.json())

# # payload = {
# #     "wstoken": TOKEN,
# #     "wsfunction": "core_user_create_users",
# #     "moodlewsrestformat": "json",
# #     "users[0][username]": "testuser001",
# #     "users[0][password]": "Password123!",     # Must meet password policy or use createpassword=1
# #     "users[0][firstname]": "Test",
# #     "users[0][lastname]": "User",
# #     "users[0][email]": "testuser001@example.com",
# #     "users[0][auth]": "manual",                # Use 'manual' for manual accounts
# #     "users[0][createpassword]": 0              # 0 = password provided; 1 = Moodle sends setup email
# # }




# fake = Faker()
# users = []

# for i, row in df.iterrows():
#     username = row['username']
#     user = {
#         "username": username,
#         # Use createpassword=1 to skip password requirements (Moodle sends email for password setup)
#         "createpassword": 1,
#         "firstname": fake.first_name(),
#         "lastname": fake.last_name(),
#         "email": f"{username}@example.com",
#         "auth": "manual",
#         "city": fake.city(),
#         "country": fake.country_code(),  # two-letter ISO country code
#         # Optional fields you can add
#         "timezone": "Australia/Adelaide",
#         "description": fake.sentence(nb_words=6),
#     }
#     users.append(user)

# # Now you have a list of user dicts with username from your dataframe and rest fake.

# # If you want to prepare payload for Moodle API POST:
# post_data = {
#     "wstoken": "YOUR_TOKEN_HERE",
#     "wsfunction": "core_user_create_users",
#     "moodlewsrestformat": "json"
# }

# for i, user in enumerate(users):
#     for key, value in user.items():
#         post_data[f"users[{i}][{key}]"] = value
#         print(value)

# # # Send the request
# # response = requests.post(REST_URL, data=post_data)
# # # Print the response JSON
# # print(response.json())


####################################################################################################



import requests
import pandas as pd
from faker import Faker

# Moodle setup
MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
FUNCTION = "core_user_create_users"
REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"

# Load your CSV and filter
df = pd.read_csv("allterm_course163601_finalgrade_test.csv")
df = df[df['term_code'] == 2405]
df = df[df['username'].notna()]
df = df[~df['username'].duplicated()]
df = df.reset_index(drop=True)
print(len(df))


# Faker setup
fake = Faker()
users = []



# Prepare users payload
users = []
for i, row in df.iterrows():
    user = {
        "username": row['username'],
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "email": f"{row['username']}@example.com",
        "auth": "manual",
        "createpassword": 1     # Let Moodle send password setup email
        # "country": "AU"
    }
    users.append(user)

# # Generate users with fake data
# for i, row in df.iterrows():
#     username = row['username']
#     user = {
#         "username": username,
#         "createpassword": 1,  # Set to 1 if you want Moodle to send password setup email
#         "firstname": fake.first_name(),
#         "lastname": fake.last_name(),
#         "email": f"{username}@example.com",
#         "auth": "manual",
#         "city": fake.city(),
#         "country": fake.country_code(),
#         "timezone": "Australia/Adelaide",
#         "description": fake.sentence(nb_words=6),
#     }
#     users.append(user)

# Prepare POST data for Moodle
post_data = {
    "wstoken": TOKEN,
    "wsfunction": FUNCTION,
    "moodlewsrestformat": "json"
}

# Flatten users into post_data format expected by Moodle
for i, user in enumerate(users):
    for key, value in user.items():
        post_data[f"users[{i}][{key}]"] = value
        for k, v in post_data.items():
            print(f"{k}: {v}")

# Send the request
response = requests.post(REST_URL, data=post_data)

# Output the result
print(response.status_code)
print(response.json())

