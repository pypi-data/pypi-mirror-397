# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from pydantic import BaseModel, Field


class LinkDesc(BaseModel):
    label: str
    url: str


class HomepageDesc(BaseModel):
    extra_links: list[LinkDesc] | None = Field(default_factory=list)
    background: str | None = None
