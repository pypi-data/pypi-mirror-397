"""Database integration for MongoDB Database.

This module creates functions to upload FullMetadata objects
to the database and search for relations by their key attributes.
"""

from typing import List

from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertOneResult

from waft.datatypes import Album, Artist, DisplayedTrack, FullMetadata, Track


def upload_relation(metadata: FullMetadata, yt_link: str, file_hash: str) -> None:
    """Upload a complete music metadata relation into the MongoDB database.

    This function decomposes a `FullMetadata` object into its component entities
    (Album, Track, Artist) and inserts them into their respective collections.
    It also creates linking records to represent relationships between tracks,
    albums, artists, and associated files, including a YouTube source link and
    a unique file hash.

    Parameters
    ----------
    metadata : FullMetadata
        Fully populated metadata object containing album, artist(s), and track
        information to be stored.
    yt_link : str
        YouTube URL associated with the track.
    file_hash : str
        Unique hash identifying the file; used as the primary key for the File
        collection.

    Returns
    -------
    None

    Raises
    ------
    pymongo.errors.PyMongoError
        If any database insertion or connection operation fails.
    """
    con_str: str = (
        "mongodb+srv://lpdh3m_db_user:wiki_app_for_tunes_pass"
        "@wiki-app-for-tunes.5juoymq.mongodb.net/"
    )
    client: MongoClient = MongoClient(con_str)

    db: Database = client["Wiki-App-DB"]

    album_collection = db["Album"]
    artist_collection = db["Artist"]
    file_collection = db["File"]
    on_collection = db["On"]
    records_collection = db["Records"]
    track_collection = db["Track"]

    album: Album = metadata.album
    inserted_album: InsertOneResult = album_collection.insert_one(
        {"Name": album.album_name, "CoverImageLink": album.image_url}
    )
    album_id: str = inserted_album.inserted_id

    track: Track = metadata.track
    inserted_track: InsertOneResult = track_collection.insert_one(
        {
            "Name": track.name,
            "ReleaseDate": track.release_date,
            "Duration": track.duration_ms,
            "Explicit": track.explicit,
        }
    )
    track_id: str = inserted_track.inserted_id

    artists: List[Artist] = metadata.artists
    for artist in artists:
        inserted_artist: InsertOneResult = artist_collection.insert_one(
            {"Name": artist.artist_name}
        )
        artist_id: str = inserted_artist.inserted_id
        records_collection.insert_one({"ArtistID": artist_id, "TrackID": track_id})

    # NOTE: _id is the same as Hash in the ER Diagram. MongoDB enforced _id as PK
    file_collection.insert_one(
        {"_id": file_hash, "TrackID": track_id, "SourceLink": yt_link}
    )

    on_collection.insert_one(
        {"TrackID": track_id, "AlbumID": album_id, "TrackNumber": track.track_number}
    )


def get_yt_url(partial_metadata: DisplayedTrack) -> str | None:
    """
    Retrieve a YouTube URL by matching metadata attributes in the database.

    This function searches the database for an existing relation that matches
    the provided metadata using track name, release date, album name, and at
    least one artist name. If a matching relation is found, the associated
    YouTube source link is returned.

    Parameters
    ----------
    metadata : FullMetadata
        Metadata object containing track, album, and artist information used
        to search for a matching database entry.

    Returns
    -------
    str | None
        The associated YouTube URL if a matching relation is found;
        otherwise, None.

    Raises
    ------
    pymongo.errors.PyMongoError
        If a database query or connection fails.
    """
    metadata: FullMetadata = FullMetadata(
        Album(partial_metadata.album, ""),
        [Artist(partial_metadata.artist)],
        Track(
            "",
            False,
            partial_metadata.title,
            "33",
            0,
        ),
    )
    track_name: str = metadata.track.name
    # release_date: str = metadata.track.release_date
    album_name: str = metadata.album.album_name
    artist_names: List[str] = []
    for artist in metadata.artists:
        artist_names.append(artist.artist_name)

    con_str: str = (
        "mongodb+srv://lpdh3m_db_user:wiki_app_for_tunes_pass"
        "@wiki-app-for-tunes.5juoymq.mongodb.net/"
    )
    client: MongoClient = MongoClient(con_str)
    db: Database = client["Wiki-App-DB"]

    album_collection = db["Album"]
    artist_collection = db["Artist"]
    file_collection = db["File"]
    on_collection = db["On"]
    records_collection = db["Records"]
    track_collection = db["Track"]

    # groupings of entities that match the given metadata
    candidate_tracks: Cursor = track_collection.find({"Name": track_name})
    candidate_albums: Cursor = album_collection.find({"Name": album_name})
    candidate_artists: Cursor = artist_collection.find({"Name": {"$in": artist_names}})
    candidate_artists_names: List[str] = []
    for artist in candidate_artists:
        candidate_artists_names.append(artist["Name"])

    # list of track ids that are associated with a candidate album_name
    for track_doc in candidate_tracks:
        track_id: str = track_doc["_id"]
        on_doc = on_collection.find_one({"TrackID": track_id})  # type: ignore
        album_id: str = on_doc["AlbumID"]  # type: ignore
        match_exists: bool = False
        for album_doc in candidate_albums:
            album_doc_id: str = album_doc["_id"]
            if album_id == album_doc_id:
                match_exists = True
                break
        if not match_exists:
            # There is no metadata in the DB that matches the provided
            return None
        records_docs = records_collection.find({"TrackID": track_id})
        for records_doc in records_docs:
            artist_id: str = records_doc["ArtistID"]
            matched_artist = artist_collection.find_one(  # type: ignore
                {"_id": artist_id}
            )
            if matched_artist["Name"] in candidate_artists_names:  # type: ignore
                # We matched Track Name, release date, Album name, and 1+ Artist names
                # Find File with track_id
                file_doc = file_collection.find_one(  # type: ignore
                    {"TrackID": track_id}
                )
                link = file_doc["SourceLink"]  # type: ignore
                return link
    return None  # Nothing was matched
