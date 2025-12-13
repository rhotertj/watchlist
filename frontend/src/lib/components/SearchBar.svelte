<script lang="ts">
	import type {
		LetterboxdMovieItem,
		StreamingOption,
		MovieItemWithLoadingState,
		StreamingOptionsByService
	} from '$lib/types';
	// updates watchlist state in parent component
	let { watchlist = $bindable([]) }: { watchlist: MovieItemWithLoadingState[] } = $props();
	// bound to search input
	let usernameQuery: string = $state('');
	// holds state of querying watchlist, used for loading info
	let loadingWatchlist = $state(false);
	// holds state of querying streaming options, used for loading info
	// used for displaying the error
	let errorMessage: string = $state('');

	// abort controller to cancel previous requests
	let currentAbortController: AbortController | null = null;

	async function onsubmit() {
		loadingWatchlist = true;
		errorMessage = '';
		let username = usernameQuery; // .split(',')[0];

		if (currentAbortController) {
			currentAbortController.abort();
		}
		currentAbortController = new AbortController();
		// give every request the same signal
		const signal = currentAbortController.signal;

		// TODO: Add support for multiple users.
		// Query letterboxd watchlist api for each user.
		// Problem is: We need to load streaming options for both watchlists
		// Little Hack: Put username into result from backend, makes data handling easier here?
		// We could keep all movies in one list though with one attribute being the user
		// Just figure out how to filter out duplicates and an ugly intersect

		// Option one:
		//  Set username on every streaming option, bloaty but not accidentally removable
		// Option Two:
		//  New model: user and watchlist.
		//   If intersect, intersect both options
		//   If union, display set of all options
		try {
			const watchlistResponse = await fetch(
				`/api/watchlist?username=${encodeURIComponent(username)}`,
				{ signal }
			);
			if (!watchlistResponse.ok) {
				const errorData = await watchlistResponse.json().catch(() => ({}));

				switch (watchlistResponse.status) {
					case 404:
						throw new Error('Watchlist not found. Check the username.');
					case 422:
						throw new Error(errorData.detail || 'Invalid username format');
					case 424:
						throw new Error('Could not reach Letterboxd. Try again later.');
					default:
						throw new Error(errorData.detail || 'An unexpected error occurred');
				}
			}
			let movieItems: LetterboxdMovieItem[] = await watchlistResponse.json();
			watchlist = movieItems.map(
				(movie: LetterboxdMovieItem) =>
					({
						...movie,
						streaming_options: {},
						loadingState: 'idle',
						stateMessage: "",
					}) as MovieItemWithLoadingState
			);
		} catch (err: any) {
			errorMessage = err.message;
			watchlist = []
		} finally {
			loadingWatchlist = false;
		}
		try {
			watchlist = watchlist.map(
				(movie: MovieItemWithLoadingState) =>
					({
						...movie,
						loadingState: 'loading'
					}) as MovieItemWithLoadingState
			);

			watchlist.map(async (movie: MovieItemWithLoadingState, index: number) => {
				try {
					const response = await fetch(`/api/availability?movie_id=${movie.movie_id}`, { signal });

					if (!response.ok) {
						const errorData = await response.json().catch(() => ({}));

						switch (response.status) {
							case 404:
								throw new Error(errorData.detail);
							case 422:
								throw new Error(errorData.detail || 'Invalid username format');
							case 424:
								throw new Error('Could not reach Letterboxd. Try again later.');
							default:
								throw new Error(errorData.detail || 'An unexpected error occurred');
						}
					}


					const options = response.ok ? await response.json() : {};

					const updatedMovie: MovieItemWithLoadingState = {
						...movie,
						streaming_options: (Object.groupBy(options, (opt: StreamingOption) => opt.service.id) ||
							{}) as StreamingOptionsByService,
						loadingState: 'success'
					};

					watchlist = watchlist.map((m, i) => (i === index ? updatedMovie : m)); // updating via watchlist[index] fails to trigger reactivity
				} catch (error: any) {
					if (error.name === 'AbortError') {
						return;
					}
					// TODO: Maybe add error message here?
					const updatedMovie: MovieItemWithLoadingState = {
						...movie,
						streaming_options: {},
						loadingState: 'error',
						stateMessage: error.message
					};
					watchlist = watchlist.map((m, i) => (i === index ? updatedMovie : m));
				}
			});
		} catch (err: any) {
			errorMessage = err.message;
		}
	}
</script>

<form {onsubmit} class="mx-auto mb-6">
	<div class="flex flex-row">
		<input
			bind:value={usernameQuery}
			disabled={loadingWatchlist}
			name="query"
			placeholder="Username"
			required
			class="mr-4 w-full rounded-lg border border-gray-300 bg-gray-50 p-4 ps-10 text-lg text-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-blue-500 dark:focus:ring-blue-500"
		/>
		<button
			type="submit"
			class="end-2.5 bottom-3 rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 focus:outline-none dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
		>
			GO!
		</button>
	</div>
	{#if errorMessage}
		<div class="shake m-3 flex justify-center dark:text-white">{errorMessage}</div>
	{/if}
	{#if loadingWatchlist}
		<div class="m-3 flex justify-center dark:text-white">Loading Watchlist</div>
	{/if}
</form>

<style>
	@keyframes shake {
		0%,
		100% {
			transform: translateX(0);
		}
		10%,
		30%,
		50%,
		70%,
		90% {
			transform: translateX(-5px);
		}
		20%,
		40%,
		60%,
		80% {
			transform: translateX(5px);
		}
	}

	.shake {
		animation: shake 0.3s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
	}
</style>
