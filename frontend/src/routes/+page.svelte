<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { calculateDistance } from '$lib/services/api';

	let sourceAddress = $state('415 Mission St Suite 4800, San Francisco, CA 94105');
	let destinationAddress = $state('3223 Hanover St Suite 110, Palo Alto, CA 94304');
	let selectedUnit = $state('both');
	let result = $state<{ miles: number; km: number } | null>(null);
	let isLoading = $state(false);
	let error = $state<string | null>(null);

	// Computed property for button disabled state
	let isButtonDisabled = $derived(!sourceAddress.trim() || !destinationAddress.trim() || isLoading);

	// Handle URL parameters for prefilling data
	onMount(() => {
		const urlParams = new URLSearchParams($page.url.search);
		const source = urlParams.get('source');
		const destination = urlParams.get('destination');
		const miles = urlParams.get('miles');
		const km = urlParams.get('km');

		if (source) sourceAddress = source;
		if (destination) destinationAddress = destination;
		if (miles && km) {
			result = {
				miles: parseFloat(miles),
				km: parseFloat(km)
			};
		}

		// Clean URL after loading data
		if (urlParams.has('source') || urlParams.has('destination')) {
			window.history.replaceState({}, '', '/');
		}
	});

	async function handleCalculateDistance() {
		isLoading = true;
		error = null;

		try {
			const response = await calculateDistance(sourceAddress, destinationAddress);

			// Convert API response to our display format
			const distanceKm = response.distance_km || 0;
			const distanceMiles = distanceKm * 0.621371; // Convert km to miles

			result = {
				miles: parseFloat(distanceMiles.toFixed(2)),
				km: parseFloat(distanceKm.toFixed(2))
			};
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to calculate distance';
		} finally {
			isLoading = false;
		}
	}

	function dismissError() {
		error = null;
	}

	function goToHistory() {
		goto('/history');
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
				onclick={goToHistory}
				class="bg-secondary hover:bg-opacity-90 flex cursor-pointer items-center gap-2 rounded-md px-6 py-6 text-white transition-colors"
			>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
					></path>
				</svg>
				View Historical Queries
			</button>
		</nav>
	</div>
</header>

<!-- Main Content -->
<main class="px-12 pb-16">
	<div class="space-y-8">
		<!-- Input Section -->
		<div class="rounded-lg bg-white p-6 shadow-sm">
			<div class="flex flex-col gap-6 lg:flex-row">
				<!-- Address Fields -->
				<div class="grid flex-1 grid-cols-1 gap-4 md:grid-cols-2">
					<div>
						<label for="source" class="text-label mb-2 block text-sm font-medium"
							>Source Address</label
						>
						<input
							id="source"
							type="text"
							bind:value={sourceAddress}
							placeholder="Input address"
							class="border-input text-text placeholder-input focus:ring-primary w-full rounded-md border bg-gray-50 px-3 py-2 focus:border-transparent focus:ring-2 focus:outline-none"
						/>
					</div>
					<div>
						<label for="destination" class="text-label mb-2 block text-sm font-medium"
							>Destination Address</label
						>
						<input
							id="destination"
							type="text"
							bind:value={destinationAddress}
							placeholder="Input address"
							class="border-input text-text placeholder-input focus:ring-primary w-full rounded-md border bg-gray-50 px-3 py-2 focus:border-transparent focus:ring-2 focus:outline-none"
						/>
					</div>
				</div>

				<!-- Unit Selection -->
				<div class="lg:w-48">
					<fieldset>
						<legend class="text-label mb-2 block text-sm font-medium">Units</legend>
						<div class="space-y-2">
							<label class="flex cursor-pointer items-center">
								<input
									type="radio"
									bind:group={selectedUnit}
									value="miles"
									class="text-primary focus:ring-primary cursor-pointer"
								/>
								<span class="text-text ml-2">Miles</span>
							</label>
							<label class="flex cursor-pointer items-center">
								<input
									type="radio"
									bind:group={selectedUnit}
									value="kilometers"
									class="text-primary focus:ring-primary cursor-pointer"
								/>
								<span class="text-text ml-2">Kilometers</span>
							</label>
							<label class="flex cursor-pointer items-center">
								<input
									type="radio"
									bind:group={selectedUnit}
									value="both"
									class="text-primary focus:ring-primary cursor-pointer"
								/>
								<span class="text-text ml-2">Both</span>
							</label>
						</div>
					</fieldset>
				</div>

				<!-- Distance Section -->
				<div class="lg:w-48">
					<div class="text-label mb-2 block text-sm font-medium">Distance</div>
					{#if result}
						<div class="text-text space-y-1 text-2xl font-bold">
							{#if selectedUnit === 'miles' || selectedUnit === 'both'}
								<div>{result.miles} mi</div>
							{/if}
							{#if selectedUnit === 'kilometers' || selectedUnit === 'both'}
								<div>{result.km} km</div>
							{/if}
						</div>
					{:else}
						<div class="text-label text-sm">Results will appear here</div>
					{/if}
				</div>
			</div>

			<!-- Calculate Button -->
			<div class="mt-6">
				<button
					onclick={handleCalculateDistance}
					disabled={isButtonDisabled}
					class="flex items-center gap-2 rounded-md px-6 py-3 transition-colors"
					class:cursor-pointer={!isButtonDisabled}
					class:cursor-not-allowed={isButtonDisabled}
					class:bg-primary={!isButtonDisabled}
					class:text-white={!isButtonDisabled}
					class:hover:bg-opacity-90={!isButtonDisabled}
					class:bg-gray-400={isButtonDisabled}
					class:text-gray-600={isButtonDisabled}
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
						></path>
					</svg>
					{isLoading ? 'Calculating...' : 'Calculate Distance'}
				</button>
			</div>
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
			<div class="font-semibold">Calculation failed</div>
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
