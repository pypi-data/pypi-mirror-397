"""Testing the module with the python internal unittest module."""

import unittest

from src.pymarkdownroh import *

TESTS = {
    # Blockquoting the provided string.
    "BLOCKSTRING": ["This is a blockquote.","""This is a multiline
string."""],
    "BLOCKQUOTE_RESULT": ["> This is a blockquote.","""> This is a multiline
> string."""],

    # Emphasizing tests whole string.
    "EMPHASIZING": ["Test"],
    "BOLD_RESULTS": ["**Test**"],
    "ITALIC_RESULTS": ["*Test*"],
    "BOLDITALIC_RESULTS": ["***Test***"],
    # Emphasizing tests substring.
    "EMPHASIZING_SUB": ["Python is great."],
    # Tuple of (startposition, endposition, result).
    "BOLD_SUB_RESULTS": [(0, 6, "**Python** is great.")],
    "ITALIC_SUB_RESULTS": [(0, 6, "*Python* is great.")],
    "BOLDITALIC_SUB_RESULTS": [(0, 6, "***Python*** is great.")],

    "HORIZONTALRULE_RESULT": ["* * *"],

    # Headline tests.
    "HEADLINES": ["Title", "Lvl2 Headline", "Lvl3 Headline", "Lvl4 Headline", "Lvl5 Headline", "Lvl6 Headline"],
    "HEADLINE_RESULTS": ["# Title", "## Lvl2 Headline", "### Lvl3 Headline", "#### Lvl4 Headline", "##### Lvl5 Headline", "###### Lvl6 Headline"],

    # Link tests.
    # list[tuple(linktext, url, linktitle)]
    "INLINE_LINKS": [("An Example","www.example.com","Example Title"),
                     ("An Example","www.example.com", "")],
    "INLINE_LINKS_RESULTS": ["[An Example](www.example.com \"Example Title\")",
                             "[An Example](www.example.com)"],
    "AUTOMATED_LINKS": ["http://www.example.com","example@example.com"],
    "AUTOMATED_LINKS_RESULTS": ["<http://www.example.com>", "<example@example.com>"],
    # list[tuple(linktext, linkname, url, linktitle)]
    "REFERENCE_LINKS": [("Link Text","Link Name","www.example.com","Link Title"),
                        ("Link Text2","Link Name2","www.example.com","")],
    "REFERENCE_LINKS_RESULTS": ["[Link Text][Link Name]\n\n[Link Name]: www.example.com (Link Title)",
                                "[Link Text2][Link Name2]\n\n[Link Name2]: www.example.com"],

    # Image tests.
    # list[tuple(linktext, url, linktitle)]
    "INLINE_IMAGES": [("Example Image","/examples/TestScreenshot.png","Example Image"),
                      ("Example Image","/examples/TestScreenshot.png","")],
    "INLINE_IMAGES_RESULT": ["![Example Image](/examples/TestScreenshot.png \"Example Image\")",
                             "![Example Image](/examples/TestScreenshot.png)"],
    # list[tuple(linktext, linkname, url, linktitle)]
    "REFERENCE_IMAGES": [("Example Image","Image Name","/examples/TestScreenshot.png","Example Image"),
                         ("Example Image","Image Name2","/examples/TestScreenshot.png","")],
    "REFERENCE_IMAGES_RESULTS": ["![Example Image][Image Name]\n\n[Image Name]: /examples/TestScreenshot.png (Example Image)",
                                 "![Example Image][Image Name2]\n\n[Image Name2]: /examples/TestScreenshot.png"],
    # Codespan tests.
    # list[(string, start, end, word)]
    "CODESPAN:": [("Use the printf() function.",0,1000,"printf()"),
                  ("Use the printf() function.",8,14,None)],
    "CODESPAN_RESULTS": ["Use the `printf()` function.",
                         "Use the `printf`() function."],

    # List tests.
    # List[tuple(input, ordered, checklist)]
    "LISTS": [
    (["Apples", "Bananas", "Cherries"], False, False),
    
    ([{"Programming Languages": ["Python", "JavaScript", "Rust"],
    "Databases": ["PostgreSQL", "MongoDB"]}],True, False),
    
    ([("Install Python", True),
    ("Set up virtualenv", False),
    {"Project Setup": [
        ("Create repo", True),
        ("Write README", False)
    ]},
    ("Push to GitHub", False)], False, True),

    ([("Book flights", False),
    ("Reserve hotel", True),
    {"Packing": [
        ("Clothes", False),
        ("Toiletries", True),
        ("Laptop", False)
    ]},
    ("Check-in online", False)],True, True),

    ],
    "LISTS_RESULT": ["- Apples\n- Bananas\n- Cherries",
                     "1. Programming Languages\n    1. Python\n    1. JavaScript\n    1. Rust\n1. Databases\n    1. PostgreSQL\n    1. MongoDB",
                     "- [x] Install Python\n- [ ] Set up virtualenv\n- [ ] Project Setup\n    - [x] Create repo\n    - [ ] Write README\n- [ ] Push to GitHub",
                     "1. [ ] Book flights\n1. [x] Reserve hotel\n1. [ ] Packing\n    1. [ ] Clothes\n    1. [x] Toiletries\n    1. [ ] Laptop\n1. [ ] Check-in online",
    ]
    }

