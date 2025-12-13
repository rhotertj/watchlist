from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

# for detailed info, see https://docs.movieofthenight.com/resource/shows#model

class Genre(BaseModel):
    id: str
    name: str


class VerticalPoster(BaseModel):
    w240: str
    w360: str
    w480: str
    w600: str
    w720: str


class HorizontalPoster(BaseModel):
    w360: str
    w480: str
    w720: str
    w1080: str
    w1440: str


class VerticalBackdrop(BaseModel):
    w240: str
    w360: str
    w480: str
    w600: str
    w720: str


class HorizontalBackdrop(BaseModel):
    w360: str
    w480: str
    w720: str
    w1080: str
    w1440: str


class ImageSet(BaseModel):
    verticalPoster: VerticalPoster
    horizontalPoster: HorizontalPoster
    verticalBackdrop: VerticalBackdrop | None = None
    horizontalBackdrop: HorizontalBackdrop | None = None


class ImageSet1(BaseModel):
    lightThemeImage: str
    darkThemeImage: str
    whiteImage: str


class Service(BaseModel):
    id: str
    name: str
    homePage: str
    themeColorCode: str
    imageSet: ImageSet1


class Audio(BaseModel):
    language: str
    region: str | None = None


class Locale(BaseModel):
    language: str
    region: str | None = None


class Subtitle(BaseModel):
    closedCaptions: bool
    locale: Locale


class Price(BaseModel):
    amount: str
    currency: str
    formatted: str

class Addon(BaseModel):
    id: str
    name: str
    homePage: str
    themeColorCode: str
    imageSet: ImageSet1

class StreamingOption(BaseModel):
    service: Service
    type: str
    addon: Addon | None = None
    link: str
    videoLink: str | None = None
    quality: Optional[str] = None
    audios: List[Audio]
    subtitles: List[Subtitle]
    price: Price | None = None
    expiresSoon: bool
    expiresOn: int | None = None
    availableSince: int


class StreamingOptions(BaseModel):
    de: Optional[List[StreamingOption]]= None
    ar: Optional[List[StreamingOption]]= None
    au: Optional[List[StreamingOption]]= None
    at: Optional[List[StreamingOption]]= None
    az: Optional[List[StreamingOption]]= None
    be: Optional[List[StreamingOption]]= None
    br: Optional[List[StreamingOption]]= None
    bg: Optional[List[StreamingOption]]= None
    ca: Optional[List[StreamingOption]]= None
    cl: Optional[List[StreamingOption]]= None
    co: Optional[List[StreamingOption]]= None
    hr: Optional[List[StreamingOption]]= None
    cy: Optional[List[StreamingOption]]= None
    cz: Optional[List[StreamingOption]]= None
    dk: Optional[List[StreamingOption]]= None
    ec: Optional[List[StreamingOption]]= None
    ee: Optional[List[StreamingOption]]= None
    fi: Optional[List[StreamingOption]]= None
    fr: Optional[List[StreamingOption]]= None
    gr: Optional[List[StreamingOption]]= None
    hk: Optional[List[StreamingOption]]= None
    hu: Optional[List[StreamingOption]]= None
    is_: Optional[List[StreamingOption]]= Field(None, alias="is")
    in_: Optional[List[StreamingOption]]= Field(None, alias="in")
    id_: Optional[List[StreamingOption]]= Field(None, alias="id")
    ie: Optional[List[StreamingOption]]= None
    il: Optional[List[StreamingOption]]= None
    it: Optional[List[StreamingOption]]= None
    jp: Optional[List[StreamingOption]]= None
    lt: Optional[List[StreamingOption]]= None
    my: Optional[List[StreamingOption]]= None
    mx: Optional[List[StreamingOption]]= None
    md: Optional[List[StreamingOption]]= None
    nl: Optional[List[StreamingOption]]= None
    nz: Optional[List[StreamingOption]]= None
    mk: Optional[List[StreamingOption]]= None
    no: Optional[List[StreamingOption]]= None
    pa: Optional[List[StreamingOption]]= None
    pe: Optional[List[StreamingOption]]= None
    ph: Optional[List[StreamingOption]]= None
    pl: Optional[List[StreamingOption]]= None
    pt: Optional[List[StreamingOption]]= None
    ro: Optional[List[StreamingOption]]= None
    ru: Optional[List[StreamingOption]]= None
    rs: Optional[List[StreamingOption]]= None
    sg: Optional[List[StreamingOption]]= None
    sk: Optional[List[StreamingOption]]= None
    si: Optional[List[StreamingOption]]= None
    za: Optional[List[StreamingOption]]= None
    kr: Optional[List[StreamingOption]]= None
    es: Optional[List[StreamingOption]]= None
    se: Optional[List[StreamingOption]]= None
    ch: Optional[List[StreamingOption]]= None
    th: Optional[List[StreamingOption]]= None
    tr: Optional[List[StreamingOption]]= None
    ua: Optional[List[StreamingOption]]= None
    ae: Optional[List[StreamingOption]]= None
    gb: Optional[List[StreamingOption]]= None
    us: Optional[List[StreamingOption]]= None
    vn: Optional[List[StreamingOption]]= None


class MOTNMovieSearchResult(BaseModel):
    itemType: str
    showType: str
    id: str
    imdbId: str
    tmdbId: str
    title: str
    overview: str
    releaseYear: int | None = None
    firstYearAir: int | None = None
    lastYearAir: int | None = None
    originalTitle: str
    genres: List[Genre]
    directors: List[str] | None = None
    creators: List[str] | None = None
    cast: List[str]
    rating: int
    seasonCount : int | None = None
    episodeCount: int| None = None
    runtime: int | None = None
    imageSet: ImageSet
    streamingOptions: StreamingOptions


class MOTNMovieSearchResults(BaseModel):
    results: List[MOTNMovieSearchResult]