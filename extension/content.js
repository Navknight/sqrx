let debounceTimer;

const extractLinks = () => {
    const links = [...document.querySelectorAll('a')].filter(link => !link.hasAttribute('data-tracked-by-hyperlinktracker')).filter(link => link.href);
    const host = window.location.hostname;
    let newLinks = {};

    links.forEach(link => {
        const href = link.href;
        newLinks[href] = (newLinks[href] || 0) + 1;
        link.setAttribute('data-tracked-by-hyperlinktracker', 'true');
    });

    if (Object.keys(newLinks).length > 0) {
        chrome.storage.local.get([host, 'visited', 'hyperlinks'], (result) => {
            let visited = result.visited || 0;
            if (!result[host]) visited++;

            let data = result[host] || {};
            let hyperlinks = result.hyperlinks || 0;

            for (const [link, count] of Object.entries(newLinks)) {
                data[link] = (data[link] || 0) + count;
                hyperlinks += count;
            }

            chrome.storage.local.set({
                [host]: data,
                visited: visited,
                hyperlinks: hyperlinks
            }, () => {
                chrome.runtime.sendMessage({ action: "update", host: host});
            });
        });
    }
};

const debouncedExtractLinks = () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(extractLinks, 500); // Adjust the debounce time as needed
};

extractLinks();

const observer = new MutationObserver(debouncedExtractLinks);
observer.observe(document.body, {
    childList: true,
    subtree: true
});
