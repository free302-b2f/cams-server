
var meta;

//name="robots", content="noindex"
meta = document.createElement('meta');
meta.name = "robots"
meta.content = "noindex"
document.getElementsByTagName('head')[0].appendChild(meta);

//<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
var link = document.createElement('link');
link.rel = "icon";
link.type = "image/png";
link.href = "/assets/logo_1140x1140.png"
document.getElementsByTagName('head')[0].appendChild(link);

//<link rel="apple-touch-icon" sizes="152x152" href="/apple-icon-152x152.png">
link = document.createElement('link');
link.rel = "apple-touch-icon";
link.type = "image/png";
link.sizes = "152x152";
link.href = "/assets/logo_1140x1140.png";
document.getElementsByTagName('head')[0].appendChild(link);


//<link rel="preconnect" href="https://fonts.gstatic.com">

//<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Two+Tone" rel="stylesheet"></link>
link = document.createElement('link');
link.rel = "stylesheet";
link.href = "https://fonts.googleapis.com/icon?family=Material+Icons+Two+Tone&display=swap";
document.getElementsByTagName('head')[0].appendChild(link);

//<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"></link>
link = document.createElement('link');
link.rel = "stylesheet";
link.href = "https://fonts.googleapis.com/icon?family=Material+Icons&display=swap";
document.getElementsByTagName('head')[0].appendChild(link);


//"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
link = document.createElement('link');
link.rel = "javascript";
link.href = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML";
document.getElementsByTagName('head')[0].appendChild(link);

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
