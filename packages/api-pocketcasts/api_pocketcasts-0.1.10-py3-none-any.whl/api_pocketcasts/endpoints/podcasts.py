# Podcast subscription endpoints for Pocket Casts API.
# Stateless, in-memory only. No credentials or tokens are ever persisted to disk.

import httpx
from api_pocketcasts.models import (
    PodcastList,
    Podcast,
    PodcastSettings,
    PodcastSetting,
    SubscriptionResult,
    UserEpisode,
)

from api_pocketcasts.exceptions import (
    PocketCastsAuthError,
    PocketCastsAPIError,
    PocketCastsAPIResponseError,
)


def get_subscribed_podcasts(access_token: str) -> PodcastList:
    """
    Retrieve the list of podcasts the user is subscribed to.
    """
    PODCAST_LIST_URL = "https://api.pocketcasts.com/user/podcast/list"
    if not access_token:
        raise PocketCastsAuthError("Not authenticated. Please login first.")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx.post(
            PODCAST_LIST_URL,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except Exception as e:
            raise PocketCastsAPIResponseError(
                message="Failed to parse podcast list response as JSON.",
                details={"exception": str(e), "response": response.text},
            )
        if not isinstance(data, dict) or "podcasts" not in data:
            raise PocketCastsAPIResponseError(
                message="Podcast list response missing 'podcasts' field.",
                details={"response": data},
            )
        podcasts = []
        for p in data.get("podcasts", []):
            settings = None
            if "settings" in p:
                try:
                    settings_kwargs = {}
                    for k, v in p["settings"].items():
                        settings_kwargs[k] = (
                            PodcastSetting(**v) if isinstance(v, dict) else None
                        )
                    settings = PodcastSettings(**settings_kwargs)
                except Exception as e:
                    raise PocketCastsAPIResponseError(
                        message="Malformed PodcastSettings in podcast list response.",
                        details={
                            "exception": str(e),
                            "settings": p.get("settings"),
                        },
                    )
            try:
                podcasts.append(
                    Podcast(
                        uuid=p["uuid"],
                        episodesSortOrder=p.get("episodesSortOrder"),
                        autoStartFrom=p.get("autoStartFrom"),
                        title=p["title"],
                        author=p["author"],
                        description=p.get("description"),
                        url=p.get("url"),
                        lastEpisodePublished=p.get("lastEpisodePublished"),
                        unplayed=p.get("unplayed"),
                        lastEpisodeUuid=p.get("lastEpisodeUuid"),
                        lastEpisodePlayingStatus=p.get("lastEpisodePlayingStatus"),
                        lastEpisodeArchived=p.get("lastEpisodeArchived"),
                        autoSkipLast=p.get("autoSkipLast"),
                        folderUuid=p.get("folderUuid"),
                        sortPosition=p.get("sortPosition"),
                        dateAdded=p.get("dateAdded"),
                        settings=settings,
                        descriptionHtml=p.get("descriptionHtml"),
                        isPrivate=p.get("isPrivate"),
                        slug=p.get("slug"),
                    )
                )
            except Exception as e:
                raise PocketCastsAPIResponseError(
                    message="Malformed Podcast object in podcast list response.",
                    details={"exception": str(e), "podcast": p},
                )
        return PodcastList(podcasts=podcasts, folders=data.get("folders"))
    except httpx.HTTPStatusError as e:
        raise PocketCastsAuthError(
            message="Failed to fetch podcast list.",
            details={
                "status_code": e.response.status_code,
                "response": e.response.text,
            },
        )
    except httpx.TimeoutException as e:
        raise PocketCastsAPIError(
            code="timeout_error",
            message="Timeout while fetching podcast list.",
            details={"exception": str(e)},
        )
    except httpx.RequestError as e:
        raise PocketCastsAPIError(
            code="network_error",
            message="Network error while fetching podcast list.",
            details={"exception": str(e)},
        )
    except PocketCastsAPIError:
        raise
    except Exception as e:
        raise PocketCastsAPIError(
            code="unexpected_error",
            message="Unexpected error during podcast list fetch.",
            details={"exception": str(e)},
        )


def subscribe_to_podcast(access_token: str, podcast_uuid: str) -> SubscriptionResult:
    """
    Subscribe the user to a podcast.
    """
    PODCAST_SUBSCRIBE_URL = "https://api.pocketcasts.com/user/podcast/subscribe"
    if not access_token:
        raise PocketCastsAuthError("Not authenticated. Please login first.")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx.post(
            PODCAST_SUBSCRIBE_URL,
            headers=headers,
            json={"uuid": podcast_uuid},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return SubscriptionResult(
            success=True, message=data.get("message"), podcast_uuid=podcast_uuid
        )
    except httpx.HTTPStatusError as e:
        return SubscriptionResult(
            success=False,
            message=f"Failed to subscribe: {e.response.text}",
            podcast_uuid=podcast_uuid,
        )
    except Exception as e:
        return SubscriptionResult(
            success=False,
            message=f"Unexpected error: {str(e)}",
            podcast_uuid=podcast_uuid,
        )


def unsubscribe_from_podcast(
    access_token: str, podcast_uuid: str
) -> SubscriptionResult:
    """
    Unsubscribe the user from a podcast.
    """
    PODCAST_UNSUBSCRIBE_URL = "https://api.pocketcasts.com/user/podcast/unsubscribe"
    if not access_token:
        raise PocketCastsAuthError("Not authenticated. Please login first.")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx.post(
            PODCAST_UNSUBSCRIBE_URL,
            headers=headers,
            json={"uuid": podcast_uuid},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return SubscriptionResult(
            success=True, message=data.get("message"), podcast_uuid=podcast_uuid
        )
    except httpx.HTTPStatusError as e:
        return SubscriptionResult(
            success=False,
            message=f"Failed to unsubscribe: {e.response.text}",
            podcast_uuid=podcast_uuid,
        )
    except Exception as e:
        return SubscriptionResult(
            success=False,
            message=f"Unexpected error: {str(e)}",
            podcast_uuid=podcast_uuid,
        )


def get_user_episode(access_token: str, episode_uuid: str) -> UserEpisode:
    """
    Retrieve a single episode's details for the user (POST /user/episode).
    Raises PocketCastsAuthError for missing/invalid token,
        and PocketCastsAPIResponseError for 404 or malformed responses.
    """
    USER_EPISODE_URL = "https://api.pocketcasts.com/user/episode"
    if not access_token:
        raise PocketCastsAuthError("Not authenticated. Please login first.")
    if not episode_uuid:
        raise PocketCastsAPIResponseError(
            message="No episode UUID provided.",
            details={"episode_uuid": episode_uuid},
        )
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx.post(
            USER_EPISODE_URL,
            headers=headers,
            json={"uuid": episode_uuid},
            timeout=10,
        )
        if response.status_code == 404:
            raise PocketCastsAPIResponseError(
                message="Episode not found (404).",
                details={
                    "status_code": 404,
                    "episode_uuid": episode_uuid,
                    "response": response.text,
                },
            )
        response.raise_for_status()
        try:
            data = response.json()
        except Exception as e:
            raise PocketCastsAPIResponseError(
                message="Failed to parse user episode response as JSON.",
                details={"exception": str(e), "response": response.text},
            )
        # Strict validation of required fields and types
        required_fields = [
            ("uuid", str),
            ("url", str),
            ("published", str),
            ("duration", int),
            ("fileType", str),
            ("title", str),
            ("podcastUuid", str),
        ]
        for field, typ in required_fields:
            if field not in data or not isinstance(data[field], typ):
                raise PocketCastsAPIResponseError(
                    message=(
                        f"UserEpisode response missing or invalid type for required field '"
                        f"{field}'"
                    ),
                    details={
                        "field": field,
                        "expected_type": typ.__name__,
                        "data": data,
                    },
                )
        try:
            return UserEpisode(
                uuid=data["uuid"],
                url=data.get("url"),
                published=data.get("published"),
                duration=data.get("duration"),
                file_type=data.get("fileType"),
                title=data.get("title"),
                size=data.get("size"),
                playing_status=data.get("playingStatus"),
                played_up_to=data.get("playedUpTo"),
                starred=data.get("starred"),
                podcast_uuid=data.get("podcastUuid"),
                podcast_title=data.get("podcastTitle"),
                episode_type=data.get("episodeType"),
                episode_season=data.get("episodeSeason"),
                episode_number=data.get("episodeNumber"),
                is_deleted=data.get("isDeleted"),
                author=data.get("author"),
                bookmarks=data.get("bookmarks"),
                podcast_slug=data.get("podcastSlug"),
                slug=data.get("slug"),
            )
        except Exception as e:
            raise PocketCastsAPIResponseError(
                message="Malformed UserEpisode object in response.",
                details={"exception": str(e), "data": data},
            )
    except httpx.HTTPStatusError as e:
        raise PocketCastsAPIError(
            code="http_error",
            message="HTTP error while fetching user episode.",
            details={
                "status_code": e.response.status_code,
                "response": e.response.text,
            },
        )
    except httpx.TimeoutException as e:
        raise PocketCastsAPIError(
            code="timeout_error",
            message="Timeout while fetching user episode.",
            details={"exception": str(e)},
        )
    except httpx.RequestError as e:
        raise PocketCastsAPIError(
            code="network_error",
            message="Network error while fetching user episode.",
            details={"exception": str(e)},
        )
    except PocketCastsAPIError:
        raise
    except Exception as e:
        raise PocketCastsAPIError(
            code="unexpected_error",
            message="Unexpected error during user episode fetch.",
            details={"exception": str(e)},
        )
