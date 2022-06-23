
//This script is completely lame and you should NOT use it!!!

function scare(){

  let trans = `\
	html {background: url(https://www.denofgeek.com/wp-content/uploads/2022/01/scr14979r.jpg?fit=1800%2C1000);}\
\
	.xlD9f3eDf {\
	  transition: all 0.5s linear 0s;\
	  transform: scale(0);\
	  opacity: 0;
	}\
`

    var styleSheet = document.createElement("style");
    styleSheet.innerText = trans;
    document.head.appendChild(styleSheet)
    document.getElementsByTagName("body")[0].classList.add("xlD9f3eDf");

    setTimeout(() => {
	alert(`Run.`)
    },  1600);

    return 'Scare transformation completed!';
}

scare();
