import os
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
        
    def __set_user__ (self, user:str):
        """ Load user proffile page 

        Args:
            user (str): user name
        """
        
        url = f"https://twitter.com/{user}"
        self.set_page (url)
    
    def __wait__ (self, message:str=""):
        time.sleep (random.randint(30, 180))
        if message:
            print (message)
    
    def __get_links__ (self, selector_link, load_more_selector="", scroll_by=0): 
        """
        Extract links from specific selects, and go down in the page for load the next links
        Save links in class variable "profile_links"
        """
                
        print ("\tGetting links...")
        
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
                
                if link not in self.followed_list and link not in self.profile_links: 
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
            self.__get_links__ (
                self.selectors["followers_links"], 
                scroll_by=5000
            )
    
    def follow_advanced (self):
        pass
    
    def unfollow (self):
        pass
    
    