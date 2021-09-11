/*-----------------------------------------------------
    + v0.1
    + 로그인 뷰의 스크립트
    + 2021-09-09 by DrBAE : amadeus.bae@gmail.com
-----------------------------------------------------*/

let _id_un = "lm-login-username"
let _id_pw = "lm-login-password"
let _id_pwc = "lm-login-password-confirm"
let _id_em = "lm-login-email"
let _id_res = "lm-login-status"


//
// login, signup 페이지에서 폼 제출
// HTML5 fetch로 처리 - 서버는 json으로 응답
// 서버 응답 결과에 따라 폼 검증함수를 이벤트에 등록
// Constraint Validation API 사용
//
async function lmSubmit(e) {
    e.preventDefault();
    let formData = new FormData(e.target);

    try {
        let response = await fetch(e.target.action, { body: formData, method: 'post' });
        console.log("response=" + response);

        let data = await response.json();
        let txt = JSON.stringify(data);
        console.log(txt);

        if (data["isOK"])
            window.location.href = data["next"];
        else {
            let errorMsg = applyServerValidation(data["cause"]);
            document.getElementById(_id_res).textContent = errorMsg;
        }
    }
    catch (ex) {
        console.log(ex);
    }
    return false;
}

//
// 두 요소의 value 속성이 같은지 검증
//
function _validateSameAs(e1, e2, errorMsg) {
    if (!(e1 && e2)) return;
    e2.setCustomValidity(e1.value != e2.value ? errorMsg : "");
}

//
// 두 패스워드 입력값이 같은지 검증
//
function validatePassword(id1, id2) {
    let exp = document.getElementById(id1);
    let act = document.getElementById(id2);
    _validateSameAs(exp, act, "입력한 패스워드가 서로 일치하지 않습니다.");
}

//
// 서버의 검증 결과에 따라 폼을 검증하는 이벤트 핸들러 등록
// 잘못된 아이디나 패스워드로 재시도 할 경우 검증 실패
//
function applyServerValidation(id) {

    if (!id) return;
    let el = document.getElementById(id);
    if (!el) return;
    let na = el.value;

    if (id != _id_pw && id != _id_pwc) {
        let errorMsg = `${id == _id_un ? "로그인 아이디" : "이메일 주소"} '${na}'가 유효하지 않습니다.`;
        el.setCustomValidity(errorMsg);
        el.addEventListener("input", function (ev) {
            el.setCustomValidity(ev.value == na ? errorMsg : "");
        });
        return errorMsg;
    }

    // pw
    errorMsg = "패스워드가 유효하지 않습니다.";
    el.setCustomValidity(errorMsg);
    el.addEventListener("input", function (ev) {
        el.setCustomValidity(ev.target.value == na ? errorMsg : "");
    });

    let elName = document.getElementById(_id_un);
    let name = elName.value;
    elName.addEventListener("input", function (ev) {
        if (ev.target.value != name) el.setCustomValidity("");
        else el.setCustomValidity(errorMsg);
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