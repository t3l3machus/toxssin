# toxssin  
[![Python 3.x](https://img.shields.io/badge/python-3.x-yellow.svg)](https://www.python.org/) ![JavaScript](https://img.shields.io/badge/-JavaScript-blue) [![License](https://img.shields.io/badge/license-MIT-red.svg)](https://github.com/t3l3machus/toxssin/blob/main/LICENSE.md)
## Purpose

Toxssin is a tool for exploiting XSS vulnerabilities, consisting of a python server (toxssin.py) and its coresponding malicious JavaScript payload (toxin.js).
Toxssin is a project that aims to assist the exploitation of XSS vulnerabilities 

## Capabilities  
By default, toxssin intercepts:
- cookies,
- keystrokes,
- paste events,
- input change events,
- file selections,
- form submissions,
- server responses,
- table data (static as well as updates),

Most importantly, toxssin:
- attempts to maintain XSS persistence while the user browses the website by intercepting server responses and re-writing the document,
- supports session management, meaning that, you can use it to exploit reflected as well as stored XSS,
- automatically logs every session.

## Installation & Configuration
```
git clone https://github.com/t3l3machus/toxssin
cd ./toxssin
pip3 install -r requirements
```  
To start toxssin.py, you will need to supply certificate and private key files.

You can issue self-signed certificates with the following command:  
```
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
```

It is strongly recommended to start the toxssin server with a trusted certificate (see [How to get a Valid Certificate](#How-to-get-a-Valid-Certificate) in this document).

## XSS Exploitation Obstacles
In my experience, there are 3 major obstacles when it comes to Cross-Site Scripting attacks attempting to include external JS scripts:
1. the "Mixed Content" error, which can be resolved by serving the JavaScript payload via https (even with a self-signed certificate).
2. the "NET::ERR_CERT_AUTHORITY_INVALID" error, which indicates that the server's certificate is untrusted / expired and can be bypassed by using a certificate from a valid Authorit.
3. Cross-origin resource sharing (CORS), which is handled appropriately by toxssin.

**Note**: The "Mixed Content" error can of course occur when the target website is hosted via http and the JavaScript payload via https. This limits the scope of toxssin to https only webistes, as (by default) toxssin is started with ssl only.

Securing cookies with httponly and secure flags
In order to succesfully execute toxin.js 

## How to get a Valid Certificate
First, you need to own a domain name. The fastest and most economic way to get one (in my knowledge) is via a cheap domain registrar service (e.g.  https://www.namecheap.com/). Search for a random string domain name (e.g. "fvcm98duf") and check the less popular TLDs, like .xyz, as they will probably cost around 3$ per year.

After you purchase a domain name, you can use certbot (Let's Encrypt) to get a trusted certificate in 5 minutes or less:
1. Append an A record to your Domain's DNS settings so that it points to your server ip,
2. Follow certbots [official instructions](https://certbot.eff.org/instructions).  

**Tip**: Don't install and run certbot on your own, you might get unexpected errors. Stick with the instructions.

## Future 
