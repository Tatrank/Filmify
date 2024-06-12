// I will keep it here for now just in case of need to use it in the future

function getDynamic(name) {
    document.getElementById(name).addEventListener("input", function (e) {
        let target = document.getElementById("show" + name);
        let value = e.target.value;

        if (value.length < 3) {
            target.innerHTML = "";
            return;
        }

        fetch(`/api/${name}?search=${value}`)
            .then((response) => response.json())
            .then((data) => {
                target.innerHTML = "";
                data.forEach((element) => {
                    let div = document.createElement("div");
                    div.innerHTML = element.name;
                    div.addEventListener("click", function () {
                        document.getElementById(name).value = element.name;
                        target.innerHTML = "";
                    });
                    target.appendChild(div);
                });
            });
    });
}
getDynamic("director");
getDynamic("actor");
getDynamic("category"); t


