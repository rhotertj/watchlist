<script lang="ts">
	import { streamingColors } from '$lib/colors';
	import type {
		LetterboxdMovieItem,
		MovieItemWithLoadingState,
		StreamingOption,
		StreamingOptionsByService
	} from '$lib/types';
	// the movie we display, the services that the user subbed, interested in other than sub options
	let {
		movie,
		selectedServices,
		displaySubscriptionOnly
	}: {
		movie: MovieItemWithLoadingState;
		selectedServices: string[];
		displaySubscriptionOnly: boolean;
	} = $props();
	let imgLoadError = $state(false);
	import { Spinner } from 'flowbite-svelte';

	// background placeholder colors for posters that fail to load
	const posterColors = [
		'bg-blue-600',
		'bg-purple-600',
		'bg-green-600',
		'bg-red-600',
		'bg-indigo-600',
		'bg-pink-600',
		'bg-yellow-600',
		'bg-teal-600'
	];

	/*
    Some thoughts around displaying streaming options:
     - User selects his services and we keep the services unique names
     - User selects whether he wants sub-only options
     - We intersect all options with users choices
     - Services might have different options per movie:
        a) different types: subscription, addon (like prime channels), rent, buy
        b) different qualities: sd, hd, uhd, 4k etc.
     - We highlight the ones that match all selected filters of the user, rest is transparent/gray
    */

	function getColorForMissingPoster(title: string) {
		// pick pseudo random color based on title
		const hash = title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
		return posterColors[hash % posterColors.length];
	}

	function isSelectedOption(option: StreamingOption): boolean {
		// Check whether the given option is selected and fits selected subscription filter

		if (!selectedServices.includes(option.service.id)) {
			return false;
		}
		if (option.type != 'subscription' && displaySubscriptionOnly) {
			return false;
		}

		return true;
	}

	function isSelectedService(options: StreamingOption[]) {
		return options
			.filter((option: StreamingOption) => isSelectedOption(option))
			.some((b: StreamingOption) => b || false);
	}

	function orderStreamingOptionsBasedOnSelection(options: StreamingOptionsByService) {
		// options are grouped by services, first get the keys
		return Object.keys(options).toSorted((a: string, b: string) => {
			const aSelected = isSelectedService(options[a]) ? 1 : 0;
			const bSelected = isSelectedService(options[b]) ? 1 : 0;
			return bSelected - aSelected; // Selected items first
		});
	}
</script>

<div class="relative h-96 w-68 rounded-lg p-4">
	<a href={movie.movie_url} target="_blank" rel="noopener noreferrer" class="block h-full">
		{#if imgLoadError}
			<div
				class="h-full w-full {getColorForMissingPoster(
					movie.movie_name
				)} flex items-center justify-center rounded-lg border-4 border-transparent hover:border-blue-700"
			>
				<p class="text-center text-xl leading-tight text-wrap font-bold text-white">
					{movie.movie_name}
				</p>
			</div>
		{:else}
			<img
				class="h-full w-full rounded-lg border-4 border-transparent hover:border-blue-700"
				src="/api/poster/{movie.movie_slug}-{movie.movie_id}"
				alt={movie.movie_name}
				loading="lazy"
				onerror={() => (imgLoadError = true)}
			/>
		{/if}
	</a>
	<!-- Streaming Options overlay -->
	<div class="absolute top-6 right-6 flex flex-col py-2">
		{#if movie.loadingState === 'loading'}
			<div class="absolute top-0 right-0 p-2">
				<Spinner size="4" />
			</div>
			<!-- TODO: Add error message for movie, eg. api limit exceeded -->
		{:else if movie.loadingState === 'error'}
			<div class="absolute top-0 right-0 rounded bg-red-500 p-2 text-xs text-white">
				{movie.stateMessage || "Loading Error"}
			</div>
		{:else if Object.keys(movie.streaming_options).length === 0 && movie.loadingState == 'success'}
			<div class="absolute top-0 right-0 rounded bg-gray-500 p-2 text-xs text-white">
				Not available
			</div>
		{:else if Object.keys(movie.streaming_options).length > 0 && movie.loadingState == 'success'}
			<!-- Sort streaming options by availability, selected ones are first -->
			{#each orderStreamingOptionsBasedOnSelection(movie.streaming_options) as serviceKey}
				<!-- Display all services, highlight selected ones -->
				<a
					href={movie.streaming_options[serviceKey][0].link}
					target="_blank"
					rel="noopener noreferrer"
					class="rounded px-2 text-sm font-semibold shadow-lg {isSelectedService(
						movie.streaming_options[serviceKey]
					)
						? 'text-white'
						: 'bg-gray-600 text-gray-300 opacity-50 grayscale'}  bg-{streamingColors[
						serviceKey
					]}-600"
					onclick={(e) => e.stopPropagation()}
				>
					{movie.streaming_options[serviceKey][0].service.name}
				</a>
				<div
					class="mb-1 flex flex-row-reverse rounded px-2 text-xs font-semibold {isSelectedService(
						movie.streaming_options[serviceKey]
					)
						? 'text-white'
						: 'bg-gray-600 text-gray-300 opacity-50 grayscale'}  bg-{streamingColors[
						serviceKey
					]}-600"
				>
					<!-- filter by display critera, then group by type to eliminate HD/SD/UHD duplicates, then get keys to have array format -->
					{#each Object.keys(Object.groupBy( movie.streaming_options[serviceKey].filter( (option: StreamingOption) => isSelectedOption(option) ), (option: StreamingOption) => option.type )) as streamingType}
						<div class="pl-1">{streamingType}</div>
					{/each}
				</div>
			{/each}
		{/if}
	</div>
</div>
