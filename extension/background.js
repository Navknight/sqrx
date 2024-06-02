let port = null;

function connect() {
    const hostName = 'com.abhinav.hyperlink';
    port = chrome.runtime.connectNative(hostName);
    port.onMessage.addListener(onNativeMessage);
    port.onDisconnect.addListener(onDisconnected);
    console.log('Connecting to native messaging host', hostName);
}

function onNativeMessage(message) {
    console.log('Received message from native app:', message);
}

function onDisconnected() {
    console.log('Disconnected from native app.');
    port = null;
}

const sendToNative = () => {
    chrome.storage.local.get(null, (items) => {
        console.log(items)
        const visited = items.visited || 0
        const hyperlinks = items.hyperlinks || 0
        const data = Object.keys(items).filter(key => key !== 'visited' && key !== 'hyperlinks').map(key => {
            return {
                [key] : items[key]
            }
        })
        console.log(data)

        const message = {data: data, visited: visited, hyperlinks: hyperlinks}
        
        if(port) {
            console.log('Sending message to native app:', message)
            port.postMessage(message)
        }
        else {
            console.error('Port is not connected')
        }
    })
}

chrome.runtime.onMessage.addListener((message, sender) => {
    if(message.action === 'update')
        sendToNative();
})

connect();