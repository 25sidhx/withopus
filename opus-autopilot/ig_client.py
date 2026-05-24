"""Instagram client wrapper — login, session persistence, safe API calls."""

import json
import logging
import time
from pathlib import Path

from instagrapi import Client
from instagrapi.types import Media, User

import config

logger = logging.getLogger("autopilot.ig_client")


class IGClient:
    """Singleton-ish Instagram client with session persistence."""

    _instance: Client | None = None

    @classmethod
    def get(cls) -> Client:
        if cls._instance is not None:
            return cls._instance

        cl = Client()
        cl.delay_range = [2, 5]

        # Try loading saved session first
        if config.IG_SESSION_FILE.exists():
            try:
                cl.load_settings(str(config.IG_SESSION_FILE))
                cl.login(config.IG_USERNAME, config.IG_PASSWORD)
                cl.get_timeline_feed()  # verify session is alive
                logger.info("Restored saved IG session for @%s", config.IG_USERNAME)
                cls._instance = cl
                return cl
            except Exception:
                logger.warning("Saved session expired, doing fresh login.")

        # Fresh login
        cl.login(config.IG_USERNAME, config.IG_PASSWORD)
        cl.dump_settings(str(config.IG_SESSION_FILE))
        logger.info("Fresh IG login for @%s, session saved.", config.IG_USERNAME)
        cls._instance = cl
        return cl

    @classmethod
    def reset(cls):
        cls._instance = None
        if config.IG_SESSION_FILE.exists():
            config.IG_SESSION_FILE.unlink()


def get_user_id(username: str) -> int | None:
    """Resolve a username to a user ID."""
    cl = IGClient.get()
    try:
        uid = cl.user_id_from_username(username)
        logger.info("Resolved @%s -> %s", username, uid)
        return uid
    except Exception as e:
        logger.error("Could not resolve @%s: %s", username, e)
        return None


def get_user_posts(username: str, amount: int = 5) -> list[Media]:
    """Fetch recent posts from a user using the private v1 API."""
    cl = IGClient.get()
    uid = get_user_id(username)
    if not uid:
        return []

    try:
        # Use v1 (private API) — more reliable than GraphQL
        medias = cl.user_medias_v1(uid, amount=amount)
        logger.info("Fetched %d posts from @%s", len(medias), username)
        return medias
    except Exception as e:
        logger.warning("v1 failed for @%s: %s. Trying paginated.", username, e)
        try:
            medias = cl.user_medias(uid, amount=amount)
            return medias
        except Exception as e2:
            logger.error("All methods failed for @%s: %s", username, e2)
            return []


def post_photo(image_path: str, caption: str) -> Media | None:
    """Post a single photo."""
    cl = IGClient.get()
    try:
        media = cl.photo_upload(path=image_path, caption=caption)
        logger.info("Posted photo: %s", media.code)
        return media
    except Exception as e:
        logger.error("Photo upload failed: %s", e)
        return None


def post_carousel(image_paths: list[str], caption: str) -> Media | None:
    """Post a carousel (album) of images."""
    cl = IGClient.get()
    try:
        media = cl.album_upload(paths=image_paths, caption=caption)
        logger.info("Posted carousel (%d slides): %s", len(image_paths), media.code)
        return media
    except Exception as e:
        logger.error("Carousel upload failed: %s", e)
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cl = IGClient.get()
    print(f"Logged in as @{config.IG_USERNAME}")
