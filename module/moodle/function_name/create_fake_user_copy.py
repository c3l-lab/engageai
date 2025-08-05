# # import requests

# # # Moodle REST API info
# # MOODLE_URL = "https://moodle.c3l.ai/webservice/rest/server.php"  # Your Moodle REST URL
# # TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# # FUNCTION_NAME = "core_user_create_users"
# # REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"


# # params = {
# #     "wstoken": TOKEN,
# #     "wsfunction": FUNCTION_NAME,
# #     "moodlewsrestformat": "json"
# # }
# # print(params)

# # data = {
# #     "users[0][username]": "testuser001",
# #     # "users[0][password]": "Pass@12345",
# #     "users[0][firstname]": "Alice",
# #     "users[0][lastname]": "Smith",
# #     # "users[0][email]": "testuser001@example.com",
# #     "users[0][auth]": "manual",
# #     "users[0][lang]": "en",
# #     "users[0][city]": "Sydney",
# #     "users[0][country]": "AU",

# #     "users[1][username]": "testuser002",
# #     # "users[1][password]": "Pass@12345",
# #     "users[1][firstname]": "Bob",
# #     "users[1][lastname]": "Johnson",
# #     # "users[1][email]": "testuser002@example.com",
# #     "users[1][auth]": "manual",
# #     "users[1][lang]": "en",
# #     "users[1][city]": "Melbourne",
# #     "users[1][country]": "AU",

# #     "users[2][username]": "testuser003",
# #     # "users[2][password]": "Pass@12345",
# #     "users[2][firstname]": "Carol",
# #     "users[2][lastname]": "Brown",
# #     # "users[2][email]": "testuser003@example.com",
# #     "users[2][auth]": "manual",
# #     "users[2][lang]": "en",
# #     "users[2][city]": "Brisbane",
# #     "users[2][country]": "AU",
# # }
# # print(data)

# # response = requests.post(REST_URL, params=params, data=data)

# # print(response.json())


# import requests

# # Moodle API info
# MOODLE_URL = "https://moodle.c3l.ai"
# TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
# FUNCTION_NAME = "core_user_create_users"
# REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"

# # Parameters
# params = {
#     "wstoken": TOKEN,
#     "wsfunction": FUNCTION_NAME,
#     "moodlewsrestformat": "json"
# }

# # Users to be created
# users = [
#     {
#         "username": "testuser001",
#         "password": "Pass@12345",
#         "firstname": "Alice",
#         "lastname": "Smith",
#         "email": "testuser001@example.com",
#         "auth": "manual",
#         "lang": "en",
#         "city": "Sydney",
#         "country": "AU"
#     },
#     {
#         "username": "testuser002",
#         "password": "Pass@12345",
#         "firstname": "Bob",
#         "lastname": "Johnson",
#         "email": "testuser002@example.com",
#         "auth": "manual",
#         "lang": "en",
#         "city": "Melbourne",
#         "country": "AU"
#     },
#     {
#         "username": "testuser003",
#         "password": "Pass@12345",
#         "firstname": "Carol",
#         "lastname": "Brown",
#         "email": "testuser003@example.com",
#         "auth": "manual",
#         "lang": "en",
#         "city": "Brisbane",
#         "country": "AU"
#     }
# ]

# # Send request using JSON payload
# response = requests.post(REST_URL, params=params, json={"users": users})

# # Print result
# print(response.json())



#####
import requests

MOODLE_URL = "https://moodle.c3l.ai"
TOKEN = "e2b64938f15b80d29e8845d4b54301e1"
FUNCTION_NAME = "core_user_create_users"
REST_URL = f"{MOODLE_URL}/webservice/rest/server.php"

params = {
    "wstoken": TOKEN,
    "wsfunction": FUNCTION_NAME,
    "moodlewsrestformat": "json"
}

users = [{
    "username": "testuser999",  # must be unique
    "password": "Pass@12345",   # required and must follow Moodle's policy
    "firstname": "Test",
    "lastname": "User",
    "email": "testuser999@example.com",  # must be valid + unique
    "auth": "manual",
    "lang": "en",
    "city": "Adelaide",
    "country": "AU"
}]

response = requests.post(REST_URL, params=params, json={"users": users})

# Check and print result
print(response.status_code)
print(response.text)
