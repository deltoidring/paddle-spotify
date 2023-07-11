def create_artist(num: int):
    sid = f"ARTISTID{num}"
    return {
        "name": f"Artist {num}",
        "external_urls": {"spotify": f"https://open.spotify.com/artist/{sid}"},
        "href": f"https://api.spotify.com/v1/artists/{sid}",
        "id": f"{sid}",
        "type": "artist",
        "uri": f"spotify:artist:{sid}",
    }


artist_1 = create_artist(num=1)
artist_2 = create_artist(num=2)
artist_3 = create_artist(num=3)
artist_4 = create_artist(num=4)
