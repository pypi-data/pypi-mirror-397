import { eventBus, MusicEvent } from "./event.js";
import { trackDisplayHtml } from "./track.js";
import { queue } from "./queue.js";
import { clamp, durationToString, vars, TRANSITION_DURATION, createToast, gettext } from "../util.js";
import { windows } from "./window.js";
import { editor } from "./editor.js";
import { getImageQuality, setSettingValue, Setting } from "./settings.js";
import { getDuration, getPosition, isPaused, pause, play, seek, seekRelative } from "./audio.js";

const SEEK_BAR = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar'));
const POSITION_TEXT = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar-text-position'));
const DURATION_TEXT = /** @type {HTMLDivElement} */ (document.getElementById('seek-bar-text-duration'));

/**
 * @returns {number} volume 0.0-1.0
 */
export function getVolume() {
    return parseInt(Setting.VOLUME.value) / 100.0;
}

/**
 * @param {number} volume volume 0.0-1.0
 */
export function setVolume(volume) {
    setSettingValue(Setting.VOLUME, clamp(Math.round(volume * 100), 0, 100) + '');
}

// Seek bar
{
    /**
     * @param {MouseEvent} event
     */
    function seekBarSeek(event) {
        const duration = getDuration();
        if (!duration) return;

        const seekbarBounds = SEEK_BAR.getBoundingClientRect();
        const relativePosition = (event.clientX - seekbarBounds.left) / seekbarBounds.width;
        if (relativePosition < 0 || relativePosition > 1) {
            // user has moved outside of seekbar, stop seeking
            document.removeEventListener('mousemove', onMove);
            return;
        }

        const newTime = relativePosition * duration;
        seek(newTime);
    }

    const onMove = (/** @type {MouseEvent} */ event) => {
        seekBarSeek(event);
        event.preventDefault(); // Prevent accidental text selection
    };

    const onUp = () => {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
    };

    SEEK_BAR.addEventListener('mousedown', event => {
        seekBarSeek(event);

        // Keep updating while mouse is moving
        document.addEventListener('mousemove', onMove);

        // Unregister events on mouseup event
        document.addEventListener('mouseup', onUp);

        event.preventDefault(); // Prevent accidental text selection
    });

    // Scroll to seek
    SEEK_BAR.addEventListener('wheel', event => {
        seekRelative(event.deltaY < 0 ? 3 : -3);
    }, { passive: true });


    function updateSeekBar() {
        // Save resources updating seek bar if it's not visible
        if (document.visibilityState != 'visible') {
            return;
        }

        const position = getPosition();
        const duration = getDuration();
        let barCurrent;
        let barDuration;
        let barWidth;

        if (position != null && duration != null) {
            barCurrent = durationToString(Math.round(position));
            barDuration = durationToString(Math.round(duration));
            barWidth = ((position / duration) * 100);
        } else {
            barCurrent = gettext("loading...");
            barDuration = '';
            barWidth = 0;
        }

        requestAnimationFrame(() => {
            POSITION_TEXT.textContent = barCurrent;
            DURATION_TEXT.textContent = barDuration;
            // Previously, the seek bar used an inner div with changing width. However, that causes an expensive
            // layout update. Instead, set a background gradient which is nearly free to update.
            SEEK_BAR.style.background = `linear-gradient(90deg, var(--seek-bar-color) ${barWidth}%, var(--background-color) 0%)`;
        });
    }
    eventBus.subscribe(MusicEvent.PLAYER_POSITION, () => updateSeekBar());
    eventBus.subscribe(MusicEvent.PLAYER_DURATION, () => updateSeekBar());

    // Seek bar is not updated when page is not visible. Immediately update it when the page does become visible.
    document.addEventListener('visibilitychange', () => updateSeekBar());
}

// Home button
{
    const homeButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-home'));
    homeButton.addEventListener('click', () => window.open('/', '_blank'));
}

// Skip buttons
{
    const prevButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-prev'));
    const nextButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-next'));
    prevButton.addEventListener('click', () => queue.previous());
    nextButton.addEventListener('click', () => queue.next());
}

// Play pause buttons
{
    const pauseButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-pause'));
    const playButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-play'));

    // Play pause click actions
    pauseButton.addEventListener('click', () => pause());
    playButton.addEventListener('click', () => play());

    const updateButtons = () => {
        requestAnimationFrame(() => {
            pauseButton.hidden = isPaused();
            playButton.hidden = !isPaused();
        })
    };

    eventBus.subscribe(MusicEvent.PLAYER_PLAY, updateButtons);
    eventBus.subscribe(MusicEvent.PLAYER_PAUSE, updateButtons);

    // Hide pause button on initial page load, otherwise both play and pause will show
    pauseButton.hidden = true;
}

