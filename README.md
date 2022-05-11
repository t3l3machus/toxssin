# toxssin
## Purpose
Toxssin is a tool for exploiting XSS vulnerabilities, consisting of a python server (toxssin.py) and its coresponding malicious JavaScript payload (toxin.js).
Toxssin is a project that aims to assist the exploitation of XSS vulnerabilities 

## Requirements
As you probably know, there are 3 major obstacles when it comes to Cross-Site Scripting attacks attempting to include external JS scripts:
1. the "Mixed Content" (browser) error, which can be resolved by serving the JavaScript payload via https (even with a self-signed certificate),
2. the "NET::ERR_CERT_AUTHORITY_INVALID" error, which indicates that the server's certificate is untrusted / expired and can be easily bypassed by getting a certificate from a valid Authority,  
3. CORS which can be bypassed if certain misconfigurations are present (althought, most CORS settings will not interfere with a script tag loading an external script, from a valid source).

Securing cookies with httponly and secure flags
In order to succesfully execute toxin.js 

## How to get a Valid Certificate
First you need to own a domain. The fastest and cheapest way to get one (im my knowledge) is through https://www.namecheap.com/domains/
Search for a random string domain name (e.g. "fvcm98duf") and check the less popular TLDs like .xyz as they will probably cost 1$ - 3$ for a year.

After you get a domain name you can use certbot (Let's Encrypt) to get a trusted certificate in 5 minutes:
1. Append an A record to your Domain's DNS settings so that it points to your server ip,
2. Follow certbots [official instructions](https://certbot.eff.org/instructions). Don't install and run certbot on your own, you might get unexpected errors. Stick with the instructions.

## Installation 
