"""Generate git diffs between branches suitable for Differential reviews."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_differ
#
# Public Classes:
#   NoDiffError
#   ReductionTechnique
#    .diff_size_utf8_bytes
#   LessContextReduction
#    .context_lines
#   RemoveContextReduction
#   DiffStatReduction
#
# Public Functions:
#   make_raw_diff
#
# Public Assignments:
#   DiffResult
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import collections

import phlgit_diff

import abdt_exception

_FULL_DIFF_CONTEXT_LINES = 100000
_GOOD_DIFF_CONTEXT_LINES = 1000
_SOME_DIFF_CONTEXT_LINES = 100

DiffResult = collections.namedtuple(
    'abdt_differ__DiffResult',
    [
        'diff',
        'reduction_list',
        'did_replace_unicode',
        'diff_size_utf8_bytes',
        'full_diff_size_utf8_bytes',
        'max_diff_size_utf8_bytes',
    ])


class NoDiffError(Exception):
    pass


class ReductionTechnique(object):

    """Base class for representing attempts to reduce diff size."""

    def __init__(self, diff_size_utf8_bytes):
        """Initialize.

        :diff_size_utf8_bytes: the size of the diff after attempting to reduce

        """
        self._diff_len = diff_size_utf8_bytes

    @property
    def diff_size_utf8_bytes(self):
        return self._diff_len


class LessContextReduction(ReductionTechnique):

    """Represent an attempt to reduce diff size by reducing context."""

    def __init__(self, diff_size_utf8_bytes, context_lines):
        """Initialize.

        :diff_size_utf8_bytes: the size of the diff after attempting to reduce
        :context_lines: the number of lines of context

        """
        ReductionTechnique.__init__(self, diff_size_utf8_bytes)
        self._context_lines = context_lines

    @property
    def context_lines(self):
        return self._context_lines


class RemoveContextReduction(ReductionTechnique):

    """Represent an attempt to reduce diff size by excluding context."""

    def __init__(self, diff_size_utf8_bytes):
        """Initialize.

        :diff_size_utf8_bytes: the size of the diff after attempting to reduce

        """
        ReductionTechnique.__init__(self, diff_size_utf8_bytes)


class DiffStatReduction(ReductionTechnique):

    """Represent an attempt to reduce diff size by reducing to diffstat."""

    def __init__(self, diff_size_utf8_bytes):
        """Initialize.

        :diff_size_utf8_bytes: the size of the diff after attempting to reduce

        """
        ReductionTechnique.__init__(self, diff_size_utf8_bytes)


def make_raw_diff(clone, base, branch, max_diff_size_utf8_bytes):
    """Return a string raw diff of the changes on 'branch'.

    If the diff would exceed the _MAX_DIFF_SIZE then take measures
    to reduce the diff size by reducing the amount of context.

    Raise 'NoDiffError' if the diff could not be fit into
    'max_bytes'.

    :clone: supports 'call'
    :base: string name of the merge-base of 'branch'
    :branch: string name of the branch to diff
    :max_diff_size_utf8_bytes: the maximum allowed size of the diff as utf8
    :returns: the string diff of the changes on the branch

    """
    raw_diff = phlgit_diff.raw_diff_range(
        clone, base, branch, _FULL_DIFF_CONTEXT_LINES)
    new_raw_diff = unicode(raw_diff, errors='replace')
    full_diff_size_utf8_bytes = len(new_raw_diff.encode("utf-8"))
    diff_size_utf8_bytes = full_diff_size_utf8_bytes

    if not raw_diff:
        raise NoDiffError()

    reduction_list = []

    # TODO: detect generated files and try less context on just those first
    # TODO: detect generated files and try no context on just those first
    # TODO: detect generated files and try excluding those first

    # if the diff is too big then regen with less context
    for context_lines in [_GOOD_DIFF_CONTEXT_LINES, _SOME_DIFF_CONTEXT_LINES]:
        if diff_size_utf8_bytes > max_diff_size_utf8_bytes:
            raw_diff = phlgit_diff.raw_diff_range(
                clone, base, branch, context_lines)
            new_raw_diff = unicode(raw_diff, errors='replace')
            diff_size_utf8_bytes = len(new_raw_diff.encode("utf-8"))
            reduction_list.append(
                LessContextReduction(
                    diff_size_utf8_bytes,
                    context_lines))

    # if the diff is still too big then regen with no context
    if diff_size_utf8_bytes > max_diff_size_utf8_bytes:
        raw_diff = phlgit_diff.raw_diff_range(clone, base, branch, None)
        new_raw_diff = unicode(raw_diff, errors='replace')
        diff_size_utf8_bytes = len(new_raw_diff.encode("utf-8"))
        reduction_list.append(
            RemoveContextReduction(
                diff_size_utf8_bytes))

    # if the diff is still too big then just use the diff stat with message
    if diff_size_utf8_bytes > max_diff_size_utf8_bytes:
        stat = phlgit_diff.stat_range(clone, base, branch)
        content = "this diff is very large, it has been reduced to a summary:"
        content = '\n\n'.join([content, stat])
        raw_diff = phlgit_diff.create_add_file('diffstat', content)
        new_raw_diff = unicode(raw_diff, errors='replace')
        diff_size_utf8_bytes = len(new_raw_diff.encode("utf-8"))
        reduction_list.append(
            DiffStatReduction(
                diff_size_utf8_bytes))

    # if the diff is still too big then error
    if diff_size_utf8_bytes > max_diff_size_utf8_bytes:
        raise abdt_exception.LargeDiffException(
            "diff too big", diff_size_utf8_bytes, max_diff_size_utf8_bytes)

    did_replace_unicode = new_raw_diff != raw_diff

    return DiffResult(
        new_raw_diff,
        reduction_list,
        did_replace_unicode,
        diff_size_utf8_bytes,
        full_diff_size_utf8_bytes,
        max_diff_size_utf8_bytes)


#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
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
