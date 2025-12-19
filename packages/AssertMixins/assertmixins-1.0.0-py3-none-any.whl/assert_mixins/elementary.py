# -*- coding: utf-8 -*-

class ElementaryMixin:
    """
    Elementary assertions, meaning:
     * Based on standard unittest assertions;
     * Or delivering better reporting;
     * Or with more generality.
    """
    
    def assertLength(self, collection, length, msg=None):
        """
        Asserts that a collection has a given length.
            self        (Same meaning as in other assertions.)
            collection  A collection whose length is to be asserted about.
            length      The expected length.
            msg         (Same meaning as in other assertions.)
        """
        self.assertEqual(len(collection), length, msg=msg or f"Collection length is not {length}: {collection}")
    
    def assertEmpty(self, collection, msg=None):
        """
        Asserts that a collection is empty.
            self        (Same meaning as in other assertions.)
            collection  A collection that is being asserted to be empty.
            msg         (Same meaning as in other assertions.)
        """
        self.assertLength(collection, 0, msg=msg or f"Collection is not empty: {collection}")
    
    def assertSingleton(self, collection, msg=None):
        """
        Asserts that a collection has length one.
            self        (Same meaning as in other assertions.)
            collection  A collection that is being asserted to have a single element.
            msg         (Same meaning as in other assertions.)
        """
        self.assertLength(collection, 1, msg=msg or f"Collection is not a singleton: {collection}")
