def run_selenium_script(): 
    import os
    import time
    import socket
    import uuid
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from datetime import datetime
    from pymongo import MongoClient
    from dotenv import load_dotenv

    load_dotenv()
    TWITTER_EMAIL = os.getenv("TWITTER_EMAIL")
    TWITTER_PHONE = os.getenv("TWITTER_PHONE")
    TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
    MONGODB_URI = os.getenv("MONGODB_URI")

    # Connect to MongoDB
    try:
        client = MongoClient(MONGODB_URI)
        db = client['TwitterTrends']
        collection = db['TrendData']
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return {"error": "MongoDB connection failed"}

    # Set up the WebDriver
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
    except Exception as e:
        print(f"WebDriver setup error: {e}")
        return {"error": "WebDriver setup failed"}

    try:
        driver.get("https://twitter.com/login")
        time.sleep(5)

        username_field = driver.find_element(By.NAME, "text")
        username_field.send_keys(TWITTER_EMAIL)
        username_field.send_keys(Keys.RETURN)
        time.sleep(5)

        # Check if a phone number is requested
        try:
            phone_field = driver.find_element(By.NAME, "text")
            phone_field.send_keys(TWITTER_PHONE)
            phone_field.send_keys(Keys.RETURN)
            time.sleep(5)
        except Exception as e:
            print("Phone number step skipped:", e)

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(TWITTER_PASSWORD)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)

        print("Login successful!")

        # Navigate to the home page
        driver.get("https://twitter.com/home")
        time.sleep(5)

        # Locate the "What's Happening" section
        try:
            trends_section = driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Timeline: Trending now')]")
        except Exception as e:
            print(f"Trending section not found: {e}")
            return {"error": "Trending section not found"}

        # Locate all trending topic containers
        try:
            trending_topics = trends_section.find_elements(By.XPATH, ".//div[@role='link']")
        except Exception as e:
            print(f"Trending topics not found: {e}")
            return {"error": "Trending topics not found"}

        # Extract trending topics
        print("Raw Trending Topics:")
        raw_topics = []
        for i, topic in enumerate(trending_topics[:5], start=1):
            try:
                topic_text = topic.text.strip()
                raw_topics.append(topic_text)
                print(f"{i}. {topic_text}")
            except Exception as e:
                print(f"Error extracting topic {i}: {e}")

        # Generate trend data
        unique_id = str(uuid.uuid4())
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip_address = socket.gethostbyname(socket.gethostname())

        trend_data = {
            "_id": unique_id,
            "trend1": raw_topics[0] if len(raw_topics) > 0 else "N/A",
            "trend2": raw_topics[1] if len(raw_topics) > 1 else "N/A",
            "trend3": raw_topics[2] if len(raw_topics) > 2 else "N/A",
            "trend4": raw_topics[3] if len(raw_topics) > 3 else "N/A",
            "trend5": raw_topics[4] if len(raw_topics) > 4 else "N/A",
            "timestamp": end_time,
            "ip_address": ip_address,
        }

        # Insert into MongoDB
        print("Inserting trend_data into MongoDB:", trend_data)
        try:
            collection.insert_one(trend_data)
            print("Data inserted into MongoDB.")
        except Exception as e:
            print(f"Error inserting into MongoDB: {e}")
            return {"error": "MongoDB insertion failed"}

        return trend_data

    finally:
        time.sleep(5)
        driver.quit()
        client.close()
        print("Browser and MongoDB connection closed.")
