"""Fixtures for exercising scenarios with real Git."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlgitu_fixture
#
# Public Classes:
#   TempRepo
#    .close
#    .repo
#   Worker
#    .create_new_file
#    .add_new_file
#    .commit_new_file
#    .commit_new_file_on_new_branch
#    .append_to_file
#    .add_append_to_file
#    .commit_append_to_file
#    .append_to_file_on_new_branch
#    .checkout_master
#    .repo
#
# Public Functions:
#   lone_worker_context
#   temprepo_context
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import contextlib
import os
import shutil
import tempfile

import phlsys_git


@contextlib.contextmanager
def lone_worker_context():
    """Return a newly attached Worker with initial commit, close when expired.

    Usage examples:

        Create a temporary repo and attached worker:
        >>> with lone_worker_context() as worker:
        ...     content = worker.repo.call("show", "HEAD:README")
        ...     content is not None
        True

    """
    with temprepo_context() as repo:
        worker = Worker(repo)
        worker.commit_new_file('initial commit', 'README')
        yield worker


@contextlib.contextmanager
def temprepo_context():
    """Return a newly created phlsys_git.Repo, close when expired.

    Usage examples:

        Create a temporary repo:
        >>> with temprepo_context() as clone:
        ...     status = clone.call("rev-parse", "--is-inside-work-tree")
        ...     status.strip().lower() == 'true'
        True

    """
    with contextlib.closing(TempRepo()) as temp_repo:
        yield temp_repo.repo


class TempRepo(object):

    """Make a temporary repository, clean up on close().

    Usage examples:

        Create a temporary repo:
        >>> with temprepo_context() as repo:
        ...     status = repo.call("rev-parse", "--is-inside-work-tree")
        ...     status.strip().lower() == 'true'
        True

    """

    def __init__(self):
        super(TempRepo, self).__init__()
        self._tmp_dir = tempfile.mkdtemp()
        self._repo = phlsys_git.Repo(self._tmp_dir)
        self._repo.call("init")

    def close(self):
        """Free up any resources used by this instance.

        Note that you must call this function to prevent leaks, it's best to
        use the supplied 'temprepo_context' if possible to guarantee closing.

        :returns: None

        """
        shutil.rmtree(self._tmp_dir)

    @property
    def repo(self):
        return self._repo


class Worker(object):

    """Attach to a git repo and support actions that a worker might do."""

    def __init__(self, repo):
        super(Worker, self).__init__()
        self._repo = repo

    def create_new_file(self, relative_path, contents=None):
        """Create a new file in the working tree.

        :relative_path: the path of the file, relative to the repo
        :contents: the string contents of the new file
        :returns: None

        """
        path = os.path.join(
            self._repo.working_dir,
            relative_path)

        with open(path, 'w') as f:
            if contents:
                f.write(contents)

    def add_new_file(self, relative_path, contents=None):
        """Create a new file in the working tree and index.

        :relative_path: the path of the file, relative to the repo
        :contents: the string contents of the new file
        :returns: None

        """
        self.create_new_file(relative_path, contents)
        self._repo.call('add', relative_path)

    def commit_new_file(self, message, relative_path, contents=None):
        """Create and commit a new file.

        :message: the string content of the commit message
        :relative_path: the path of the file, relative to the repo
        :contents: the string contents of the new file
        :returns: None

        """
        self.add_new_file(relative_path, contents)
        self._repo.call('commit', '-m', message, '--', relative_path)

    def commit_new_file_on_new_branch(
            self, branch, message, relative_path, contents=None, base=None):
        """Checkout a new branch and create and commit a new file.

        :branch: the string name of the new branch
        :message: the string content of the commit message
        :relative_path: the path of the file, relative to the repo
        :contents: the string contents of the new file
        :base: the string name of the branch to base off of or None for HEAD
        :returns: None

        """
        base_ref = base if base is not None else 'HEAD'
        self._repo.call('checkout', '-b', branch, base_ref)
        self.commit_new_file(message, relative_path, contents)

    def append_to_file(self, relative_path, to_append):
        """Append to a file in the working tree.

        :relative_path: the path of the file, relative to the repo
        :to_append: the string contents to append to the file
        :returns: None

        """
        path = os.path.join(
            self._repo.working_dir,
            relative_path)

        with open(path, 'a') as f:
            f.write(to_append)

    def add_append_to_file(self, relative_path, to_append):
        """Create a new file in the working tree and index.

        :relative_path: the path of the file, relative to the repo
        :to_append: the string contents to append to the file
        :returns: None

        """
        self.append_to_file(relative_path, to_append)
        self._repo.call('add', relative_path)

    def commit_append_to_file(self, message, relative_path, to_append):
        """Create and commit a new file.

        :message: the string content of the commit message
        :relative_path: the path of the file, relative to the repo
        :to_append: the string contents to append to the file
        :returns: None

        """
        self.add_append_to_file(relative_path, to_append)
        self._repo.call('commit', '-m', message, '--', relative_path)

    def append_to_file_on_new_branch(
            self, branch, message, relative_path, to_append, base=None):
        """Checkout a new branch and commit an append to a file.

        :branch: the string name of the new branch
        :message: the string content of the commit message
        :relative_path: the path of the file, relative to the repo
        :to_append: the string contents to append to the file
        :base: the string name of the branch to base off of or None for HEAD
        :returns: None

        """
        base_ref = base if base is not None else 'HEAD'
        self._repo.call('checkout', '-b', branch, base_ref)
        self.commit_append_to_file(message, relative_path, to_append)

    def checkout_master(self):
        """Checkout the 'master' branch."""
        self._repo.call('checkout', 'master')

    @property
    def repo(self):
        return self._repo


# class CentralisedWithContributors(object):
#
#     def __init__(self, contributor_count=2):
#         super(CentralisedTwoContributors, self).__init__()
#
#         self.central = phlsys_git.GitClone(tempfile.mkdtemp())
#         self.contributors = []
#         for
#         self.alpha = phlsys_git.GitClone(tempfile.mkdtemp())
#         self.beta = phlsys_git.GitClone(tempfile.mkdtemp())
#         sys_clone = phlsys_git.GitClone(tempfile.mkdtemp())


#------------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------- END-OF-FILE ----------------------------------
