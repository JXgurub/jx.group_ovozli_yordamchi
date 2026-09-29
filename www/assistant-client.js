$(document).ready(function () {
    var recognition = null;
    var installPrompt = null;
    var isListening = false;
    var recordingStream = null;
    var recordingTimer = null;
    var audioChunks = [];
    var apiUrlMeta = document.querySelector('meta[name="liza-api-url"]');
    var commandUrl = apiUrlMeta ? apiUrlMeta.content : "/api/liza/command/";
    var csrfUrlMeta = document.querySelector('meta[name="liza-csrf-url"]');
    var csrfUrl = csrfUrlMeta ? csrfUrlMeta.content : "/api/liza/csrf/";

    if (window.SiriWave) {
        new SiriWave({
            container: document.getElementById("siri-container"),
            width: Math.max(280, Math.min(window.innerWidth - 32, 800)),
            height: 160,
            style: "ios9",
            amplitude: 1,
            speed: 0.3,
            autostart: true
        });
    }

    function showAssistant() {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
    }

    function setStatus(message) {
        $(".siri-message").text(message);
    }

    function appendMessage(message, role) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (!chatBox || !message) return;

        var row = document.createElement("div");
        var width = document.createElement("div");
        var bubble = document.createElement("div");
        row.className = "row justify-content-" + (role === "sender" ? "end" : "start") + " mb-3";
        width.className = "width-size";
        bubble.className = role + "_message";
        bubble.textContent = message;
        width.appendChild(bubble);
        row.appendChild(width);
        chatBox.appendChild(row);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function csrfHeaders() {
        var response = await fetch(csrfUrl, { credentials: "same-origin" });
        if (!response.ok) throw new Error("G-med sessiyasi yoki CSRF tokeni mavjud emas.");
        var data = await response.json();
        if (!data.csrfToken) throw new Error("CSRF tokenini olib bo'lmadi.");
        return { "X-CSRFToken": data.csrfToken };
    }

    function showReply(data) {
        if (data.transcript) appendMessage(data.transcript, "sender");
        if (data.reply) {
            appendMessage(data.reply, "receiver");
            setStatus(data.reply);
            if (window.speechSynthesis && window.SpeechSynthesisUtterance) {
                var utterance = new SpeechSynthesisUtterance(data.reply);
                utterance.lang = "uz-UZ";
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            }
        }
    }

    async function sendToDjango(message) {
        var headers = await csrfHeaders();
        headers["Content-Type"] = "application/json";
        var response = await fetch(commandUrl, {
            method: "POST",
            credentials: "same-origin",
            headers: headers,
            body: JSON.stringify({ message: message })
        });
        var data = await response.json().catch(function () { return {}; });
        if (!response.ok) {
            throw new Error(data.error || "Yordamchi serveriga ulanib bo'lmadi.");
        }
        showReply(data);
    }

    async function sendVoiceToDjango(blob, mimeType) {
        var headers = await csrfHeaders();
        var formData = new FormData();
        var extension = mimeType.indexOf("mp4") >= 0 ? "mp4" : mimeType.indexOf("ogg") >= 0 ? "ogg" : "webm";
        formData.append("audio", blob, "liza-audio." + extension);
        var response = await fetch(commandUrl.replace(/command\/?$/, "voice/"), {
            method: "POST",
            credentials: "same-origin",
            headers: headers,
            body: formData
        });
        var data = await response.json().catch(function () { return {}; });
        if (!response.ok) throw new Error(data.error || "Ovoz serverda qayta ishlanmadi.");
        showReply(data);
    }

    async function sendCommand(message) {
        message = String(message || "").trim();
        if (!message) return;

        var desktopBridge = window.eel && typeof window.eel.allCommands === "function";
        if (!desktopBridge) appendMessage(message, "sender");
        showAssistant();
        setStatus("Buyruq bajarilmoqda...");
        $("#SendBtn, #MicBtn").prop("disabled", true);
        try {
            if (desktopBridge) {
                await window.eel.allCommands(message)();
            } else {
                await sendToDjango(message);
            }
        } catch (error) {
            setStatus(error.message || "Ulanishda xatolik yuz berdi.");
        } finally {
            $("#chatbox").val("");
            $("#SendBtn, #MicBtn").prop("disabled", false);
            updateInputButtons("");
        }
    }

    function startListening() {
        if (window.eel && typeof window.eel.allCommands === "function") {
            showAssistant();
            if (window.eel.playAssistantSound) window.eel.playAssistantSound()();
            window.eel.allCommands()();
            return;
        }
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
            setStatus("Bu brauzerda xavfsiz ovoz yozish qo'llanmaydi. Matn kiriting.");
            return;
        }
        if (isListening) {
            if (recognition && recognition.state === "recording") recognition.stop();
            return;
        }

        isListening = true;
        showAssistant();
        setStatus("Tinglayapman. Yozuvni tugatish uchun mikrofonni bosing.");
        $("#MicBtn").attr("aria-pressed", "true");
        navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
            recordingStream = stream;
            audioChunks = [];
            var mimeType = ["audio/webm;codecs=opus", "audio/mp4", "audio/ogg;codecs=opus"]
                .find(function (type) { return MediaRecorder.isTypeSupported(type); });
            recognition = mimeType ? new MediaRecorder(stream, { mimeType: mimeType }) : new MediaRecorder(stream);
            recognition.ondataavailable = function (event) {
                if (event.data && event.data.size) audioChunks.push(event.data);
            };
            recognition.onerror = function () {
                setStatus("Ovozni yozib bo'lmadi. Mikrofonga ruxsatni tekshiring.");
            };
            recognition.onstop = function () {
                window.clearTimeout(recordingTimer);
                recordingTimer = null;
                var recordedType = recognition.mimeType || "audio/webm";
                recordingStream.getTracks().forEach(function (track) { track.stop(); });
                recordingStream = null;
                $("#MicBtn").attr("aria-pressed", "false");
                if (!audioChunks.length) {
                    isListening = false;
                    setStatus("Ovoz yozuvi bo'sh.");
                    return;
                }
                setStatus("Ovoz G-med serverida qayta ishlanmoqda...");
                $("#MicBtn").prop("disabled", true);
                sendVoiceToDjango(new Blob(audioChunks, { type: recordedType }), recordedType)
                    .catch(function (error) { setStatus(error.message); })
                    .finally(function () {
                        isListening = false;
                        $("#MicBtn").prop("disabled", false);
                    });
            };
            recognition.start();
            recordingTimer = window.setTimeout(function () {
                if (recognition && recognition.state === "recording") recognition.stop();
            }, 20000);
        }).catch(function () {
            isListening = false;
            $("#MicBtn").attr("aria-pressed", "false");
            setStatus("Mikrofonga ruxsat berilmadi yoki HTTPS ulanishi yo'q.");
        });
    }

    function updateInputButtons(message) {
        var hasText = String(message || "").trim().length > 0;
        $("#MicBtn").attr("hidden", hasText);
        $("#SendBtn").attr("hidden", !hasText);
    }

    $("#MicBtn").on("click", startListening);
    $("#SendBtn").on("click", function () {
        sendCommand($("#chatbox").val());
    });
    $("#chatbox").on("input", function () {
        updateInputButtons($(this).val());
    }).on("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendCommand($(this).val());
        }
    });

    $("#InstallBtn").on("click", async function () {
        if (!installPrompt) return;
        installPrompt.prompt();
        await installPrompt.userChoice;
        installPrompt = null;
        $(this).attr("hidden", true);
    });

    window.addEventListener("beforeinstallprompt", function (event) {
        event.preventDefault();
        installPrompt = event;
        $("#InstallBtn").attr("hidden", false);
    });

    document.addEventListener("keyup", function (event) {
        if (event.key.toLowerCase() === "j" && (event.metaKey || event.ctrlKey)) {
            startListening();
        }
    });

    if ("serviceWorker" in navigator && window.location.protocol !== "file:") {
        window.addEventListener("load", function () {
            navigator.serviceWorker.register("service-worker.js").catch(function () {});
        });
    }
});
