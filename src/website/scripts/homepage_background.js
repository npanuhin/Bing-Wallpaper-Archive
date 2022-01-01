//! Copyright ©; 2019-2022 Nikita Paniukhin

function urlencode(data) {
    let res = [];
    for (let key in data) {
        if (data.hasOwnProperty(key)) {
            res.push(key + '=' + encodeURIComponent(data[key]));
        }
    }
    return res.join('&');
}

function ajax(method, path, data = {}, success = () => {}, error = () => {}, complete = () => {}, headers = {}) {

    let request = false;
    if (window.XMLHttpRequest) {
        request = new XMLHttpRequest();

    } else if (window.ActiveXObject) {
        try {
            request = new ActiveXObject("Microsoft.XMLHTTP");
        } catch (CatchException) {
            request = new ActiveXObject("Msxml2.XMLHTTP");
        }
    }

    if (!request) {
        console.log("Can not create XMLHttpRequest");
        return;
    }

    request.onreadystatechange = function() {
        if (request.readyState == 4) {
            if (request.status == 200) {
                success(request);
            } else {
                error(request);
            }
            complete(request);
        }
    }

    data = urlencode(data);

    if (method.toLowerCase() == "get" && data.length > 0) path += "?" + data;

    request.open(method, path, true);

    for (let header in headers) request.setRequestHeader(header, headers[header]);

    if (method.toLowerCase() == "post") {
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=utf-8");
        request.send(data);
    } else {
        request.send(null);
    }
}


var images = [
    ["US", "2021-08-31.jpg"],
    ["US", "2021-09-09.jpg"],
    ["US", "2021-10-06.jpg"],
    ["US", "2021-10-07.jpg"],
    ["US", "2021-10-17.jpg"],
    ["US", "2021-10-19.jpg"],
    ["US", "2021-10-23.jpg"]
];

// ajax(
//  "GET",
//  "https://bing.npanuhin.me/homepage_images.txt", {},
//  (req) => {
//      let images = req.responseText.trim().split('\n');

//      for (let i = 0; i < images.length; ++i) {
//          images[i] = images[i].trim().split('|').map((elem) => {return elem.trim()});
//      }

        let image = images[Math.floor(Math.random() * images.length)];

        document.body.style.backgroundImage = "url(api/" + image[0] + "/images/" + image[1] + ")";
        
//  }
// );

// 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

// https://raw.githubusercontent.com/npanuhin/bing-wallpaper-archive/api/US/images/2010-01-01.jpg?login=npanuhin&token=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
// btoa
