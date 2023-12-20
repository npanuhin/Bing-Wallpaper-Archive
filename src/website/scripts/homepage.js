const api_path = "api/US/en.json",
    year_api_path = (year) => `api/US/en.${year}.json`,
    image_url_prefix = "https://storage.googleapis.com/npanuhin-bing-wallpaper-archive/US/en/";

const start_date = new Date(2017, 2, 1), // 2017-03-01: 1080p images start here
    end_date = (d => new Date(d.setDate(d.getDate() - 1)))(new Date), // Yesterday
    previous_year = end_date.getFullYear() - 1; // Previous year to avoid having only one image on January 1st

const background = document.getElementById("background"),
    foreground = document.getElementById("foreground"),
    title = document.getElementById("title"),
    transition_delay = 1000,
    delay = 5000;

var cur_image = foreground;

var api;


// =====================================================================================================================

function random(min, max) {
    return Math.random() * (max - min) + min;
}

function randomDate(from, to) {
    return new Date(random(from.getTime(), to.getTime()));
}

function leadingZeros(s, totalDigits) {
    s = s.toString();
    let res = "";
    for (i = 0; i < (totalDigits - s.length); ++i) res += "0";
    return res + s.toString();
}

function date2str(date) {
    return leadingZeros(date.getFullYear(), 4) +
        "-" + leadingZeros(date.getMonth() + 1, 2) +
        "-" + leadingZeros(date.getDate(), 2);
}

// function reflow(element){
//     void(element.offsetHeight);
// }

// function wait_func(func, callback, interval = 20) {
//     (async () => {
//         while (!func()) await new Promise(resolve => setTimeout(resolve, interval));
//         callback();
//     })();
// }

function waitFor(conditionFunction, interval = 20) {
    const poll = resolve => {
        if (conditionFunction()) resolve();
        else setTimeout(_ => poll(resolve), interval);
    }
    return new Promise(poll);
}

function fetchYear(year, callback, alert_error = false) {
    fetch(year_api_path(year), {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            },
            mode: "same-origin"
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error(`Error: can not load API file: ${year_api_path(year)}`);
            }
        })
        .then(data => {
            // let result = {};
            // data.forEach(image => {
            //     result[image["date"]] = image;
            // });
            callback(data);
        })
        .catch(error => {
            console.log(error);
            if (alert_error) alert(`Error: can not load API file for year ${year}`);
        });
}


// =====================================================================================================================

function changeBackground() {
    const chosen_image = api[Math.floor(Math.random() * api.length)];

    const image_path = image_url_prefix + chosen_image["date"] + ".jpg";
    const image_title = chosen_image["title"];

    cur_image.src = image_path;

    setTimeout(() => {
        waitFor(
            () => cur_image.complete,
        ).then(() => {
            foreground.style.opacity = (cur_image === foreground ? 1 : 0);

            cur_image = (cur_image === foreground ? background : foreground);

            setTimeout(changeBackground, transition_delay + 50);  // 50 just to be safe that animation has finished

            if (document.body.classList.contains("shown")) {

                title.style.opacity = 0;

                setTimeout(() => {
                    title.textContent = image_title;
                    title.href = image_path;
                    title.style.opacity = 1;
                }, transition_delay / 2);

            } else {
                title.textContent = image_title;
                title.href = image_path;
                document.body.classList.add("shown");
            }

        });
    }, (document.body.classList.contains("shown") ? delay - transition_delay : 0));
}

fetchYear(previous_year, year_api => {
    console.log("Loaded year:", previous_year);
    api = year_api;

    // changeBackground();
    waitFor(
        () => document.readyState == "complete"
    ).then(changeBackground);

    for (let year = start_date.getFullYear(); year <= end_date.getFullYear(); ++year) {
        if (year === previous_year) continue;
        console.log("Loaded year:", year);

        fetchYear(year, year_api => {
            year_api.forEach(item => {
                if (item["date"] >= date2str(start_date)) api.push(item);
            });
        });
    }
}, alert_error = true);