EXAMPLEFILES = {
    "BLOCKQUOTES": "./examples/BLOCKQUOTES.md",
    "CODESPAN": "./examples/CODESPAN.md",
    "EMPHASIZING": "./examples/EMPHASIZE.md",
    "HEADLINES": "./examples/HEADLINES.md",
    "IMAGES": "./examples/IMAGES.md",
    "LINKS": "./examples/LINKS.md",
    "LISTS": "./example/LISTS.md"
    # "TABLES": "./examples/TABLES.md"
}

class TestPymarkdownroh_Emphasizing(unittest.TestCase):
    """Test emphasizing of pymarkdownroh module.."""

    def setUp(self):
        self.tests = TESTS

    def test_bold_emphasizing(self):
        for i in range(len(TESTS["EMPHASIZING"])):
            testobj = MDFormat(string=TESTS["EMPHASIZING"][i])
            self.assertEqual(testobj.write_bold(), TESTS["BOLD_RESULTS"][i])

    def test_italic_emphasizing(self):
        for i in range(len(TESTS["EMPHASIZING"])):
            testobj = MDFormat(string=TESTS["EMPHASIZING"][i])
            self.assertEqual(testobj.write_italic(), TESTS["ITALIC_RESULTS"][i])

    def test_bold_italic_emphasizing(self):
        for i in range(len(TESTS["EMPHASIZING"])):
            testobj = MDFormat(string=TESTS["EMPHASIZING"][i])
            self.assertEqual(testobj.write_bold_italic(), TESTS["BOLDITALIC_RESULTS"][i])

    def test_bold_emphasizing_substring(self):
        for i in range(len(TESTS["EMPHASIZING_SUB"])):
            testobj = MDFormat(TESTS["EMPHASIZING_SUB"][i], TESTS["BOLD_SUB_RESULTS"][i][0], TESTS["BOLD_SUB_RESULTS"][i][1])
            self.assertEqual(testobj.write_bold(), TESTS["BOLD_SUB_RESULTS"][i][2])
    
    def test_bold_emphasizing_substring(self):
        for i in range(len(TESTS["EMPHASIZING_SUB"])):
            testobj = MDFormat(TESTS["EMPHASIZING_SUB"][i], TESTS["ITALIC_SUB_RESULTS"][i][0], TESTS["ITALIC_SUB_RESULTS"][i][1])
            self.assertEqual(testobj.write_italic(), TESTS["ITALIC_SUB_RESULTS"][i][2])

    def test_bold_emphasizing_substring(self):
        for i in range(len(TESTS["EMPHASIZING_SUB"])):
            testobj = MDFormat(TESTS["EMPHASIZING_SUB"][i], TESTS["BOLDITALIC_SUB_RESULTS"][i][0], TESTS["BOLDITALIC_SUB_RESULTS"][i][1])
            self.assertEqual(testobj.write_bold_italic(), TESTS["BOLDITALIC_SUB_RESULTS"][i][2])

    def test_horizontal_rule(self):
        for i in range(len(TESTS["HORIZONTALRULE_RESULT"])):
            self.assertEqual(MDFormat.create_horizontal_rule(), TESTS["HORIZONTALRULE_RESULT"][i])

