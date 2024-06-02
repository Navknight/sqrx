const extractLinks = () => {
    const links = [...document.querySelectorAll('a')].map(link => link.href)
    const host = window.location.hostname
    console.log(host)

    chrome.storage.local.get([host, 'visited', 'hyperlinks'], (result) => {
        console.log(result)
        if(!result[host])
            result.visited++

        let data = result[host] || {}
        let hyperlinks = result.hyperlinks? result.hyperlinks : 0
        links.forEach(link => {
            if(data[link] && data[link] !== '')
                data[link]++
            else {
                data[link] = 1
                hyperlinks++
            }
        })

        chrome.storage.local.set({
            [host]: data,
            visited: result.visited ? result.visited++ : 1,
            hyperlinks: hyperlinks
        }, () => {
            chrome.runtime.sendMessage({action: "update"})
        })
    })
}

extractLinks()

const observer  = new MutationObserver(extractLinks)
observer.observe(document.body, {
    childList: true,
    subtree: true
})