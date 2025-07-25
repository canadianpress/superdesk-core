# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
from typing import List, Mapping, TypedDict, cast
from hachoir.stream import InputIOStream
from hachoir.parser import guessParser
from hachoir.metadata import extractMetadata
from flask import json
import logging
from superdesk.media.image import PhotoMetadata


logger = logging.getLogger(__name__)


def get_meta(filestream):
    metadata = {}

    try:
        filestream.seek(0)
        stream = InputIOStream(filestream, None, tags=[])
        parser = guessParser(stream)
        if not parser:
            return metadata

        tags = extractMetadata(parser).exportPlaintext(human=False, line_prefix="")
        for text in tags:
            try:
                json.dumps(text)
                key, value = text.split(":", maxsplit=1)
                key, value = key.strip(), value.strip()
                if key and value:
                    metadata.update({key: value})
            except Exception as ex:
                logger.exception(ex)
    except Exception as ex:
        logger.exception(ex)
        return metadata
    return metadata


VideoMetadata = TypedDict(
    "VideoMetadata",
    {
        "Description": str | None,
        "CaptionWriter": str | None,
        "Headline": str | None,
        "Instructions": str | None,
        "TransmissionReference": str | None,
        "Title": str | None,
        "Creator": str | None,
        "AuthorsPosition": str | None,
        "Rights": str | None,
        "City": str | None,
        "Country": str | None,
        "CountryCode": str | None,
        "Credit": str | None,
        "State": str | None,
        "Location": str | None,
        "CreatorContactInfo": str | None,
        "Language": str | None,
        "Destination": str | None,
        "ServiceIdentifier": str | None,
        "ProductID": str | None,
        "DateSent": str | None,
        "TimeSent": str | None,
        "EditStatus": str | None,
        "Urgency": str | None,
        "SubjectCode": str | None,
        "Category": str | None,
        "SupplementalCategories": str | None,
        "Subject": str | None,
        "LocationCode": str | None,
        "LocationName": str | None,
        "ReleaseDate": str | None,
        "ReleaseTime": str | None,
        "ExpirationDate": str | None,
        "ExpirationTime": str | None,
        "TimeCreated": str | None,
        "Source": str | None,
        "DateCreated": str | None,
    },
    total=False,
)


def read_metadata(input: bytes) -> VideoMetadata:
    import tempfile
    from exiftool import ExifToolHelper  # type: ignore
    from exiftool.exceptions import ExifToolException  # type: ignore

    with tempfile.NamedTemporaryFile(delete=True) as temp:
        temp.write(input)
        temp.flush()

        try:
            with ExifToolHelper() as et:
                raw_metadata: Mapping[str, str] = et.get_metadata(temp.name, ["-xmp:all"])[0]
                metadata = {k.replace("XMP:", ""): v for k, v in raw_metadata.items()}
                return cast(VideoMetadata, metadata)
        except ExifToolException as e:
            logger.exception(e.stderr)
            return {}


def write_metadata(input: bytes, metadata: VideoMetadata):
    args = map_xmp_to_exiftool_args(metadata)
    return write_xmp_with_exiftool(input, args)


def get_metadata_from_item(metadata: PhotoMetadata) -> VideoMetadata:
    """Get XMP and truthy custom tags

    @param metadata: PhotoMetadata
    """

    xmp = {
        "Description": metadata.get("Caption-Abstract"),
        "CaptionWriter": metadata.get("Writer-Editor"),
        "Headline": metadata.get("Headline"),
        "Instructions": metadata.get("SpecialInstructions"),
        "TransmissionReference": metadata.get("OriginalTransmissionReference"),
        "Title": metadata.get("ObjectName"),
        "Creator": metadata.get("By-line"),
        "AuthorsPosition": metadata.get("By-lineTitle"),
        "Rights": metadata.get("CopyrightNotice"),
        "City": metadata.get("City"),
        "Country": metadata.get("Country-PrimaryLocationName"),
        "CountryCode": metadata.get("Country-PrimaryLocationCode"),
        "Credit": metadata.get("Credit"),
        "State": metadata.get("Province-State"),
        "Location": metadata.get("Sub-location"),
        "CreatorContactInfo": metadata.get("Contact"),
        "Language": metadata.get("LanguageIdentifier"),
        "Destination": metadata.get("Destination"),
        "ServiceIdentifier": metadata.get("ServiceIdentifier"),
        "ProductID": metadata.get("ProductID"),
        "DateSent": metadata.get("DateSent"),
        "TimeSent": metadata.get("TimeSent"),
        "EditStatus": metadata.get("EditStatus"),
        "Urgency": metadata.get("Urgency"),
        "SubjectCode": metadata.get("SubjectReference"),
        "Category": metadata.get("Category"),
        "SupplementalCategories": metadata.get("SupplementalCategories"),
        "Subject": metadata.get("Keywords"),
        "LocationCode": metadata.get("ContentLocationCode"),
        "LocationName": metadata.get("ContentLocationName"),
        "ReleaseDate": metadata.get("ReleaseDate"),
        "ReleaseTime": metadata.get("ReleaseTime"),
        "ExpirationDate": metadata.get("ExpirationDate"),
        "ExpirationTime": metadata.get("ExpirationTime"),
        "TimeCreated": metadata.get("TimeCreated"),
        "Source": metadata.get("Source"),
        **(
            {"DateCreated": f"{metadata['DateCreated']}T{metadata['TimeCreated']}"}
            if metadata.get("DateCreated") and metadata.get("TimeCreated")
            else {}
        ),
    }
    tags = {k: vv for k, v in xmp.items() if (vv := v or metadata.get(k))}
    tags.update({k: v for k, v in metadata.items() if k not in xmp and v})
    return cast(VideoMetadata, tags)


def get_metadata_from_exiftool(metadata: VideoMetadata) -> VideoMetadata:
    xmp = {
        "Description": metadata.get("Description"),
        "CaptionWriter": metadata.get("CaptionWriter"),
        "Headline": metadata.get("Headline"),
        "Instructions": metadata.get("Instructions"),
        "TransmissionReference": metadata.get("TransmissionReference"),
        "Title": metadata.get("Title"),
        "Creator": metadata.get("Creator"),
        "AuthorsPosition": metadata.get("AuthorsPosition"),
        "Rights": metadata.get("Rights"),
        "City": metadata.get("City"),
        "Country": metadata.get("Country"),
        "CountryCode": metadata.get("CountryCode"),
        "Credit": metadata.get("Credit"),
        "State": metadata.get("State"),
    }
    xmp = {k: v for k, v in xmp.items() if v}
    return cast(VideoMetadata, xmp)


def map_xmp_to_exiftool_args(xmp: VideoMetadata):
    args = [f"-{key}={value}" for key, value in xmp.items()]
    args.append("-overwrite_original")
    return args


def write_xmp_with_exiftool(original: bytes, args: List[str]):
    import tempfile
    from exiftool import ExifToolHelper
    from exiftool.exceptions import ExifToolExecuteError

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(original)
        temp.flush()
        temp_path = temp.name

    try:
        with ExifToolHelper() as et:
            et.execute(*args, temp_path)

        with open(temp_path, "rb") as updated:
            return updated.read()
    except ExifToolExecuteError as e:
        logger.exception(e.stderr)
        return original
    finally:
        os.remove(temp_path)