class TestPymarkdownroh_Headlines(unittest.TestCase):
    """Test headline and title creation of pymarkdownroh module."""

    def setUp(self):
        self.tests = TESTS

    def test_headline(self):
        for i in range(len(TESTS["HEADLINES"])):
            # Create with i +1 because the lsit starts counting by zero but a headline must have one #.
            self.assertEqual(create_headline(i +1, TESTS["HEADLINES"][i]), TESTS["HEADLINE_RESULTS"][i])

            with open(EXAMPLEFILES["HEADLINES"], "w") as f:
                for i in range(len(TESTS["HEADLINES"])):
                    f.write(create_headline(i +1, TESTS["HEADLINES"][i]) + "\n")
    
class TestPymarkdownroh_Blockquotes(unittest.TestCase):
    """Test blockquote creation of pymarkdownroh module."""

    def setUp(self):
        self.tests = TESTS

    def test_blockquote(self):
        for i in range(len(TESTS["BLOCKSTRING"])):
            self.assertEqual(create_blockquote(TESTS["BLOCKSTRING"][i]), TESTS["BLOCKQUOTE_RESULT"][i])

class TestPymarkdownroh_Links(unittest.TestCase):
    """Test link creation of pymarkdownroh module."""

    def setUp(self):
        self.tests = TESTS

    def test_inline_link(self):
        for i in range(len(TESTS["INLINE_LINKS"])):
            link = MDLink(linktext= TESTS["INLINE_LINKS"][i][0], url= TESTS["INLINE_LINKS"][i][1], title= TESTS["INLINE_LINKS"][i][2])
            self.assertEqual(link.create_inline_link(), TESTS["INLINE_LINKS_RESULTS"][i])

        with open(EXAMPLEFILES["LINKS"], "w") as f:
            for i in range(len(TESTS["INLINE_LINKS"])):
                link = MDLink(linktext= TESTS["INLINE_LINKS"][i][0], url= TESTS["INLINE_LINKS"][i][1], title= TESTS["INLINE_LINKS"][i][2])
                f.write(link.create_inline_link() + "\n")
                f.write("\n")
            
    def test_reference_link(self):
        for i in range(len(TESTS["REFERENCE_LINKS"])):
            link = MDLink(linktext=TESTS["REFERENCE_LINKS"][i][0], linkname= TESTS["REFERENCE_LINKS"][i][1], url= TESTS["REFERENCE_LINKS"][i][2], title=TESTS["REFERENCE_LINKS"][i][3])
            self.assertEqual(link.create_reference_link(), TESTS["REFERENCE_LINKS_RESULTS"][i])
       
        with open(EXAMPLEFILES["LINKS"],"a") as f:
            for i in range(len(TESTS["REFERENCE_LINKS"])):
                link = MDLink(linktext=TESTS["REFERENCE_LINKS"][i][0], linkname= TESTS["REFERENCE_LINKS"][i][1], url= TESTS["REFERENCE_LINKS"][i][2], title=TESTS["REFERENCE_LINKS"][i][3])
                f.write(link.create_reference_link() + "\n")
                f.write("\n")

    def test_automated_link(self):
        for i in range(len(TESTS["AUTOMATED_LINKS"])):
            self.assertEqual(create_automatic_link(TESTS["AUTOMATED_LINKS"][i]), TESTS["AUTOMATED_LINKS_RESULTS"][i])

        # # Currently not appending strings to file. Unknown why, because file is writable.
        # with open(EXAMPLEFILES["LINKS"],"a") as f:
        #     for i in range(len(TESTS["AUTOMATED_LINKS"])):
        #         f.write(str(create_automatic_link(TESTS["AUTOMATED_LINKS"][i])) + "\n")
        #         f.write("\n")

