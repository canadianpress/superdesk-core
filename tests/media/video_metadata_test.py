from pytest import fixture
from superdesk.media.video import (
    read_metadata as read_video_metadata,
    get_xmp_tags_from_exif,
    convert_xmp_to_args,
    write_xmp_with_exiftool,
    get_xmp_tags_from_item,
)
from superdesk.media.image import read_metadata as read_image_metadata

from .. import fixture_path


@fixture
def image_binary() -> bytes:
    image_path = fixture_path("cp.jpg", "media")
    with open(image_path, mode="rb") as f:
        return f.read()


@fixture
def video_binary() -> bytes:
    image_path = fixture_path("cp.mov", "media")
    with open(image_path, mode="rb") as f:
        return f.read()


def test_picture_metadata_read_write_from_video(video_binary) -> None:
    metadata = read_video_metadata(video_binary)
    xmp = get_xmp_tags_from_exif(metadata)

    assert xmp == {
        "Description": "Your Description Here",
        "Headline": "Your Headline",
        "City": "Your City",
        "Country": "Your Country",
        "CountryCode": "US",
        "Creator": "Your Creator Name",
        "AuthorsPosition": "Your Job Title",
        "TransmissionReference": "Your Job ID",
        "Instructions": "Your Instructions",
        "Title": "Your Title",
        "Rights": "Your Copyright Notice",
        "Credit": "Your Credit Line",
        "State": "Your Province or State",
        "CaptionWriter": "Your Caption Writer",
    }

    updated = {
        "Description": "Your Description Here 1",
        "Headline": "Your Headline 2",
        "City": "Your City 3",
        "Country": "Your Country 4",
        "CountryCode": "US 5",
        "Creator": "Your Creator Name 6",
        "AuthorsPosition": "Your Job Title 7",
        "TransmissionReference": "Your Job ID 8",
        "Instructions": "Your Instructions 9",
        "Title": "Your Title 10",
        "Rights": "Your Copyright Notice 11",
        "Credit": "Your Credit Line 12",
        "State": "Your Province or State 13",
        "CaptionWriter": "Your Caption Writer 14",
    }
    args = convert_xmp_to_args(updated)
    next_video = write_xmp_with_exiftool(video_binary, args)
    next_metadata = read_video_metadata(next_video)
    next_xmp = get_xmp_tags_from_exif(next_metadata)

    assert next_xmp == updated


def test_picture_metadata_read_from_image(image_binary) -> None:
    metadata = read_image_metadata(image_binary)
    xmp = get_xmp_tags_from_item(metadata)

    assert xmp == {
        "Description": "The Montreal Police logo is seen on a police car in Montreal on Wednesday, July 8, 2020. THE CANADIAN PRESS/Paul Chiasson",
        "DescriptionWriter": "pch",
        "City": "Montreal",
        "Country": "Canada",
        "CountryCode": "CAN",
        "Creator": ["Paul Chiasson"],
        "CreatorsJobtitle": "stf",
        "JobId": "DPI755",
        "Instructions": "EDS NOTE:A FILE PHOTO",
        "Title": "MORT PIÉTONNE MONTRÉAL 20201014",
        "CreditLine": "The Canadian Press",
        "ProvinceState": "PQ",
    }
