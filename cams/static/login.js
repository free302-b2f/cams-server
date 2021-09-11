/*-----------------------------------------------------
    + v0.1
    + 로그인 뷰의 스크립트
    + 2021-09-09 by DrBAE : amadeus.bae@gmail.com
-----------------------------------------------------*/

async function lmSubmit(e) {
    e.preventDefault();
    let formData = new FormData(e.target);

    try {
        let response = await fetch(e.target.action, { body: formData, method: 'post' });
        console.log("response=" + response);

        let data = await response.json();
        let txt = JSON.stringify(data);
        console.log(txt);

        if (data["result"])
            window.location.href = data["next"];
        else {
            let errorMsg = setDifferValidation(data["cause"]);            
            document.getElementById('lm-login-status').textContent = errorMsg;
        }
    }
    catch (ex) {
        console.log(ex);
    }
    return false;
}

//
// check two input value is the same
//
function _validateSameAs(e1, e2, errorMsg) {
    if (!(e1 && e2)) return;
    e2.setCustomValidity(e1.value != e2.value ? errorMsg : "");
}

//
// check password values
//
function validatePassword(id1, id2) {
    let exp = document.getElementById(id1);
    let act = document.getElementById(id2);
    _validateSameAs(exp, act, "Passwords not matched!");
}

//
// check username
//
function setDifferValidation(id) {

    if(!id) return;
    let el = document.getElementById(id);
    if (!el) return;
    let na = el.value;

    let errorMsg = "'" + na + "'" + "은 사용할 수 없습니다.";
    el.setCustomValidity(errorMsg);
    el.checkValidity();
    el.addEventListener("input", function (ev) {
        ev.target.setCustomValidity(ev.target.value == na ? errorMsg : "");
    });

    return errorMsg;
}


//
//testing...
//
function lmPostData(url, data) {
    // Default options are marked with *
    return fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, cors, *same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'omit', // include, *same-origin, omit
        headers: {
            // 'Content-Type': 'application/json', 
            'Content-Type': 'multipart/form-data',
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: 'follow', // manual, *follow, error
        referrer: 'no-referrer', // no-referrer, *client
        // body: JSON.stringify(data), // body data type must match "Content-Type" header
        body: data, // body data type must match "Content-Type" header
    })
        .then(response => {
            console.log("response=" + response);
            response.json();
        }); // parses JSON response into native JavaScript objects
}