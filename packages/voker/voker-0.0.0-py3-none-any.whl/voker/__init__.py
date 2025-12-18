# Copyright 2025 Invoke Labs, Inc.
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

"""TODO."""

from .client import VokerClient
from .schema import (
    AgentVersionId,
    CreateEventPayload,
    CreatePersonPayload,
    EventId,
    EventProperties,
    PersonId,
    UpdatePersonPayload,
)

__all__ = [
    "AgentVersionId",
    "CreateEventPayload",
    "CreatePersonPayload",
    "EventId",
    "EventProperties",
    "PersonId",
    "UpdatePersonPayload",
    "VokerClient",
]


def __clean_module_refs() -> None:
    locals_ = locals()

    for name in __all__:
        try:
            locals_[name].__module__ = "voker"
        except (TypeError, AttributeError):
            ...


__clean_module_refs()
