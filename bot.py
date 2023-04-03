import os
import csv
import time
import random
import config
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
        self.profile_links = []
        
        # Css selectors
        self.selectors = {
            "user": 'input[autocomplete="username"]',
            "user_next": '.css-1dbjc4n.r-mk0yit + div[role="button"][tabindex="0"]',
            "password": 'input[autocomplete="current-password"]',
            "login": '.css-1dbjc4n.r-pw2am6 > [role="button"]',
            "followers_down": 'main',
            "followers_links": '[aria-label="Timeline: Followers"] [data-testid="cellInnerDiv"] a[role="link"]', 
        }
    
        # Start chrome
        super ().__init__ (headless=self.headless, chrome_folder=self.chrome_folder, start_killing=True)
        
        # Auto login
        self.__login__ ()
        
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
        
        history_file = os.path.join (os.path.dirname (__file__), "history.csv")
        with open (history_file, "r") as file:
            csv_reader = csv.reader (file)
            history = list (csv_reader)
            
        followed_classic = list(map(lambda row: row[0], filter(lambda row: row[1] == "followed_classic", history)))
        followed_advanced = list(map(lambda row: row[0], filter(lambda row: row[1] == "followed_advanced", history)))
        unfollowed = list(map(lambda row: row[0], filter(lambda row: row[1] == "unfollowed", history)))
        history_rows = list(map(lambda row: row[0], history))
        
        return followed_classic, followed_advanced, unfollowed, history_rows
            
    def __login__ (self):
        """ Login to twitter with user and password
        """
        
        # Set login page
        self.set_page ("https://twitter.com/")
        
        # # Write user name
        # self.send_data (self.selectors["user"], self.user)
        # self.click_js (self.selectors["user_next"])
        # time.sleep (2)
        # self.refresh_selenium ()
        
        # # Write password
        # self.send_data (self.selectors["password"], self.password)
        # time.sleep (1)
        # self.refresh_selenium ()
        # self.click_js (self.selectors["login"])
        
        input ("Running.\nPress enter to continue...")        
    
    def __wait__ (self, message:str=""):
        """ Wait time and show message

        Args:
            message (str, optional): message to show after wait time. Defaults to "".
        """
        
        time.sleep (random.randint(30, 180))
        if message:
            print (message)
    
    def __load_links__ (self, selector_link:str, load_more_selector:str="", filter_advanced:bool=False, 
                       filter_classic:bool=False, filter_unfollowed:bool=False): 
        """ Extract links from specific selects, and go down in the page for load the next links
        Save links in "profile_links" attribute

        Args:
            selector_link (str): css selector for profile links
            load_more_selector (str, optional): element to click for load more results. Defaults to "".
            filter_advanced (bool, optional): skip users already followed with the advanced bot. Defaults to False.
            filter_classic (bool, optional): skip users already followed with the classic bot. Defaults to False.
            filter_unfollowed (bool, optional): skip users already unfollowed. Defaults to False.
        """
        
                
        print ("\tGetting user profiles...")
        
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
            self.refresh_selenium()
            time.sleep(3)
            links = self.get_attribs(selector_link, "href", allow_duplicates=False, allow_empty=False)
            
            # Break where no new links
            if links == last_links: 
                break
            else: 
                last_links = links
            
            # Validate each link
            for link in links: 
                
                # # Skip tag links
                # if "explore/tags" in link: 
                #     continue
                
                if link not in skip_users: 
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
    
    def __set_user__ (self, profile_link:str):
        """ Open profile page of specific user """
        
        self.set_page (profile_link)
    
    def __follow_user__ (self):
        """ Follow current user """
        pass
    
    def __like_posts__ (self, post_num:int=3):
        """ Like specific number of posts of the current user

        Args:
            post_num (int, optional): Post to like. Defaults to 3.
        """
        pass
    
    def __unfollow_user__ (self):
        """ Unfollow current user """
        
    def __follow_like_users__ (self):
        """ Follow and like posts of users from a profile_links """
    
    def follow_classic (self):
        """ Follow users from current followers list of an specific users
        """
        
        # Loop each user
        for user in self.list_follow:
                        
            print (f"getting users from followers list {user}...")
            
            # Show followers page 
            url = f"https://twitter.com/{user}/followers"
            self.set_page (url)
                    
            # Go down and get links
            self.__load_links__ (
                self.selectors["followers_links"], 
                filter_classic=True,
                filter_unfollowed=True,
            )
            
            print (f"{len(self.profile_links)} users found")
        
        # Follow users
    
    def follow_advanced (self):
        pass
    
    def unfollow (self):
        pass
    
    