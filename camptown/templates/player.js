window.addEventListener("load", () => {

    // Only one disclosure should be open at a time
    disclosures = document.querySelectorAll('input[type="checkbox"]');

    function closeOthers(disclosure) {
        console.log("closeOthers", disclosure);
        if (disclosure.checked) {
            disclosures.forEach((other) => {
                if (disclosure != other) {
                    other.checked = false;
                }
            });
        }
    }
    disclosures.forEach((disclosure) => {
        disclosure.addEventListener("change", () => {
            closeOthers(disclosure);
        });
    });

    document.querySelectorAll('button[data-disclosure]').forEach((button) => {
        button.addEventListener("click", () => {
            var check = document.getElementById(button.dataset.disclosure);
            check.checked = !check.checked;
            closeOthers(check);
        });
    });

    let player = document.querySelector('audio');
    var playlist = [];
    var currentTrack = undefined;

    // preserve the default album art
    var albumArt = document.querySelector('img#coverart');
    albumArt = {
        src: albumArt.src,
        srcset: albumArt.srcset
    };

    function playTrack(idx) {
        console.log("Playing track " + idx);
    }

    tracks = document.querySelectorAll('#tracklist .file');
    tracks.forEach((track) => {
        console.log(track);
        var link = track.querySelector('a');

        var entry = {
            url: link?.href,
            img: track.querySelector('img'),
            title: track.querySelector('.title').textContent,
            button: track.querySelector('button')
        };


        if (link) {
            var idx = playlist.length;
            playlist.push(track);
            track.addEventListener("click", () => {
                playTrack(idx);
            });
            link.addEventListener("click", (e) => {
                e.preventDefault();
                playTrack(idx);
            });
        }
    });
});

