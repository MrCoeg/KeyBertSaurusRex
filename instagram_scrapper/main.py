import json
import os
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv

from instagram_scrapper.helper import MyEncoder
from instagram_scrapper.model import *


def login(driver, username, password):
    driver.get("https://www.instagram.com")

    username_input = WebDriverWait(driver, timeout=5).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "input[name=username]"))
    password_input = WebDriverWait(driver, timeout=5).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "input[name=password]"))
    login_btn = WebDriverWait(driver, timeout=10).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "button[type=submit]"))

    username_input.send_keys(username)
    password_input.send_keys(password)

    login_btn.click()


def escape_after_login(driver):
    # Save login info
    save_login_info_btn = WebDriverWait(driver, timeout=10).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "button[type=button]._acan._acap._acas._aj1-"))
    save_login_info_btn.click()

    time.sleep(3)

    # Notification
    turn_on_notification_btn = WebDriverWait(driver, timeout=10).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "button._a9--._a9_1"))
    turn_on_notification_btn.click()


def get_user(driver, username):
    user = User(username)

    driver.get("https://www.instagram.com/" + username)
    time.sleep(3)
    posts = driver.find_elements(By.CSS_SELECTOR,
                                 "div._ab8w._ab94._ab99._ab9f._ab9m._ab9o._abcm div._ac7v._aang div._aabd._aa8k._aanf a.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz._a6hd")

    post_code_pattern = re.compile(r"https://www.instagram.com/p/(.*)/")
    post_codes = []
    for post in posts:
        href = post.get_attribute("href")
        post_code = re.search(post_code_pattern, href).group(1)
        post_codes.append(post_code)

    itr = len(post_codes)
    if itr > 4:
        itr = 4

    for code in post_codes:
        if itr < 0:
            break

        try:
            post_model = get_post(driver, code)
            user.add_post(post_model)
        except:
            pass
        finally:
            itr -= 1

    return user


def get_post(driver, post_code):
    driver.get("https://www.instagram.com/p/" + post_code)
    description = WebDriverWait(driver, timeout=5).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "._aacl._aaco._aacu._aacx._aad7._aade")).text

    post = Post(description, post_code)

    time.sleep(4)

    load_more_comments(driver)

    comments = WebDriverWait(driver, timeout=4).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "ul._a9z6._a9za ul._a9ym"))

    for comment in comments:
        comment_text = comment.find_element(By.CSS_SELECTOR, "span._aacl._aaco._aacu._aacx._aad7._aade").text
        comment_model = Comment(comment_text)

        # Check if there is any reply
        try:
            view_replies_btn = comment.find_element(By.CSS_SELECTOR, "button[type=button]._acan._acao._acas._aj1-")
            view_replies_btn.click()

            time.sleep(1.5)

            replies = comment.find_elements(By.CSS_SELECTOR, "ul._a9yo li._a9zj._a9zl._a9ye")
            for reply in replies:
                reply_text = reply.find_element(By.CSS_SELECTOR, "span._aacl._aaco._aacu._aacx._aad7._aade").text
                comment_model.add_reply(Reply(reply_text))

        except NoSuchElementException:
            pass
        finally:
            post.add_comment(comment_model)

    return post


def load_more_comments(driver):
    i = 5
    while i > 0:
        time.sleep(1.5)
        try:
            load_comment_btn = driver.find_element(By.CSS_SELECTOR,
                                                   'li div._ab8w._ab94._ab99._ab9h._ab9m._ab9p._abcj._abcm button._abl-')
            load_comment_btn.click()
            i -= 1
        except NoSuchElementException:
            break


def join_comments(username):
    # Open the JSON file
    with open("data/" + username + ".json", 'r') as f:
        # Decode the JSON data
        data = json.load(f)

    strs = []
    for posts in data["posts"]:
        for comments in posts["comments"]:
            strs.append(comments["text"])
            for replies in comments["replies"]:
                strs.append(replies["text"])

    return ', '.join(strs)


def main():
    load_dotenv()

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.delete_all_cookies()

    login(driver, os.environ.get('INSTAGRAM_USERNAME'), os.environ.get('INSTAGRAM_PASSWORD'))
    time.sleep(5)

    escape_after_login(driver)
    time.sleep(5)

    data = get_user(driver, os.environ.get('INSTAGRAM_TARGET_USERNAME'))
    driver.quit()
    json_str = json.dumps(data, cls=MyEncoder, indent=2)

    with open(f'data/{data.username}.json', 'w') as file:
        file.write(json_str)
