<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { getHistory, type HistoryItem } from '$lib/services/api';

	// State management
	let historyData: HistoryItem[] = $state([]);
	let isLoading = $state(true);
	let error = $state<string | null>(null);
	let hasMore = $state(false);
	let currentOffset = $state(0);
	const limit = 10;

	// Load history data on mount
	onMount(() => {
		loadHistory();
	});

	async function loadHistory(offset = 0) {
		if (offset === 0) {
			isLoading = true;
			historyData = [];
		}
		error = null;

		try {
			const response = await getHistory({
				limit,
				offset,
				sort_by: 'created_at',
				sort_order: 'desc'
			});

			if (offset === 0) {
				historyData = response.items;
			} else {
				historyData = [...historyData, ...response.items];
			}

			hasMore = response.has_more;
			currentOffset = offset + response.items.length;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load history';
		} finally {
			isLoading = false;
		}
	}

	function loadMore() {
		loadHistory(currentOffset);
	}

	function dismissError() {
		error = null;
	}

	function backToCalculator() {
		goto('/');
	}

	function selectHistoryItem(item: HistoryItem) {
		// Navigate to calculator with data in URL params
		const distanceKm = item.distance_km || 0;
		const distanceMiles = distanceKm * 0.621371; // Convert km to miles

		const params = new URLSearchParams({
			source: item.source_address,
			destination: item.destination_address,
			miles: distanceMiles.toFixed(2),
			km: distanceKm.toFixed(2)
		});
		goto(`/?${params.toString()}`);
	}
</script>

<!-- Header -->
<header class="w-full px-12 py-12">
	<div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
		<div>
			<h1 class="text-text mb-2 text-5xl font-medium">Distance Calculator</h1>
			<p class="text-label text-lg">
				Prototype web application for calculating the distance between addresses.
			</p>
		</div>

		<nav class="flex gap-4">
			<button
				onclick={backToCalculator}
				class="border-secondary bg-background text-text hover:bg-secondary flex cursor-pointer items-center gap-2 rounded-md border-2 px-6 py-6 transition-colors hover:text-white"
			>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 19l-7-7m0 0l7-7m-7 7h18"
					></path>
				</svg>
				Back to Calculator
			</button>
		</nav>
	</div>
</header>

<!-- Main Content -->
<main class="px-12 pb-16">
	<div class="space-y-8">
		<!-- History Section -->
		<div class="overflow-hidden rounded-lg bg-white shadow-sm">
			<!-- Section Header -->
			<div class="border-b border-gray-200 px-6 py-4">
				<h2 class="text-text mb-1 text-2xl font-semibold">Historical Queries</h2>
				<p class="text-label text-sm">History of the user's queries.</p>
			</div>

			<!-- History Table -->
			{#if isLoading}
				<div class="text-label p-8 text-center">
					<div class="flex items-center justify-center gap-2">
						<svg class="text-primary h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
						<span>Loading history...</span>
					</div>
				</div>
			{:else if historyData.length === 0}
				<div class="text-label p-8 text-center">
					<p class="text-lg">No historical queries found.</p>
					<p class="mt-2 text-sm">Start calculating distances to see your history here.</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead class="border-b border-gray-200 bg-gray-50">
							<tr>
								<th
									class="text-label px-6 py-4 text-left text-xs font-semibold tracking-wider uppercase"
								>
									Source Address
								</th>
								<th
									class="text-label px-6 py-4 text-left text-xs font-semibold tracking-wider uppercase"
								>
									Destination Address
								</th>
								<th
									class="text-label px-6 py-4 text-left text-xs font-semibold tracking-wider uppercase"
								>
									Distance in Miles
								</th>
								<th
									class="text-label px-6 py-4 text-left text-xs font-semibold tracking-wider uppercase"
								>
									Distance in Kilometers
								</th>
								<th
									class="text-label px-6 py-4 text-left text-xs font-semibold tracking-wider uppercase"
								>
									Date
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white">
							{#each historyData as item (item.id)}
								<tr class="cursor-pointer hover:bg-gray-50" onclick={() => selectHistoryItem(item)}>
									<td class="text-text max-w-xs truncate px-6 py-4 text-sm">
										{item.source_address}
									</td>
									<td class="text-text max-w-xs truncate px-6 py-4 text-sm">
										{item.destination_address}
									</td>
									<td class="text-text px-6 py-4 text-sm font-medium">
										{item.distance_km ? (item.distance_km * 0.621371).toFixed(2) : 'N/A'} mi
									</td>
									<td class="text-text px-6 py-4 text-sm font-medium">
										{item.distance_km ? item.distance_km.toFixed(2) : 'N/A'} km
									</td>
									<td class="text-label px-6 py-4 text-sm">
										{new Date(item.created_at).toLocaleDateString()}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Load More Button -->
				{#if hasMore}
					<div class="border-t border-gray-200 px-6 py-4 text-center">
						<button
							onclick={loadMore}
							disabled={isLoading}
							class="bg-secondary hover:bg-opacity-90 rounded-md px-4 py-2 text-white transition-colors disabled:cursor-not-allowed disabled:opacity-50"
						>
							{isLoading ? 'Loading...' : 'Load More'}
						</button>
					</div>
				{/if}
			{/if}
		</div>
	</div>
</main>

<!-- Error Notification -->
{#if error}
	<div
		class="fixed right-4 bottom-4 flex max-w-sm items-start gap-3 rounded-md bg-red-500 p-4 text-white shadow-lg"
	>
		<div class="flex-shrink-0">
			<div class="flex h-6 w-6 items-center justify-center rounded-full bg-white">
				<svg class="h-4 w-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
					<path
						fill-rule="evenodd"
						d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
						clip-rule="evenodd"
					></path>
				</svg>
			</div>
		</div>
		<div class="flex-1">
			<div class="font-semibold">Failed to load history</div>
			<div class="text-sm opacity-90">{error}</div>
		</div>
		<button
			onclick={dismissError}
			class="cursor-pointer text-white hover:text-gray-200"
			aria-label="Dismiss error"
		>
			<svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
				<path
					fill-rule="evenodd"
					d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
					clip-rule="evenodd"
				></path>
			</svg>
		</button>
	</div>
{/if}
