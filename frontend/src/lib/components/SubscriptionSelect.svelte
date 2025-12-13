<script lang="ts">
	import { MultiSelect, Badge } from 'flowbite-svelte';

	// all available streaming options for DE
	// see https://docs.movieofthenight.com/guide/countries-and-services#germany
	let streamingOptions = [
		{ value: 'prime', name: 'Prime Video', color: 'indigo' },
		{ value: 'apple', name: 'Apple TV', color: 'gray' },
		{ value: 'paramount', name: 'Paramount+', color: 'sky' },
		{ value: 'netflix', name: 'Netflix', color: 'red' },
		{ value: 'disney', name: 'Disney+', color: 'cyan' },
		{ value: 'mubi', name: 'Mubi', color: 'indigo' },
		{ value: 'discovery', name: 'Discovery+', color: 'amber' },
		{ value: 'zee5', name: 'Zee5', color: 'teal' },
		{ value: 'curiosity', name: 'Curiosity Stream', color: 'orange' },
		{ value: 'wow', name: 'WOW', color: 'red' },
		{ value: 'plutotv', name: 'Pluto TV', color: 'gray' }
	];
	// propagates selection to parent
	let { multiSelected = $bindable() } = $props();
</script>

<MultiSelect
	placeholder="Choose your streaming services."
	items={streamingOptions}
	bind:value={multiSelected}
	class="dark:border-gray-600 dark:bg-gray-800 dark:text-white"
	classes={{ dropdown: 'dark:bg-gray-800 dark:text-white dark:border-gray-600' }}
>
	{#snippet children({ item, clear })}
		<Badge
			color={item.color}
			dismissable
			params={{ duration: 100 }}
			onclose={clear}
			class="mx-0.5 dark:ring-1 dark:ring-gray-600"
		>
			{item.name}
		</Badge>
	{/snippet}
</MultiSelect>
