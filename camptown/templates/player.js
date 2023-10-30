window.addEventListener("load", () => {
    let player = document.querySelector('audio');
    let nowPlaying = document.getElementById("nowplaying");
    let coverArt = document.getElementById("coverart");

    var playlist = [];
    var currentTrack = 0;

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
        button.addEventListener("click", (e) => {
            e.stopPropagation();
            var check = document.getElementById(button.dataset.disclosure);
            check.checked = !check.checked;
            closeOthers(check);
        });
    });


    // preserve the default album art
    var albumArt = document.querySelector('img#coverart');
    albumArt = {
        src: albumArt.src,
        srcset: albumArt.srcset,
    };

    function playTrack(idx) {
        console.log("Playing track " + idx + ": " + playlist[idx].title);
        if (currentTrack != idx || player.paused) {
            playlist[currentTrack].row.classList.remove("now-playing");
            currentTrack = idx;
            player.pause();
            player.src = playlist[idx].url;
        }
        player.play();
    }

    tracks = document.querySelectorAll('#tracklist .file');
    tracks.forEach((track) => {
        var link = track.querySelector('a');

        var entry = {
            row: track,
            url: link?.href,
            img: track.querySelector('img'),
            title: track.querySelector('.title').textContent,
        };


        if (link) {
            var idx = playlist.length;
            playlist.push(entry);
            track.addEventListener("click", () => {
                playTrack(idx);
            });
            link.addEventListener("click", (e) => {
                e.preventDefault();
                playTrack(idx);
            });
        }
    });

    player.src = playlist[0].url;

    player.addEventListener("play", () => {
        let track = playlist[currentTrack];
        let img = track.img || albumArt
        coverArt.src = img.src;
        coverArt.srcset = img.srcset;
        console.log(coverArt);
        nowPlaying.textContent = "Now playing: ";
        var title = document.createElement("span");
        title.textContent = track.title;
        nowPlaying.appendChild(title);
        track.row.classList.add("now-playing");
    });

    player.addEventListener("ended", () => {
        playlist[currentTrack].row.classList.remove("now-playing");
        if (currentTrack + 1 < playlist.length) {
            ++currentTrack;
            let track = playlist[currentTrack];
            player.src = track.url;
            player.play();
            track.row.scrollIntoView({
                behafior: 'smooth',
                block: 'nearest',
            });
        }
    });

    // document.getElementById("previous").addEventListener("click", prevTrack);
    // document.getElementById("next").addEventListener("click", nextTrack);
});