class TestPymarkdownroh_Images(unittest.TestCase):
    """Test image link creation of pymarkdownroh module."""

    def setUp(self):
        self.tests = TESTS

    def test_inline_image_link(self):
        for i in range(len(TESTS["INLINE_IMAGES"])):
            image = MDImage(linktext= TESTS["INLINE_IMAGES"][i][0], url= TESTS["INLINE_IMAGES"][i][1], title= TESTS["INLINE_IMAGES"][i][2])
            self.assertEqual(image.create_inline_link(), TESTS["INLINE_IMAGES_RESULT"][i])

        with open(EXAMPLEFILES["IMAGES"], "w") as f:
            for i in range(len(TESTS["INLINE_IMAGES"])):
                image = MDImage(linktext= TESTS["INLINE_IMAGES"][i][0], url= TESTS["INLINE_IMAGES"][i][1], title= TESTS["INLINE_IMAGES"][i][2])
                f.write(image.create_inline_link() + "\n")
                f.write("\n")

    def test_reference_image_link(self):
        for i in range(len(TESTS["REFERENCE_IMAGES"])):
            image = MDImage(linktext= TESTS["REFERENCE_IMAGES"][i][0], linkname= TESTS["REFERENCE_IMAGES"][i][1], url= TESTS["REFERENCE_IMAGES"][i][2], title= TESTS["REFERENCE_IMAGES"][i][3])
            self.assertEqual(image.create_reference_link(), TESTS["REFERENCE_IMAGES_RESULTS"][i])

        with open(EXAMPLEFILES["IMAGES"], "a") as f:
            for i in range(len(TESTS["REFERENCE_IMAGES"])):
                image = MDImage(linktext= TESTS["REFERENCE_IMAGES"][i][0], linkname= TESTS["REFERENCE_IMAGES"][i][1], url= TESTS["REFERENCE_IMAGES"][i][2], title= TESTS["REFERENCE_IMAGES"][i][3])
                f.write(image.create_reference_link() + "\n")
                f.write("\n")

class TestPymarkdownroh_CodeSpan(unittest.TestCase):
    """Test codespan of pymarkdownroh module.."""

    def setUp(self):
        self.tests = TESTS

    def test_codespan_word(self):
        for i in range(len(TESTS["CODESPAN:"])):
            # print(create_code_span(string= TESTS["CODESPAN:"][i][0], start= TESTS["CODESPAN:"][i][1], end= TESTS["CODESPAN:"][i][2], word= TESTS["CODESPAN:"][i][3]))
            self.assertEqual(create_code_span(string= TESTS["CODESPAN:"][i][0], start= TESTS["CODESPAN:"][i][1], end= TESTS["CODESPAN:"][i][2], word= TESTS["CODESPAN:"][i][3]), TESTS["CODESPAN_RESULTS"][i])

        with open(EXAMPLEFILES["CODESPAN"], "w") as f:
            for i in range(len(TESTS["CODESPAN:"])):
                f.write(create_code_span(string= TESTS["CODESPAN:"][i][0], start= TESTS["CODESPAN:"][i][1], end= TESTS["CODESPAN:"][i][2], word= TESTS["CODESPAN:"][i][3]) + "\n")
                f.write("\n")

class TestPymarkdownroh_Lists(unittest.TestCase):
    """Test lists of pymarkdownroh module.."""

    def setUp(self):
        self.tests = TESTS

    def test_list(self):
        for i in range(len(TESTS["LISTS"])):
            if TESTS["LISTS"][i][1] == True and TESTS["LISTS"][i][2] == False :
                self.assertEqual(create_list(TESTS["LISTS"][i][0],ordered=True), TESTS["LISTS_RESULT"][i])
            elif TESTS["LISTS"][i][1] == False and TESTS["LISTS"][i][2] == True:
                self.assertEqual(create_list(TESTS["LISTS"][i][0],checklist=True), TESTS["LISTS_RESULT"][i])
            elif TESTS["LISTS"][i][1] == True and TESTS["LISTS"][i][2] == True:
                self.assertEqual(create_list(TESTS["LISTS"][i][0],ordered=True, checklist=True), TESTS["LISTS_RESULT"][i])        
            else:
                self.assertEqual(create_list(TESTS["LISTS"][i][0]), TESTS["LISTS_RESULT"][i])


if __name__ == '__main__':
    # Verbose unittests.
    unittest.main(verbosity=2)