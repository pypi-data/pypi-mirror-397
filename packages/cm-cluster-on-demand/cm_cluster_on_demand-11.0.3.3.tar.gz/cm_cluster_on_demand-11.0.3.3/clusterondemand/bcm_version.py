# Copyright (c) 2004-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import re
from functools import total_ordering
from typing import Any

VERSION_PATTERN = r'^(?P<major>\d+)\.(?P<minor>\d+)(-(?P<suffix>dev|rc))?$'


@total_ordering
class BcmVersion:
    """A utility class for comparing Base Command Manager versions.

    Wraps a version number string and handles comparison logic.

    Hard-coded assumption: Once we start working on BCM with major version X, then we
    will never release another minor version of a major X-1. That is: there will never be a release
    of something like 8.4 if 9.0 has been released (even internally).

    The comparison is based on the order in which versions appear during the development cycle, so:
    9.0 < 10.0-dev < 10.0-rc < 10.0

    """
    @classmethod
    def _wrap_with_instance(cls, obj: BcmVersion | str) -> BcmVersion:
        return obj if isinstance(obj, cls) else cls(obj)  # type: ignore

    def __init__(self, string: str) -> None:
        self.string: str = string
        self.major: int = 0
        self.minor: int = 0
        self.suffix: int = 0  # stored as integer for easy comparison, see below

        if "trunk" == string:
            self.major = self.minor = 1000000  # store trunk as high number so it always wins in comparisons
            return

        if (match := re.match(VERSION_PATTERN, string)) is None:
            raise ValueError(f"The value '{string}' is not a valid BCM version. "
                             "It should match '\\d+\\.\\d+(-(dev|rc))?'. E.g. '10.0', '10.0-dev'.")

        self.major = int(match.group("major"))
        self.minor = int(match.group("minor"))
        if not match.group("suffix"):
            self.suffix = 2  # there was no suffix, so this is a public release like 10.0, store as highest value
        elif match.group("suffix") == "rc":
            self.suffix = 1  # release candidate comes before public release
        elif match.group("suffix") == "dev":
            self.suffix = 0  # dev version before release candidate

    def __str__(self) -> str:
        return self.string

    def __eq__(self, other: Any) -> bool:
        other = self.__class__._wrap_with_instance(other)
        return (
            (self.major, self.minor, self.suffix)
            == (other.major, other.minor, other.suffix)
        )

    def __gt__(self, other: BcmVersion | str) -> bool:
        other = self.__class__._wrap_with_instance(other)
        return (
            (self.major, self.minor, self.suffix)
            > (other.major, other.minor, other.suffix)
        )

    """ Can be used for comparison when we don't care about suffix.
    For example: version.release > (10, 0)
    Note, when version is trunk it returns (1000000, 1000000) so that trunk is always the highest version"""
    @property
    def release(self) -> tuple[int, int]:
        return (self.major, self.minor)
