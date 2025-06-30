<script lang="ts">
	import '../app.css';

	let { children } = $props();
</script>

<div class="bg-background min-h-screen">
	{@render children()}
</div>
