/**
 * TabStash - Client-side search with MiniSearch
 */

(function() {
    let miniSearch = null;
    let searchData = [];

    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('search-results');
    const tabList = document.getElementById('tab-list');

    if (!searchInput) return;

    // Load search index
    fetch('/search-index.json')
        .then(response => response.json())
        .then(data => {
            searchData = data;

            miniSearch = new MiniSearch({
                fields: ['title', 'artist', 'tags'],
                storeFields: ['title', 'artist', 'url', 'tags'],
                searchOptions: {
                    boost: { title: 2, artist: 1.5 },
                    fuzzy: 0.2,
                    prefix: true,
                }
            });

            miniSearch.addAll(data);
        })
        .catch(err => {
            console.error('Failed to load search index:', err);
        });

    // Debounce helper
    function debounce(fn, delay) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    // Render search results
    function renderResults(results) {
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-result-item"><span class="search-result-title">No results found</span></div>';
            searchResults.classList.add('active');
            return;
        }

        const html = results.slice(0, 10).map(result => `
            <a href="${result.url}" class="search-result-item">
                <span class="search-result-title">${escapeHtml(result.title)}</span>
                <span class="search-result-artist">${escapeHtml(result.artist)}</span>
            </a>
        `).join('');

        searchResults.innerHTML = html;
        searchResults.classList.add('active');
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Filter the tab list (fallback when no results dropdown needed)
    function filterTabList(query) {
        if (!tabList) return;

        const items = tabList.querySelectorAll('.tab-item');
        const lowerQuery = query.toLowerCase();

        items.forEach(item => {
            const id = item.dataset.id || '';
            const title = item.querySelector('.tab-title')?.textContent || '';
            const artist = item.querySelector('.tab-artist')?.textContent || '';

            const matches = !query ||
                title.toLowerCase().includes(lowerQuery) ||
                artist.toLowerCase().includes(lowerQuery);

            item.classList.toggle('hidden', !matches);
        });
    }

    // Handle search input
    const handleSearch = debounce(function(e) {
        const query = e.target.value.trim();

        if (!query) {
            searchResults.classList.remove('active');
            filterTabList('');
            return;
        }

        if (miniSearch) {
            const results = miniSearch.search(query);
            renderResults(results);
        }

        filterTabList(query);
    }, 150);

    searchInput.addEventListener('input', handleSearch);

    // Close results on click outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('active');
        }
    });

    // Close results on Escape
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            searchResults.classList.remove('active');
            searchInput.blur();
        }
    });
})();
