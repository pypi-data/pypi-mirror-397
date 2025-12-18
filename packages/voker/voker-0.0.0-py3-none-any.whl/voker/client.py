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

from __future__ import annotations

import os
from typing import Optional

import requests

from .api import ApiClient, EventQueue, EventWorker
from .schema import (
    CreateEventPayload,
    CreatePersonPayload,
    PersonId,
    UpdatePersonPayload,
)


# this just adds the request to the queue to call the api in the background
class VokerClient:
    """TODO."""

    def __init__(
        self,
        *,
        base_url: str = "evals.voker.ai",
        api_key: Optional[str] = None,
    ) -> None:
        self._api_client = ApiClient(base_url=base_url, api_key=api_key)
        self._queue = EventQueue()
        self._event_worker = EventWorker(self._api_client, self._queue)

    @property
    def events(self) -> VokerClient_Events:
        """TODO."""
        return VokerClient_Events(self._queue)

    @property
    def people(self) -> VokerClient_People:
        """TODO."""
        return VokerClient_People(self._queue)

    @property
    def groups(self) -> VokerClient_Groups:
        """TODO."""
        return VokerClient_Groups(self._queue)

    def close(self) -> None:
        """TODO."""
        self._event_worker.close()


class VokerClient_BaseSubPath:
    """TODO."""

    def __init__(self, queue: EventQueue) -> None:
        self._queue = queue


class VokerClient_Events(VokerClient_BaseSubPath):
    """TODO."""

    def create(self, payload: CreateEventPayload) -> None:
        """Create a new event.

        asd
        ---
        a: b
        a: c
        """
        # TODO: requests or httpx?

        req = requests.post(
            "http://localhost:8080/api/v1/events",
            json=payload,
        )

        req.raise_for_status()

        # with Client(base_url=self._base_url) as client:
        #     if self._api_key is not None:
        #         client.headers.update({"Authorization": f"Bearer {self._api_key}"})

        #     response = client.post("/api/v1/events", json=payload)
        #     response.raise_for_status()
        self._queue.put()


class VokerClient_People(VokerClient_BaseSubPath):
    """TODO."""

    def get(self) -> None:
        """TODO."""
        self._queue.put()

    def create(self, payload: CreatePersonPayload) -> None:
        """Create a new person.

        TODO:
        """
        # TODO: requests or httpx?

        req = requests.put(
            "http://localhost:8080/api/v1/people",
            json=payload,
        )

        req.raise_for_status()

        # with Client(base_url=self._base_url) as client:
        #     if self._api_key is not None:
        #         client.headers.update({"Authorization": f"Bearer {self._api_key}"})

        #     response = client.post("/api/v1/people", json=payload)
        #     response.raise_for_status()
        self._queue.put()

    def update(
        self,
        person_id: PersonId,
        payload: UpdatePersonPayload,
    ) -> None:
        """Updates a person.

        TODO:
        """
        # TODO: requests or httpx?

        req = requests.put(
            f"http://localhost:8080/api/v1/people/{person_id}",
            json=payload,
        )

        req.raise_for_status()

        # with Client(base_url=self._base_url) as client:
        #     if self._api_key is not None:
        #         client.headers.update({"Authorization": f"Bearer {self._api_key}"})

        #     response = client.put(f"/api/v1/people/{person_id}", json=payload)
        #     response.raise_for_status()
        self._queue.put()

    def delete(
        self,
        person_id: PersonId,
    ) -> None:
        """Deletes a person.

        TODO:
        """
        # TODO: requests or httpx?

        req = requests.delete(f"http://localhost:8080/api/v1/people/{person_id}")

        req.raise_for_status()

        # with Client(base_url=self._base_url) as client:
        #     if self._api_key is not None:
        #         client.headers.update({"Authorization": f"Bearer {self._api_key}"})

        #     response = client.delete(f"/api/v1/people/{person_id}")
        #     response.raise_for_status()
        self._queue.put()

    def add_to_group(self) -> None:
        """TODO."""
        self._queue.put()

    def remove_from_group(self) -> None:
        """TODO."""
        self._queue.put()

    def list_groups(self) -> None:
        """TODO."""
        self._queue.put()


class VokerClient_Groups(VokerClient_BaseSubPath):
    """TODO."""

    def list(self) -> None:
        """TODO."""
        self._queue.put()

    def create(self) -> None:
        """TODO."""
        self._queue.put()
