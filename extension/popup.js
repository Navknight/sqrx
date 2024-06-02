document.addEventListener('DOMContentLoaded', () => {
    const statsElem = document.getElementById('stats')
    const detailsButton = document.getElementById('detailsButton')

    chrome.storage.local.get(['visited', 'hyperlinks'], (results) => {
        statsElem.textContent = `Visited: ${results.visited}, Hyperlinks: ${results.hyperlinks}`
    })

    detailsButton.addEventListener('click', () => {
        chrome.tabs.create({url: chrome.runtime.getURL('details.html')})
    })
})