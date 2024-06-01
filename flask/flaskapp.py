from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
import os
import json
from dotenv import load_dotenv
from flask_sock import Sock

load_dotenv()
WHOISAPI = os.getenv('WHOISAPI')
app = Flask(__name__)
sock = Sock(app)

@app.route("/")
def index():
    url = request.args.get('url', '')
    if not url:
        return 'Please provide a URL'

    info = get_domain_info(url)
    subdomains = get_subdomains(url)
    asset_domains = get_asset_domains(url)

    response = {
        "info": info,
        "subdomains": subdomains,
        "asset_domains": asset_domains
    }

    return jsonify(response)

def get_domain_info(url):
    url = url.split('://')[-1]
    ip_info = requests.get(f"https://ip-geolocation.whoisxmlapi.com/api/v1?apiKey={WHOISAPI}&domain={url}").json()
    org_info = requests.get(f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={WHOISAPI}&domainName={url}&outputFormat=JSON").json()
    return {
        "ip": ip_info.get('ip'),
        "isp": ip_info.get('isp'),
        "organization": org_info.get('WhoisRecord', {}).get('registrant', {}).get('organization'),
        "asn": ip_info.get('as', {}).get('asn'),
        "location": ip_info.get('location', {}).get('country')
    }

def get_subdomains(url):
    url = url.split('://')[-1]
    subdomain_info = requests.get(f"https://subdomains.whoisxmlapi.com/api/v1?apiKey={WHOISAPI}&domainName={url}").json()
    return [record['domain'] for record in subdomain_info.get('result', {}).get('records', [])]

def get_asset_domains(url):
    url = "https://" + url if not url.startswith('http') else url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return {
        "javascripts": [script['src'] for script in soup.find_all('script', src=True) if script['src'].startswith('http')],
        "stylesheets": [link['href'] for link in soup.find_all('link', rel='stylesheet') if link['href'].startswith('http')],
        "images": [img['src'] for img in soup.find_all('img') if img['src'].startswith('http')],
        "iframes": [iframe['src'] for iframe in soup.find_all('iframe') if iframe['src'].startswith('http')],
        "anchors": [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
    }

@sock.route('/ws')
def socket(ws):
    url = None
    while True:
        message = ws.receive()
        if not message:
            break
        message = json.loads(message)
        response = {}
        if 'url' in message:
            url = message['url']
            response = {"data": f"session created for {url}"}
        elif 'operation' in message:
            if url is None:
                response = {"error": "URL not set"}
            else:
                if message['operation'] == 'get_info':
                    response = {"data": get_domain_info(url)}
                elif message['operation'] == 'get_subdomains':
                    response = {"data": get_subdomains(url)}
                elif message['operation'] == 'get_asset_domains':
                    response = {"data": get_asset_domains(url)}
                else:
                    response = {"error": "Invalid operation"}
        else:
            response = {"error": "Invalid request"}
        
        ws.send(json.dumps(response))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
