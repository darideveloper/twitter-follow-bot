import os
import csv
import time
import random
import config
from selenium.webdriver.common.by import By
from scraping_manager.automate import WebScraping

class Bot (WebScraping):
    
    def __init__ (self):
        """ Constructor of class
        """
        
        # Read credentials
        self.debug = config.get_credential ("debug")
        self.headless = config.get_credential ("headless")
        self.list_follow = config.get_credential ("list_follow")
        self.max_follow = config.get_credential ("max_follow")
        self.chrome_folder = config.get_credential ("chrome_folder")
        
        # User to follow or unfollow
        self.profile_links = []
        
        # History file
        self.history_file = os.path.join (os.path.dirname (__file__), "history.csv")
        
        # Css selectors
        self.selectors = {
            "user": 'input[autocomplete="username"]',
            "user_next": '.css-1dbjc4n.r-mk0yit + div[role="button"][tabindex="0"]',
            "password": 'input[autocomplete="current-password"]',
            "login": '.css-1dbjc4n.r-pw2am6 > [role="button"]',
            "followers_links": '[aria-label="Timeline: Followers"] [data-testid="cellInnerDiv"] a[role="link"]', 
            "follow": '.css-1dbjc4n.r-6gpygo > [role="button"]',
            "post": '[data-testid="cellInnerDiv"] > .css-1dbjc4n',
            "like": '[role="group"] > div:nth-child(3) > [role="button"]',
            "confirm_unfollow": '[data-testid="confirmationSheetConfirm"]',
        }
        self.selectors["post_link"] = f"{self.selectors['post']} .css-1dbjc4n.r-18u37iz.r-1q142lx a"
        self.selectors["post_like_user"] = f"{self.selectors['post']} a"
        self.selectors["unfollow"] = f"{self.selectors['follow']}"
    
        # Start chrome
        super ().__init__ (headless=self.headless, chrome_folder=self.chrome_folder, start_killing=True)
        
        # Get history rows
        self.followed_classic, self.followed_advanced, \
        self.unfollowed, self.history = self.__get_history__ ()
        
    def __get_history__ (self) -> tuple:
        """ Read rows from history file

        Returns:
            tuple: lists of followed and unfollowed users
                list: followed_classic
                list: followed_advanced
                list: unfollowed
                list: history_rows
        """
        
        with open (self.history_file, "r") as file:
            csv_reader = csv.reader (file)
            history = list (csv_reader)
            
        followed_classic = list(map(lambda row: row[0], filter(lambda row: row[1] == "followed_classic", history)))
        followed_advanced = list(map(lambda row: row[0], filter(lambda row: row[1] == "followed_advanced", history)))
        unfollowed = list(map(lambda row: row[0], filter(lambda row: row[1] == "unfollowed", history)))
        history_rows = list(map(lambda row: row[0], history))
        
        return followed_classic, followed_advanced, unfollowed, history_rows      
    
    def __wait__ (self, message:str=""):
        """ Wait time and show message

        Args:
            message (str, optional): message to show after wait time. Defaults to "".
        """
        
        time.sleep (random.randint(30, 180))
        if message:
            print (message)
    
    def __load_links__ (self, selector_link:str, load_more_selector:str="", filter_advanced:bool=False, 
                       filter_classic:bool=False, filter_unfollowed:bool=False, load_from:str=False): 
        """ Extract links from specific selects, and go down in the page for load the next links
        Save links in "profile_links" attribute

        Args:
            selector_link (str): css selector for profile links
            load_more_selector (str, optional): element to click for load more results. Defaults to "".
            filter_advanced (bool, optional): skip users already followed with the advanced bot. Defaults to False.
            filter_classic (bool, optional): skip users already followed with the classic bot. Defaults to False.
            filter_unfollowed (bool, optional): skip users already unfollowed. Defaults to False.
        """
        
                
        print (f"\tGetting user profiles from {load_from}...")
        
        # Gennerate list of users to skip
        skip_users = []
        if filter_advanced:
            skip_users += self.followed_advanced
        if filter_classic:
            skip_users += self.followed_classic
        if filter_unfollowed:
            skip_users += self.unfollowed
        
        more_links = True
        last_links = []
        while more_links: 
            
            # Get all profile links
            time.sleep(6)
            self.refresh_selenium()
            links = self.get_attribs(selector_link, "href", allow_duplicates=False, allow_empty=False)
            
            # Break where no new links
            if links == last_links: 
                break
            else: 
                last_links = links
            
            # Validate each link
            for link in links: 
                
                # Save current linl
                if link not in skip_users and link not in self.profile_links: 
                    self.profile_links.append(link)
                    
                # Count number of links
                links_num = len (self.profile_links)
                if links_num >= self.max_follow: 
                    more_links = False
                    break
            
            # Go down
            self.go_bottom ()
            
            # Click button for load more results
            if load_more_selector:
                try:
                    self.get_elem (load_more_selector)
                except:
                    pass
                else:
                    self.click_js (load_more_selector)
                    time.sleep(3)
    
    def __save_user_history__ (self, user:str, status:str):
        """ Save new user in history file

        Args:
            user (str): user link
            status (str): status of the user
        """
        
        with open (self.history_file, "a", newline='') as file:
            csv_writer = csv.writer (file)
            csv_writer.writerow ([user, status])
            
    def __set_page_wait__ (self, user:str):
        """ Open user profile and wait for load

        Args:
            user (str): user link
        """
        self.set_page (user)
        time.sleep (10)
        self.refresh_selenium ()
        
    def __follow_like_users__ (self, max_posts:int=3, follow_type:str=""):
        """ Follow and like posts of users from a profile_links

        Args:
            max_posts (int, optional): number of post to like. Defaults to 3.
            follow_type (str, optional): type of follow. Defaults to "".
        """
        
        for user in self.profile_links:
            
            # Set user page
            self.__set_page_wait__ (user)
            
            # Follow user
            follow_text = self.get_text (self.selectors["follow"])
            if follow_text.lower().strip() == "follow":
                self.click_js (self.selectors["follow"])
                self.__wait__ (f"user followed: {user}")
            else:
                self.__wait__ (f"user already followed: {user}")
            
            # Get posts of user
            posts_elems = self.get_elems (self.selectors["post"])
            if len(posts_elems) > max_posts:
                posts_elems = posts_elems[:max_posts]
            
            # loop posts to like
            for post in posts_elems:
                
                # Like post
                try:
                    like_button = post.find_element(By.CSS_SELECTOR, self.selectors["like"])
                except:
                    continue
                else:
                    like_button.click ()
                        
                    # Wait after like
                    post_index = posts_elems.index(post) + 1
                    self.__wait__ (f"\tpost liked: {post_index}/{max_posts}")
            
            # Save current user in history
            self.__save_user_history__ (user, follow_type)
            
    def __get_unfollow_users__ (self) -> list:
        """ Request to the user the list of followed users from text files

        Returns:
            list: list of followed users to unfollow
        """
        
        # Request follow file to user
        manu_options = ["1", "2"]
        while True:
            print ("1. Follow Advanced")
            print ("2. Follow Classic")
            option = input ("Select folloed list, for unfollow: ")
            if option not in manu_options: 
                print ("\nInvalid option")
                continue
            else:
                break
        
        # Select followed list 
        if option == "1": 
            followed = self.followed_advanced
        elif option == "2":
            followed = self.followed_classic
            
        # Remove users already unfollowed
        followed = list(filter(lambda user: user not in self.unfollowed, followed))
        
        return followed

    def follow_classic (self):
        """ Follow users from current followers list of an specific users
        """
        
        # Loop each user
        for user in self.list_follow:
                        
            print (f"getting users from followers list {user}...")
            
            # Show followers page 
            url = f"https://twitter.com/{user}/followers"
            self.set_page (url)
                    
            # Go down and get profiles links
            self.__load_links__ (
                self.selectors["followers_links"], 
                filter_classic=True,
                filter_unfollowed=True,
                load_from="followers"
            )
            
        print (f"{len(self.profile_links)} users found")
        
        # Follow users
        self.__follow_like_users__ (follow_type="followed_classic")
    
    def follow_advanced (self):
        """ Follow users from linkes of last posts from specific users
        """
        
        # Loop each user
        for user in self.list_follow:
            
            # Show followers page 
            url = f"https://twitter.com/{user}"
            self.__set_page_wait__ (url)
            
            # Get posts links
            posts_links = self.get_attribs (self.selectors["post_link"], "href")
            
            # Open each post details
            for post_link in posts_links:
                
                # Open post likes
                post_link_likes = post_link + "/likes"
                self.__set_page_wait__ (post_link_likes)
                
                # Go down and get profiles links from likes
                self.__load_links__ (
                    self.selectors["post_like_user"], 
                    filter_advanced=True,
                    filter_unfollowed=True,
                    load_from="likes"
                )
                
                # Open post comments
                self.__set_page_wait__ (post_link)
                
                # Go down and get profiles links from comments
                self.__load_links__ (
                    self.selectors["post_like_user"], 
                    filter_advanced=True,
                    filter_unfollowed=True,
                    load_from="comments"
                )
                
                # End loop if max users reached
                if len(self.profile_links) >= self.max_follow:
                    break
                
        print (f"{len(self.profile_links)} users found")
                
        # Follow users
        self.__follow_like_users__ (follow_type="followed_advanced")
    
    def unfollow (self):
        """ Unfollow users """
        
        # Select users to unfollow
        unfollow_users = self.__get_unfollow_users__ () 
        
        # Unfollow each user
        for user in unfollow_users:
            
            # Load user page
            self.__set_page_wait__ (user)
            
            # Unfollow user
            unfollow_text = self.get_text (self.selectors["unfollow"])
            if unfollow_text.lower().strip() == "following":
                self.click_js (self.selectors["unfollow"])
                self.refresh_selenium ()
                
                # Confirm unfollow
                self.click_js (self.selectors["confirm_unfollow"])
                
                # Save user in history
                self.__save_user_history__ (user, "unfollowed")
                
                # Wait after unfollow
                self.__wait__ (f"user unfollowed: {user}")
            
            
    