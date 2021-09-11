
let _element;

//name="robots", content="noindex"
_element = document.createElement('meta');
_element.name = "robots"
_element.content = "noindex"
document.getElementsByTagName('head')[0].appendChild(_element);

//<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
_element = document.createElement('link');
_element.rel = "icon";
_element.type = "image/png";
_element.href = "/assets/img/logo_1140x1140.png"
document.getElementsByTagName('head')[0].appendChild(_element);

//<link rel="apple-touch-icon" sizes="152x152" href="/apple-icon-152x152.png">
_element = document.createElement('link');
_element.rel = "apple-touch-icon";
_element.type = "image/png";
_element.sizes = "152x152";
_element.href = "/assets/img/logo_1140x1140.png";
document.getElementsByTagName('head')[0].appendChild(_element);


//<link rel="preconnect" href="https://fonts.gstatic.com">
//<link rel="preload" href="/fonts/my-font.woff2" as="font">
// MDN example
//<link rel="preload" href="style.css" as="style">
//<link rel="preload" href="main.js" as="script">
//
//<link rel="stylesheet" href="style.css"></link>
// ...
//<script src="main.js" defer></script>
//</body>

// var preloadLink = document.createElement("link");
// preloadLink.href = "myscript.js";
// preloadLink.rel = "preload";
// preloadLink.as = "script";
// document.head.appendChild(preloadLink);
// ...
// var preloadedScript = document.createElement("script");
// preloadedScript.src = "myscript.js";
// document.body.appendChild(preloadedScript);


//<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Two+Tone" rel="stylesheet"></link>
_element = document.createElement('link');
_element.rel = "stylesheet";
_element.href = "https://fonts.googleapis.com/icon?family=Material+Icons+Two+Tone&display=swap";
document.getElementsByTagName('head')[0].appendChild(_element);

//<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"></link>
_element = document.createElement('link');
_element.rel = "stylesheet";
_element.href = "https://fonts.googleapis.com/icon?family=Material+Icons&display=swap";
document.getElementsByTagName('head')[0].appendChild(_element);


//"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
_element = document.createElement('script');
_element.src = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML";
document.getElementsByTagName('head')[0].appendChild(_element);


//
// Date 포맷 함수 : 로컬시간을 ISO 포맷의 문자열로 반환
//
function toLocalISOString(d) {
    var z  = n =>  ('0' + n).slice(-2);
    var zz = n => ('00' + n).slice(-3);
    var off = d.getTimezoneOffset();
    var sign = off < 0? '+' : '-';
    off = Math.abs(off);
  
    return d.getFullYear() + '-'
           + z(d.getMonth()+1) + '-' +
           z(d.getDate()) + 'T' +
           z(d.getHours()) + ':'  + 
           z(d.getMinutes()) + ':' +
           z(d.getSeconds()) + '.' +
           zz(d.getMilliseconds()) +
           sign + z(off/60|0) + ':' + z(off%60); 
}
