/**
 * TypeScript type definitions generated from Python Pydantic models
 * These match the API responses from the backend
 */

// ============================================================================
// MovieOfTheNight API Types
// ============================================================================

export interface Genre {
	id: string;
	name: string;
}

export interface VerticalPoster {
	w240: string;
	w360: string;
	w480: string;
	w600: string;
	w720: string;
}

export interface HorizontalPoster {
	w360: string;
	w480: string;
	w720: string;
	w1080: string;
	w1440: string;
}

export interface VerticalBackdrop {
	w240: string;
	w360: string;
	w480: string;
	w600: string;
	w720: string;
}

export interface HorizontalBackdrop {
	w360: string;
	w480: string;
	w720: string;
	w1080: string;
	w1440: string;
}

export interface ImageSet {
	verticalPoster: VerticalPoster;
	horizontalPoster: HorizontalPoster;
	verticalBackdrop?: VerticalBackdrop | null;
	horizontalBackdrop?: HorizontalBackdrop | null;
}

export interface ServiceImageSet {
	lightThemeImage: string;
	darkThemeImage: string;
	whiteImage: string;
}

export interface StreamingService {
	id: string;
	name: string;
	homePage: string;
	themeColorCode: string;
	imageSet: ServiceImageSet;
}

export interface Audio {
	language: string;
	region?: string | null;
}

export interface Locale {
	language: string;
	region?: string | null;
}

export interface Subtitle {
	closedCaptions: boolean;
	locale: Locale;
}

export interface Price {
	amount: string;
	currency: string;
	formatted: string;
}

export interface Addon {
	id: string;
	name: string;
	homePage: string;
	themeColorCode: string;
	imageSet: ServiceImageSet;
}

/**
 * Streaming option type literals
 * - subscription: Regular subscription service (Netflix, Disney+, etc.)
 * - buy: Purchase to own
 * - rent: Temporary rental
 * - addon: Additional subscription required (e.g., Prime Video Channels)
 */
export type StreamingOptionType = 'subscription' | 'buy' | 'rent' | 'addon';

export interface StreamingOption {
	service: StreamingService;
	type: StreamingOptionType;
	addon?: Addon | null;
	link: string;
	videoLink?: string | null;
	quality?: string | null;
	audios: Audio[];
	subtitles: Subtitle[];
	price?: Price | null;
	expiresSoon: boolean;
	expiresOn?: number | null;
	availableSince: number;
}

/**
 * Country-specific streaming options
 * ISO 3166-1 alpha-2 country codes
 */
export interface StreamingOptions {
	de?: StreamingOption[];
	ar?: StreamingOption[];
	au?: StreamingOption[];
	at?: StreamingOption[];
	az?: StreamingOption[];
	be?: StreamingOption[];
	br?: StreamingOption[];
	bg?: StreamingOption[];
	ca?: StreamingOption[];
	cl?: StreamingOption[];
	co?: StreamingOption[];
	hr?: StreamingOption[];
	cy?: StreamingOption[];
	cz?: StreamingOption[];
	dk?: StreamingOption[];
	ec?: StreamingOption[];
	ee?: StreamingOption[];
	fi?: StreamingOption[];
	fr?: StreamingOption[];
	gr?: StreamingOption[];
	hk?: StreamingOption[];
	hu?: StreamingOption[];
	is?: StreamingOption[];
	in?: StreamingOption[];
	id?: StreamingOption[];
	ie?: StreamingOption[];
	il?: StreamingOption[];
	it?: StreamingOption[];
	jp?: StreamingOption[];
	lt?: StreamingOption[];
	my?: StreamingOption[];
	mx?: StreamingOption[];
	md?: StreamingOption[];
	nl?: StreamingOption[];
	nz?: StreamingOption[];
	mk?: StreamingOption[];
	no?: StreamingOption[];
	pa?: StreamingOption[];
	pe?: StreamingOption[];
	ph?: StreamingOption[];
	pl?: StreamingOption[];
	pt?: StreamingOption[];
	ro?: StreamingOption[];
	ru?: StreamingOption[];
	rs?: StreamingOption[];
	sg?: StreamingOption[];
	sk?: StreamingOption[];
	si?: StreamingOption[];
	za?: StreamingOption[];
	kr?: StreamingOption[];
	es?: StreamingOption[];
	se?: StreamingOption[];
	ch?: StreamingOption[];
	th?: StreamingOption[];
	tr?: StreamingOption[];
	ua?: StreamingOption[];
	ae?: StreamingOption[];
	gb?: StreamingOption[];
	us?: StreamingOption[];
	vn?: StreamingOption[];
}

export interface MOTNMovieSearchResult {
	itemType: string;
	showType: string;
	id: string;
	imdbId: string;
	tmdbId: string;
	title: string;
	overview: string;
	releaseYear?: number | null;
	firstYearAir?: number | null;
	lastYearAir?: number | null;
	originalTitle: string;
	genres: Genre[];
	directors?: string[] | null;
	creators?: string[] | null;
	cast: string[];
	rating: number;
	seasonCount?: number | null;
	episodeCount?: number | null;
	runtime?: number | null;
	imageSet: ImageSet;
	streamingOptions: StreamingOptions;
}

export interface MOTNMovieSearchResults {
	results: MOTNMovieSearchResult[];
}

// ============================================================================
// Letterboxd Types
// ============================================================================

/**
 * Movie item from Letterboxd watchlist
 * The streaming_options field is populated after fetching from MovieOfTheNight API
 */
export interface LetterboxdMovieItem {
	readonly movie_id: string;
	readonly movie_name: string;
	readonly movie_slug: string;
	readonly movie_url: string;
	streaming_options: StreamingOptionsByService;
}

/**
 * Streaming options grouped by service ID
 * This is the format used in the frontend after processing the API response
 *
 * Example:
 * {
 *   "netflix": [StreamingOption, StreamingOption],
 *   "prime": [StreamingOption],
 *   "disney": [StreamingOption, StreamingOption, StreamingOption]
 * }
 */
export type StreamingOptionsByService = Record<string, StreamingOption[]>;

// ============================================================================
// Frontend-Specific Types
// ============================================================================

/**
 * Movie item with loading state for better UX
 */
export interface MovieItemWithLoadingState extends LetterboxdMovieItem {
	loadingState: 'idle' | 'loading' | 'success' | 'error';
	stateMessage: string;
}

/**
 * Error response from the API
 */
export interface APIError {
	detail: string;
}
