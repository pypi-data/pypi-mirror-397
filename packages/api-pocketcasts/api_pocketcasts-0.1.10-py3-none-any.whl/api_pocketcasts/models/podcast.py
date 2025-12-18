"""
Podcast and subscription data models for Pocket Casts API.
"""

import attr
from typing import List, Optional, Dict, Any


@attr.s(auto_attribs=True, frozen=True)
class PodcastSetting:
    value: Optional[Any] = None
    changed: Optional[bool] = None
    modifiedAt: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True)
class PodcastSettings:
    notification: Optional[PodcastSetting] = None
    addToUpNext: Optional[PodcastSetting] = None
    addToUpNextPosition: Optional[PodcastSetting] = None
    autoArchive: Optional[PodcastSetting] = None
    playbackEffects: Optional[PodcastSetting] = None
    playbackSpeed: Optional[PodcastSetting] = None
    trimSilence: Optional[PodcastSetting] = None
    volumeBoost: Optional[PodcastSetting] = None
    autoStartFrom: Optional[PodcastSetting] = None
    autoSkipLast: Optional[PodcastSetting] = None
    episodesSortOrder: Optional[PodcastSetting] = None
    autoArchivePlayed: Optional[PodcastSetting] = None
    autoArchiveInactive: Optional[PodcastSetting] = None
    autoArchiveEpisodeLimit: Optional[PodcastSetting] = None
    episodeGrouping: Optional[PodcastSetting] = None
    showArchived: Optional[PodcastSetting] = None


@attr.s(auto_attribs=True, frozen=True)
class Podcast:
    uuid: str
    title: str
    author: str
    episodesSortOrder: Optional[int] = None
    autoStartFrom: Optional[int] = None
    description: Optional[str] = None
    url: Optional[str] = None
    lastEpisodePublished: Optional[str] = None
    unplayed: Optional[bool] = None
    lastEpisodeUuid: Optional[str] = None
    lastEpisodePlayingStatus: Optional[int] = None
    lastEpisodeArchived: Optional[bool] = None
    autoSkipLast: Optional[int] = None
    folderUuid: Optional[str] = None
    sortPosition: Optional[int] = None
    dateAdded: Optional[str] = None
    settings: Optional[PodcastSettings] = None
    descriptionHtml: Optional[str] = None
    isPrivate: Optional[bool] = None
    slug: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True)
class PodcastList:
    podcasts: List[Podcast]
    folders: Optional[List[Dict[str, Any]]] = None


@attr.s(auto_attribs=True, frozen=True)
class SubscriptionResult:
    success: bool
    message: Optional[str] = None
    podcast_uuid: Optional[str] = None
