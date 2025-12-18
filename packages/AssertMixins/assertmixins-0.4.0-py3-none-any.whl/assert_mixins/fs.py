# -*- coding: utf-8 -*-
import os

class FsMixin:
    """
    Filesystem-related assertions.
    """
    
    def assertLooksLikePath(self, path, iserr=None):
        """
        Asserts() that a given value represents something that looks like a path.
        """
        if isinstance(path, str):
            return
        if iserr:
            raise iserr[0](f"Function {iserr[1]}() was called with the non-string «{repr(path)}».")
        else:
            raise AssertionError(f"Value «{repr(path)}» does not look like a path.")
    
    def assertPathExists(self, path, msg=None):
        """
        Asserts() that a given value represents the path of an existing directory entry.
        """
        self.assertLooksLikePath(path, iserr=(ValueError, "assertPathExists"))
        self.assertTrue(os.path.exists(path), msg=msg or f"Path «{path}» does not exist.")
    
    def assertPathNotExists(self, path, msg=None):
        """
        Asserts() that a given value represents the path of a non-existing directory entry.
        """
        self.assertLooksLikePath(path, iserr=(ValueError, "assertPathNotExists"))
        self.assertFalse(os.path.exists(path), msg=msg or f"Path «{path}» exists.")
    
    def assertIsFile(self, path, msg=None):
        """
        Asserts() that a given value represents the path of a regular file.
        """
        self.assertLooksLikePath(path, iserr=(ValueError, "assertIsFile"))
        self.assertTrue(os.path.exists(path), msg=msg or f"Path «{path}» does not even exist.")
        self.assertTrue(os.path.isfile(path), msg=msg or f"Path «{path}» is not a regular file!")
    
    def assertIsDirectory(self, path, msg=None):
        """
        Asserts() that a given value represents the path of a directory.
        """
        self.assertLooksLikePath(path, iserr=(ValueError, "assertIsDirectory"))
        self.assertTrue(os.path.exists(path), msg=msg or f"Path «{path}» does not even exist.")
        self.assertTrue(os.path.isdir(path), msg=msg or f"Path «{path}» is not a directory!")
