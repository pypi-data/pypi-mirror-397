"""Create markdown links."""

from typing import Optional
from urllib.parse import urlparse
import re

class MDLink:
    """Class for creating different kinds of links."""

    def __init__(self, linktext:str, url:str , title: Optional[str], linkname: str | int = 1):
        self.linktext = linktext
        self.url = url
        self.title = title
        self.linkname = linkname

    def create_inline_link(self) -> str:
        """
        Create inline link.
        
        An inline link is defined as:

        \[linktext](url)
        """

        # Check if title is set. If so return markdown link without title.
        if self.title == "" or self.title == None:
            
            return "[" + self.linktext + "]" + "(" + self.url + ")"
            
        return "[" + self.linktext + "]" + "(" + self.url + " " + '"' + self.title + '"' + ")"
    
    def create_reference_link(self) -> str:
        """
        Create reference link.

        \[linktext][linkname]
        
        \[linkname]: [url]
        """

        if self.linkname == "" or self.linkname == None:
            return _create_reference_text_name(self.linktext, self.linkname) + "\n" + "\n" + _create_reference_name_url(self.linktext, self.url, self.title)
        
        # Check if title is set. If so return markdown link with title.
        if not self.title == "" or not self.title == None:
            return _create_reference_text_name(self.linktext, self.linkname) + "\n" + "\n" + _create_reference_name_url(self.linkname, self.url, self.title)

        return _create_reference_text_name(self.linktext, self.linkname) + "\n" + "\n" + _create_reference_name_url(self.linkname, self.url)

def create_automatic_link(string: str) -> str:
    """
    Create an automatic link.

    Shows the actual text of a link or email and make it clickable.

    <url/email>
    """
    
    # Check if it is valid url or mail.
    mailpattern = r'^[A-Za-z0-9]+[\._]?[A-Za-z0-9]+[@]\w+[.]\w+$'
    
    if string.startswith("http:") or string.startswith("https:"):
        return "<" + urlparse(string).geturl() + ">"
    
    elif re.match(mailpattern, string):
        return "<" + string + ">"
    
    else:
        raise ValueError(f"Need valid url or email got <{string}>.")

def _create_reference_text_name(linktext:str, linkname: str) -> str:
    """
    Create a reference to the given link.
    
    A reference looks like this:

    \[linktext][linkname]    
    """

    return "[" + linktext + "]" + "[" + str(linkname) + "]"

def _create_reference_name_url(linkname:str, url: str, title:str = "") -> str:
    """
    Create the link to the given reference.
    
    \[linkname]: [url]
    """

    # Check if title is set. If so return markdown link with title.
    if title == "" or title == None:
        return "[" + str(linkname) + "]" + ":" + " " + url
    
    return "[" + str(linkname) + "]" + ":" + " " + url + " " + "(" + title + ")"