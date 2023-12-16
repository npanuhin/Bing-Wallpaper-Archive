function random(min, max) {
    return Math.random() * (max - min) + min;
}

function getRandomDate(from, to) {
    return new Date(random(from.getTime(), to.getTime()));
}

function leadingZeros(s, totalDigits) {
    s = s.toString();
    let res = '';
    for (i = 0; i < (totalDigits - s.length); ++i) res += '0';
    return res + s.toString();
}

// function reflow(element){
//     void(element.offsetHeight);
// }

function waitFunc(func, callback, interval=20) {
    (async() => {
        while (!func()) await new Promise(resolve => setTimeout(resolve, interval));
        callback();
    })();
}



// =====================================================================================================================

const api_filepath = "api/us.json",
      image_url_prefix = "https://storage.googleapis.com/npanuhin-bing-wallpaper-archive/US/images/";

const start_date = new Date(2017, 5, 10), // 2017-05-10: high resolution images start around here
      end_date = (d => new Date(d.setDate(d.getDate() - 1)))(new Date); // Yesterday

var background = document.getElementById("background"),
    foreground = document.getElementById("foreground"),
    description = document.getElementById("description"),
    cur_image = foreground,
    transition_delay = 1000,
    delay = 5000;

var api;


function changeBackground() {
    var image_name, image_short_name = "", image_path;

    while (!(image_short_name in api)) {

        let image_date = getRandomDate(start_date, end_date);

        let year = leadingZeros(image_date.getUTCFullYear(), 4),
            month = leadingZeros(image_date.getUTCMonth() + 1, 2),
            day = leadingZeros(image_date.getUTCDate(), 2);

        image_name = year + '-' + month + '-' + day;
        image_short_name = year + month + day;
        image_path = image_url_prefix + image_name + ".jpg";
    }

    var image_loaded = false;
    cur_image.onload = () => {image_loaded = true;}

    setTimeout(waitFunc, (description.classList.contains("firstrun") ? 0 : delay - transition_delay - 500),
        () => {
            return image_loaded;
        },
        () => {
            foreground.style.opacity = (cur_image === foreground ? 1 : 0);

            cur_image = (cur_image === foreground ? background : foreground);

            setTimeout(() => {
                setTimeout(changeBackground);
            }, (description.classList.contains("firstrun") ? 0 : transition_delay) + 500);

            if (description.classList.contains("firstrun")) {
                description.classList.remove("firstrun");

                description.textContent = api[image_short_name];
                description.href = image_path;

                document.body.classList.add("shown");

            } else {
                description.style.opacity = 0;

                setTimeout(() => {
                    description.textContent = api[image_short_name];
                    description.href = image_path;
                    description.style.opacity = 1;
                }, transition_delay / 2);
            }
        }
    );

    cur_image.src = image_path;
}

var page_loaded = false;
window.onload = () => {page_loaded = true;}

ajax(
    "GET",
    api_filepath,
    {},
    success = (req) => {
        api = JSON.parse(req.responseText);
        // changeBackground();
        waitFunc(
            () => {
                return page_loaded;
            },
            changeBackground
        );
    },
    error = () => {
        alert(`Error: can not load API file (${api_filepath})`);
    }
);
