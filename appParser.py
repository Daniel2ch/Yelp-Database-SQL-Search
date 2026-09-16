import json

# Clean up strings for SQL
def cleanStr4SQL(s):
    return s.replace("'","''").replace("\n"," ")

# Get all key-value pairs from nested attribute dicts
def flattenAttributes(attributes):
    result = []
    for key, value in attributes.items():
        if isinstance(value, dict):
            result += flattenAttributes(value)
        else:
            result.append((key,value))
    return result
        
# Buisness data parser
def parseBusinessData():
    print ("Parsing business...")
    with open('yelp_business.json', 'r', encoding='utf-8') as infile, \
         open('insert_business.sql', 'w', encoding='utf-8') as bfile, \
         open('insert_categories.sql', 'w', encoding='utf-8') as cfile, \
         open('insert_attributes.sql', 'w', encoding='utf-8') as afile:
        
        count = 0
        for line in infile:
            # Parse each line as a json object
            data = json.loads(line)
            business_id = data['business_id']
            name = cleanStr4SQL(data['name'])
            address = cleanStr4SQL(data['address'])
            city = cleanStr4SQL(data['city'])
            state = data['state']
            zipcode = data['postal_code']
            review_count = data['review_count']
            stars = data['stars']

            bfile.write(
                f"INSERT INTO business (business_id, name, address, city, state, zipcode, stars, review_count, reviewrating, numCheckins) "
                f"VALUES ('{business_id}', '{name}', '{address}', '{city}', '{state}', '{zipcode}', {stars}, {review_count},  0.0, 0);\n"
            )

            # Write business categories
            if data.get("categories"):
                for category in data['categories']:
                    category_clean = cleanStr4SQL(category)
                    cfile.write(f"INSERT INTO Categories (business_id, category_name) "
                                f"VALUES ('{business_id}', '{category_clean}');\n")

            # Write business attributes
            if data.get("attributes"):
                flat_attrs = flattenAttributes(data["attributes"])
                for attr, value in flat_attrs:
                    attr_clean = cleanStr4SQL(attr)
                    value_clean = cleanStr4SQL(str(value))
                    afile.write(f"INSERT INTO Attributes (business_id, attr_name, value) "
                                f"VALUES ('{business_id}', '{attr_clean}', '{value_clean}');\n")

            count += 1

    print(f"{count} business records processed.")


# Parse user json 
def parseUserData():
    print("Parsing users...")
    with open('yelp_user.json', 'r', encoding='utf-8') as infile, \
         open('insert_user.sql', 'w', encoding='utf-8') as ufile, \
         open('insert_friendship.sql', 'w', encoding='utf-8') as ffile:
        
        count = 0
        for line in infile:
            data = json.loads(line)
            user_id = data['user_id']
            name = cleanStr4SQL(data['name'])
            yelping_since = data['yelping_since']
            review_count = data['review_count']
            fans = data['fans']
            average_stars = data['average_stars']
            funny = data['funny']
            useful = data['useful']
            cool = data['cool']

            ufile.write(
                f"INSERT INTO Users (user_id, name, yelping_since, review_count, fans, average_stars, funny, useful, cool) "
                f"VALUES ('{user_id}', '{name}', '{yelping_since}', {review_count}, {fans}, {average_stars}, {funny}, {useful}, {cool});\n")
                       
             # Write friend relationships
            for friend_id in data.get("friends", []):
                ffile.write(f"INSERT INTO Friendship (user_id, friend_id) VALUES ('{user_id}', '{friend_id}');\n")

            count += 1

    print(f"{count} user records processed.")


# Parses review json
def parseReviewData():
    print("Parsing reviews...")
    with open('yelp_review.json', 'r', encoding='utf-8') as infile, \
         open('insert_review.sql', 'w', encoding='utf-8') as outfile:
        
        count = 0
        for line in infile:
            data = json.loads(line)
            review_id = data['review_id']
            user_id = data['user_id']
            business_id = data['business_id']
            stars  = data['stars']
            date = data['date']
            text = cleanStr4SQL(data['text'])
            useful = data['useful']
            funny = data['funny']
            cool = data['cool']

            # Write review info
            outfile.write(f"INSERT INTO Review (review_id, business_id, user_id, stars, date, text, useful_vote, funny_vote, cool_vote) "
                          f"VALUES ('{review_id}', '{business_id}', '{user_id}', {stars}, '{date}', '{text}', {useful}, {funny}, {cool});\n")
            count += 1

    print(f"{count} Review records processed.")


# Parse checkin json
def parseCheckinData():
    print("Parsing check-ins...")
    with open('yelp_checkin.json', 'r', encoding='utf-8') as infile, \
         open('insert_checkins.sql', 'w', encoding='utf-8') as outfile:
        
        count = 0
        for line in infile:
            data = json.loads(line)
            business_id = data['business_id']
            time_data = data.get("time", {})

            # Write check-in records for each day and hour
            for day, hours in time_data.items():
                for hour, checkins in hours.items():
                    outfile.write(f"INSERT INTO Checkin (business_id, day, time, count) "
                                  f"VALUES ('{business_id}', '{day}', '{hour}', {checkins});\n")
            count += 1

    print(f"{count} check-in records processed.")


if __name__ == '__main__':
    parseBusinessData()
    parseUserData()
    parseCheckinData()
    parseReviewData()

