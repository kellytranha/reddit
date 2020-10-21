import praw
import random
import time
import os


def bot_loggin():
    "This function return your session in Reddit as an instance"
    reddit = praw.Reddit(username=os.environ['REDDIT_USERNAME'],
                         password=os.environ['REDDIT_PASSWORD'],
                         client_id=os.environ['REDDIT_SECRET_CLIENT_ID'],
                         client_secret=os.environ['REDDIT_SECRET_CLIENT_SECRET'],
                         user_agent=os.environ['REDDIT_SECRET_USER_AGENT'])
    return reddit


def get_imgs_bot(reddit):
    "This function returns a list with the first most populars images in the subreddit /wholesomememes"
    jpg_url = []
    for submission in reddit.subreddit('wholesomememes').hot(limit=20):
        if submission.url.endswith(".jpg"):
            jpg_url.append(submission.url)

    return jpg_url


def random_url(lst):
    "This function return a random choice from the list of popular images of the wholesomememes subreddit"
    day_url = random.choice(lst)
    return day_url


if __name__ == '__main__':

    import webbrowser

    reddit = bot_loggin()
    if not reddit.read_only:
        print "Logged to Reddit!!"
    list_urls = get_imgs_bot(reddit)
    picture_day = random_url(list_urls)

    while True:
        number_pictures = len(list_urls)
        if number_pictures == 1:
            print "This is my last wholosome picture for you"
            last_one = list_urls[-1]
            webbrowser.open(last_one)
            break

        ask_user = raw_input("Are you having a bad day? Y or N ?")
        if ask_user == "Y":     
            print "I have %i wholosome pictures to cheer you up" % (number_pictures)
            check = raw_input("Do you want a wholosome picture? Y or N ?")
            if check == "Y":
                webbrowser.open(picture_day)
                list_urls.remove(picture_day)
                picture_day = random_url(list_urls)
                print "I need a short break"
                time.sleep(5)

            else:
                print "Ok, see you soon!"
                break

        else:
            print "That's the spirit! Have a good one!"
            break
