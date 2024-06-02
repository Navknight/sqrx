document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('detailsBody')

    chrome.storage.local.get(null, (items) => {
        // tbody.innerHTML=  ''
        console.log(items)

        Object.keys(items).forEach((key, index) => {
            if (key !== 'visited' && key !== 'hyperlinks') {
                Object.keys(items[key]).forEach((link, index) => {
                    const tr = document.createElement('tr')
                    const hostTd = document.createElement('td')
                    const linkTd = document.createElement('td')
                    const freqTd = document.createElement('td')

                    hostTd.textContent = index === 0 ? key : ''
                    linkTd.textContent = link
                    freqTd.textContent = items[key][link]

                    tr.appendChild(hostTd)
                    tr.appendChild(linkTd)
                    tr.appendChild(freqTd)

                    tbody.appendChild(tr)
                })
            }
        })
    })
})