// Handle presence of buttons that perform file actions: dislike, copy, share, edit, delete
if (!vars.offlineMode) {
    const dislikeButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-dislike'));
    const copyButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-copy'));
    const shareButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-share'));
    const problemButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-problem'));
    const editButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-edit'));
    const deleteButton = /** @type {HTMLButtonElement} */ (document.getElementById('button-delete'));

    const requiresRealTrack = [dislikeButton, copyButton, shareButton, problemButton];
    const requiresWriteAccess = [editButton, deleteButton];

    async function updateButtons() {
        requestAnimationFrame(() => {
            for (const button of requiresRealTrack) {
                button.hidden = !queue.currentTrack || queue.currentTrack.isVirtual();
            }

            const hasWriteAccess = queue.currentTrack && queue.currentTrack.isWritable();
            for (const button of requiresWriteAccess) {
                button.hidden = !hasWriteAccess;
            }
        });
    }

    eventBus.subscribe(MusicEvent.TRACK_CHANGE, updateButtons);

    // Hide all buttons initially
    for (const button of [...requiresRealTrack, ...requiresWriteAccess]) {
        button.hidden = true;
    }

    // Dislike button
    dislikeButton.addEventListener('click', async () => {
        if (queue.currentTrack && !queue.currentTrack.isVirtual()) {
            await queue.currentTrack.dislike();
            queue.next();
        } else {
            throw new Error();
        }
    });

    // Copy button
    const copyTrack = /** @type {HTMLButtonElement} */ (document.getElementById('copy-track'));
    const copyPlaylist = /** @type {HTMLSelectElement} */ (document.getElementById('copy-playlist'));
    const copyDoButton = /** @type {HTMLButtonElement} */ (document.getElementById('copy-do-button'));
    copyButton.addEventListener('click', () => {
        if (!queue.currentTrack || queue.currentTrack.isVirtual()) {
            throw new Error();
        }
        copyTrack.value = queue.currentTrack.path;
        windows.open('window-copy');
    });
    copyDoButton.addEventListener('click', async () => {
        if (!queue.currentTrack) throw new Error();
        if (copyPlaylist.value == '') return;
        copyDoButton.disabled = true;
        try {
            await queue.currentTrack.copyTo(copyPlaylist.value);
        } catch (err) {
            console.error(err);
            alert('Error: ' + err);
        }
        windows.closeTop();
        copyDoButton.disabled = false;
    });

    // Share button is handled by share.js

    // Problem button
    problemButton.addEventListener('click', async () => {
        if (queue.currentTrack) {
            await queue.currentTrack.reportProblem();
            createToast('alert-circle', gettext("Problem reported"));
        }
    })

    // Edit button
    editButton.addEventListener('click', () => {
        if (queue.currentTrack) {
            editor.open(queue.currentTrack);
        }
    });

    // Delete button
    const deleteSpinner = /** @type {HTMLDivElement} */ (document.getElementById('delete-spinner'));
    deleteButton.addEventListener('click', async () => {
        if (!queue.currentTrack) {
            return;
        }
        deleteSpinner.hidden = false;
        await queue.currentTrack.delete();
        queue.next();
        deleteSpinner.hidden = true;
    });
}

// Volume slider
{
    function updateVolumeIcon() {
        const volume = parseInt(Setting.VOLUME.value);
        requestAnimationFrame(() => {
            Setting.VOLUME.classList.remove('input-volume-high', 'input-volume-medium', 'input-volume-low');
            if (volume > 60) {
                Setting.VOLUME.classList.add('input-volume-high');
            } else if (volume > 30) {
                Setting.VOLUME.classList.add('input-volume-medium');
            } else {
                Setting.VOLUME.classList.add('input-volume-low');
            }
        });
    }

    // Unfocus after use so arrow hotkeys still work for switching tracks
    Setting.VOLUME.addEventListener('mouseup', () => Setting.VOLUME.blur());

    // Respond to volume button changes
    // Event fired when input value changes, also manually when code changes the value
    Setting.VOLUME.addEventListener('change', () => updateVolumeIcon());
    // Also respond to input event, so volume changes immediately while user is dragging slider
    Setting.VOLUME.addEventListener('input', () => Setting.VOLUME.dispatchEvent(new Event('change')));
    // Set icon on page load
    updateVolumeIcon();

    // Scroll to change volume
    Setting.VOLUME.addEventListener('wheel', event => {
        setVolume(getVolume() + (event.deltaY < 0 ? 0.05 : -0.05));
    }, { passive: true });
}

// Album images
{
    function replaceAlbumImages() {
        if (!queue.currentTrack) return;
        const track = queue.currentTrack;
        const imageUrl = track.getCoverURL(getImageQuality(), Setting.MEME_MODE.checked);
        const cssUrl = `url("${imageUrl}")`;

        const bgBottom = /** @type {HTMLDivElement} */ (document.getElementById('bg-image-1'));
        const bgTop = /** @type {HTMLDivElement} */ (document.getElementById('bg-image-2'));
        const fgBottom = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-1'));
        const fgTop = /** @type {HTMLDivElement} */ (document.getElementById('album-cover-2'));

        if (Setting.LITE_MODE.checked) {
            bgTop.style.backgroundImage = cssUrl;
            fgTop.style.backgroundImage = cssUrl;
            return;
        }

        // Set bottom to new image
        bgBottom.style.backgroundImage = cssUrl;
        fgBottom.style.backgroundImage = cssUrl;

        // Slowly fade out old top image
        bgTop.style.opacity = '0';
        fgTop.style.opacity = '0';

        setTimeout(() => {
            // To prepare for next replacement, move bottom image to top image
            bgTop.style.backgroundImage = cssUrl;
            fgTop.style.backgroundImage = cssUrl;
            // Make it visible
            bgTop.style.opacity = '1';
            fgTop.style.opacity = '1';
        }, TRANSITION_DURATION);
    }

    // Update album cover when track is changed
    eventBus.subscribe(MusicEvent.TRACK_CHANGE, replaceAlbumImages);
    // Update album cover when meme mode is enabled or disabled
    Setting.MEME_MODE.addEventListener('change', replaceAlbumImages);
    // Update album cover when quality is changed
    Setting.AUDIO_TYPE.addEventListener('change', replaceAlbumImages);
}

// Current track info
{
    eventBus.subscribe(MusicEvent.TRACK_CHANGE, () => {
        if (!queue.currentTrack) throw new Error();
        const track = queue.currentTrack;
        const currentTrackElem = /** @type {HTMLSpanElement} */ (document.getElementById('current-track'));
        currentTrackElem.replaceChildren(trackDisplayHtml(track, true));
        document.title = track.displayText();
    });
}
