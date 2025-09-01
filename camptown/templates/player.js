/*
 * Camptown player logic script
 * Doo-dah
 * Doo-dah
 *
 * https://github.com/fluffy-critter/camptown
 */

window.addEventListener('load', () => {
    let player = document.querySelector('audio');
    let nowPlaying = document.getElementById('nowplaying');

    var playlist = [];
    var currentTrack = 0;

    // Only one disclosure should be open at a time
    disclosures = document.querySelectorAll('input[type="checkbox"]');

    function closeOthers(disclosure) {
        console.log('closeOthers', disclosure);
        if (disclosure.checked) {
            disclosures.forEach((other) => {
                if (disclosure != other) {
                    other.checked = false;
                }
            });
        }
    }
    disclosures.forEach((disclosure) => {
        disclosure.addEventListener('change', () => {
            closeOthers(disclosure);
        });
    });

    document.querySelectorAll('button[data-disclosure]').forEach((button) => {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            var check = document.getElementById(button.dataset.disclosure);
            check.checked = !check.checked;
            closeOthers(check);
        });
    });

    let fullSizeArt = document.getElementById('fullsizeart')

    document.getElementById('openfullsize').addEventListener('click', (e) => {
        e.stopPropagation();

        console.log(fullSizeArt);
        if (fullSizeArt.open) {
            fullSizeArt.close();
        } else {
            fullSizeArt.showModal();
        }
    });

    var dlg = document.querySelector('dialog#fullsizeart');
    dlg.addEventListener('click', (e) => {
        e.stopPropagation();

        fullSizeArt.close();
    });
    dlg.addEventListener('cancel', (e) => {
        console.log("Dialog was canceled");
    });

    // preserve the default album art
    var albumArt = document.querySelector('img#coverart');
    albumArt = {
        src: albumArt.src,
        srcset: albumArt.srcset,
        dataset: albumArt.dataset
    };

    // set the album art from what's now playing
    function setCoverArt(ref) {
        let thumb = document.querySelector('img#coverart');
        let fullsize = ref.dataset.fullsize ?? albumArt.dataset.fullsize ?? '';

        console.log("setting artwork", ref, fullsize);

        thumb.src = ref.src;
        thumb.srcset = ref.srcset;

        document.querySelector('#fullsizeart img').src = fullsize;
        document.querySelector('#fullcover img').src = fullsize;
    }

    function playTrack(idx) {
        console.log('Playing track ' + idx + ': ' + playlist[idx].title);
        if (currentTrack != idx || player.paused) {
            playlist[currentTrack].row.classList.remove('now-playing');
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
            track.addEventListener('click', () => {
                playTrack(idx);
            });
            link.addEventListener('click', (e) => {
                e.preventDefault();
                playTrack(idx);
            });
        }
    });

    player.src = playlist[0].url;

    player.addEventListener('play', () => {
        let track = playlist[currentTrack];
        let img = track.img || albumArt;
        setCoverArt(img);
        console.log(img);
        nowPlaying.textContent = 'Now playing: ';
        var title = document.createElement('span');
        title.textContent = track.title;
        nowPlaying.appendChild(title);
        track.row.classList.add('now-playing');
    });

    player.addEventListener('ended', () => {
        playlist[currentTrack].row.classList.remove('now-playing');
        if (currentTrack + 1 < playlist.length) {
            console.log(`finished ${currentTrack + 1}/${playlist.length}`);
            ++currentTrack;
            let track = playlist[currentTrack];
            player.src = track.url;
            player.play();
            track.row.scrollIntoView({
                behafior: 'smooth',
                block: 'nearest',
            });
        } else {
            console.log('Playback ended');
            nowPlaying.textContent = '';
        }
    });

    function prevTrack() {
        playlist[currentTrack].row.classList.remove('now-playing');
        if (player.paused || player.currentTime < 2) {
            // We're paused or near the start of a track, so go to the previous track
            var paused = player.paused;
            player.pause();
            if (currentTrack > 0) {
                --currentTrack;
                player.src = playlist[currentTrack].url;
            }
            player.currentTime = 0;
            if (!paused) {
                player.play();
            }
        } else {
            // We're within the track, so go to the start of the track
            player.currentTime = 0;
        }
        playlist[currentTrack].row.classList.add('now-playing');
    }

    function nextTrack() {
        playlist[currentTrack].row.classList.remove('now-playing');
        if (currentTrack + 1 < playlist.length) {
            var paused = player.paused;
            player.pause();
            ++currentTrack;
            player.src = playlist[currentTrack].url;
            player.currentTime = 0;
            if (!paused) {
                player.play();
            }
        }
        playlist[currentTrack].row.classList.add('now-playing');
    }

    document.getElementById('previous').addEventListener('click', prevTrack);
    document.getElementById('next').addEventListener('click', nextTrack);

    window.addEventListener('keydown', (e) => {
        e = e || window.event;
        console.log(e);
        if (!e.altKey && !e.metaKey && !e.ctrlKey) {
            switch (e.key) {
                case ' ':
                    e.preventDefault();
                    if (player.paused) {
                        player.play();
                    } else {
                        player.pause();
                    }
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    prevTrack();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    nextTrack();
                    break;
            }
        }
    });
});
