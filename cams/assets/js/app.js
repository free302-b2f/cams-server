
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
// _element = document.createElement('link');
// _element.rel = "stylesheet";
// _element.href = "https://fonts.googleapis.com/icon?family=Material+Icons&display=swap";
// document.getElementsByTagName('head')[0].appendChild(_element);

//<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet"></link>
_element = document.createElement('link');
_element.rel = "stylesheet";
_element.href = "https://fonts.googleapis.com/icon?family=Material+Icons+Outlined&display=swap";
document.getElementsByTagName('head')[0].appendChild(_element);


//"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
_element = document.createElement('script');
_element.src = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML";
document.getElementsByTagName('head')[0].appendChild(_element);


//
// Date 포맷 함수 : 로컬시간을 ISO 포맷의 문자열로 반환
//
function toLocalISOString(d) {
    var z = n => ('0' + n).slice(-2);
    var zz = n => ('00' + n).slice(-3);
    var off = d.getTimezoneOffset();
    var sign = off < 0 ? '+' : '-';
    off = Math.abs(off);

    return d.getFullYear() + '-'
        + z(d.getMonth() + 1) + '-' +
        z(d.getDate()) + 'T' +
        z(d.getHours()) + ':' +
        z(d.getMinutes()) + ':' +
        z(d.getSeconds()) + '.' +
        zz(d.getMilliseconds()) +
        sign + z(off / 60 | 0) + ':' + z(off % 60);
}

//
// cams jpeg bytes decoder
//
async function decodeJpeg(data, imgIndex){
    header = await data.slice(-4).arrayBuffer();
    var decoder = new TextDecoder();
    var metaLen = parseInt(decoder.decode(header), 10);
    console.log(`metaLen=${metaLen}`);

    meta = await data.slice(-metaLen).arrayBuffer();
    const ts = decoder.decode(meta.slice(0, 32));
    const dt = new Date(ts);
    console.log(`ts=${ts}, dt=${dt}`);
    
    const sn = decoder.decode(meta.slice(32, - 4));
    console.log(`sn=${sn}`);

    // const imgInfo = document.querySelector(`#apps-camera-info-${imgIndex}`);
    // imgInfo.textContent = sn + " @ " + toLocalISOString(dt); //dt.toString();

    const jpg = data.slice(0, data.size, "image/jpeg");
    // const elImg = document.querySelector(`#apps-camera-img-${imgIndex}`);
    // elImg.src = URL.createObjectURL(jpg);

    return (dt, sn, jpg);
}

//
// websocket
//
function wsImg(wsUri, imgIndex) {

    console.log(`wsImg(): wsUri=${wsUri}, imgIndex=${imgIndex}`);
    const ws = new WebSocket(wsUri);

    ws.onopen = function (event) {
        console.log(`img${imgIndex}: ws connected: ${wsUri}`);
    };

    ws.onmessage = function (event) {

        if (event === undefined) return;

        event.data.slice(-4).arrayBuffer().then(header => {
            var decoder = new TextDecoder();
            var metaLen = parseInt(decoder.decode(header), 10);
            //console.log("metaLen= " + metaLen);

            event.data.slice(-metaLen).arrayBuffer().then(meta => {
                const ts = decoder.decode(meta.slice(0, 32));
                const dt = new Date(ts);
                //console.log("ts=" + ts + "  dt=" + dt);

                const sn = decoder.decode(meta.slice(32, - 4));
                //console.log(sn);

                const imgInfo = document.querySelector(`#apps-camera-info-${imgIndex}`);
                imgInfo.textContent = sn + " @ " + toLocalISOString(dt); //dt.toString();

                const jpg = event.data.slice(0, event.data.size, "image/jpeg");
                const elImg = document.querySelector(`#apps-camera-img-${imgIndex}`);
                elImg.src = URL.createObjectURL(jpg);
            });
        });
    }
}

function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

// //
// // window onload: start ws
// //
// window.addEventListener("load", async (e) => {
    
//     let camera_view = document.getElementById("apps-camera-container");
//     while (camera_view == undefined || camera_view == null) {
//         await sleep(100);
//         camera_view = document.getElementById("apps-camera-container");
//     }

//     if (camera_view !== undefined) {
//         console.log(`camera view found: ${camera_view}`);
//         for (var i = 0; i < 5; i++) {

//             const imgId = `#apps-camera-img-${i}`;
//             console.log(`finding img <${imgId}>`);

//             const img = document.querySelector(imgId);
//             if (img == undefined) continue;

//             console.log(`found: uri=${img.dataset.ws_uri}, id=${img.id}`);
//             //wsImg(img.dataset.ws_uri, i);//start ws
            
//             //
//             img.addEventListener("load", function(){
//                 const a = img.textContent;
//             });

//         }
//     }
// });


// //
// // window onload: add img load handler
// //
// window.addEventListener("load", async (e) => {
    
//     let camera_view = document.getElementById("apps-camera-container");
//     while (camera_view == undefined || camera_view == null) {
//         await sleep(100);
//         camera_view = document.getElementById("apps-camera-container");
//     }

//     if (camera_view === undefined || camera_view == null) 
//     {
//         console.log("fail to find #apps-camera-container");
//         return;
//     }

//     console.log(`found #apps-camera-container: ${camera_view}`);

//     const imgs = document.querySelectorAll(".apps-camera-img");
//     imgs.forEach(img => {
//         console.log(`found img: id=<${img.id}>, uri=${img.dataset.ws_uri}`);

//         //
//         img.addEventListener("load", async function(){
//             const a = await img.decode();
//         });

//     });     
// });


