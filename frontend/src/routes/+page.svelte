<script lang="ts">
	import type { LetterboxdMovieItem, MovieItemWithLoadingState, StreamingOption } from '$lib/types';
	import MoviePoster from '$lib/components/MoviePoster.svelte';
	import SearchBar from '$lib/components/SearchBar.svelte';
	import SubscriptionSelect from '$lib/components/SubscriptionSelect.svelte';
	import { Toggle } from 'flowbite-svelte';
	import { flip } from 'svelte/animate';
	import { fade } from 'svelte/transition';

	// holds state from search bar to implement intersection
	let usernames: string[] = $state([]);
	// keeps track of movies in watchlist
	let watchlist: MovieItemWithLoadingState[] = $state([]);
	// selected streaming services
	let selectedServices: string[] = $state([]);
	// whether the user is also interested in buy-rent-addon offers
	let displaySubscriptionOnly: boolean = $state(false);
	// whether we intersect watchlists instead of building the union
	let intersectWatchlists: boolean = $state(false);
	let intersectedWatchlist: MovieItemWithLoadingState[] = $derived(
		intersectWatchlists
			? watchlist.filter(
					(movie: MovieItemWithLoadingState) => movie.users.length == usernames.length
				)
			: watchlist
	);

	// We need to hold off the animations a bit
	let sortTimeout: number | undefined;
	let stableOrderedWatchlist: MovieItemWithLoadingState[] = $state([]);
	$effect(() => {
		intersectedWatchlist;
		selectedServices;
		displaySubscriptionOnly;
		clearTimeout(sortTimeout);
		sortTimeout = window.setTimeout(() => {
			stableOrderedWatchlist = intersectedWatchlist.toSorted(
				(a: MovieItemWithLoadingState, b: MovieItemWithLoadingState) => {
					const aMatches = countStreamingOptionsOfInterest(a) || 0;
					const bMatches = countStreamingOptionsOfInterest(b) || 0;
					return bMatches - aMatches;
				}
			);
		}, 200);
	});

	function countStreamingOptionsOfInterest(movie: LetterboxdMovieItem | MovieItemWithLoadingState) {
		/* How we count:
            We want to sort a watchlist based on selectedServices & subonly intersecting available options
            streaming_options are grouped by service {"amazon":  [...], "nextflix": [...]}
            To count options of interest, we need to check all services and their options and rate each one by
             a) is the service selected?
             b) is the type of service a subscription and are we interested in subs only?
            Sum all fitting ones.
        */
		if (Object.values(movie.streaming_options).length == 0) {
			return 0;
		}
		// All streaming options, flat reverses grouping by service
		return Object.values(movie.streaming_options)
			.flat(1)
			.filter(
				(options: StreamingOption) =>
					selectedServices.includes(options.service.id) &&
					!(options.type != 'subscription' && displaySubscriptionOnly)
			).length;
	}
</script>

<div class="outer-container flex flex-col items-center">
	<h1
		class="logo w-full justify-center pt-10 pb-12 text-center text-4xl font-bold md:pt-30 md:text-6xl dark:text-white"
	>
		Watchlist Availability
	</h1>
	<div class="search-container">
		<!-- Input of username and querying of watchlist API & movieofthenight API -->
		<SearchBar bind:watchlist bind:usernames />
	</div>
	<div class="flex w-full flex-col gap-4 px-4 md:w-auto md:flex-row md:items-center">
		<!-- Selection of filters -->
		<SubscriptionSelect bind:multiSelected={selectedServices} />
		<Toggle class="pr-2 pl-4 dark:text-gray-400" bind:checked={displaySubscriptionOnly}
			>Subscriptions only</Toggle
		>
		<Toggle class="pl2 pr-4 dark:text-gray-400" bind:checked={intersectWatchlists}
			>Intersect watchlists</Toggle
		>
	</div>
	<div class="result-container flex w-3/4 flex-row flex-wrap justify-center py-3">
		<!-- Grid (actually flex) of movie posters with streaming option ribbons -->
		{#each stableOrderedWatchlist as movie (movie.movie_id)}
			<div animate:flip={{ duration: 800 }} in:fade={{ duration: 1200 }}>
				<MoviePoster {movie} {selectedServices} {displaySubscriptionOnly} />
			</div>
		{/each}
	</div>
</div>
